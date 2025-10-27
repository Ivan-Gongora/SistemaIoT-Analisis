import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# =============================================================================
# PRIMERO: Definir ConfigEnergetico ANTES de que se use
# =============================================================================

class ConfigEnergetico:
    # Ruta BASE - apunta al directorio app/
    BASE_DIR = Path(__file__).parent
    
    # Ruta del CSV - está en app/data/recibos/
    RUTA_RECIBOS = BASE_DIR / "data" / "recibos" / "recibos_gdmth.csv"
    
    # Rutas para modelos ML
    RUTA_MODELOS = BASE_DIR / "modelos_ml"
    
    # Parámetros del modelo predictivo
    HORIZONTE_PREDICCION = 12
    MESES_ENTRENAMIENTO = 24
    MESES_ESTACIONALIDAD = 12
    
    # URLs de APIs de IA
    IA_API_URLS = {
        "openrouter": "https://openrouter.ai/api/v1",
        "deepseek": "https://api.deepseek.com/v1"
    }
    
    # Modelos gratuitos disponibles
    MODELOS_GRATUITOS = {
        "openrouter": [
            {"id": "deepseek", "nombre": "DeepSeek Chat", "modelo": "deepseek/deepseek-chat:free"},
            {"id": "gemini", "nombre": "Google Gemini Flash", "modelo": "google/gemini-flash-1.5:free"},
            {"id": "llama", "nombre": "Meta Llama 3.1", "modelo": "meta-llama/llama-3.1-8b-instruct:free"},
            {"id": "mistral", "nombre": "Mistral 7B", "modelo": "mistralai/mistral-7b-instruct:free"}
        ],
        "deepseek": [
            {"id": "deepseek-chat", "nombre": "DeepSeek Chat", "modelo": "deepseek-chat"}
        ]
    }
    
    # Estos se establecerán después de crear configuracion
    IA_PROVIDER = None
    IA_API_KEY = None
    IA_MODELO_DEFAULT = None
    IA_MAX_TOKENS = None
    IA_TIMEOUT = None
    
    @classmethod
    def obtener_url_api(cls):
        """Obtener URL de API según el proveedor configurado"""
        return cls.IA_API_URLS.get(cls.IA_PROVIDER, cls.IA_API_URLS["openrouter"])
    
    @classmethod
    def obtener_modelos_disponibles(cls):
        """Obtener modelos disponibles según el proveedor"""
        return cls.MODELOS_GRATUITOS.get(cls.IA_PROVIDER, cls.MODELOS_GRATUITOS["openrouter"])
    
    @classmethod
    def inicializar_desde_configuracion(cls, config):
        """Inicializar valores desde ConfiguracionSimulacion"""
        cls.IA_PROVIDER = config.IA_PROVIDER
        cls.IA_API_KEY = config.OPENROUTER_API_KEY
        cls.IA_MODELO_DEFAULT = config.IA_MODELO_DEFAULT
        cls.IA_MAX_TOKENS = config.IA_MAX_TOKENS
        cls.IA_TIMEOUT = config.IA_TIMEOUT
        
        # Crear directorios si no existen
        cls.RUTA_MODELOS.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def validar_configuracion_ia(cls):
        """Validar configuración de IA"""
        print("🔍 Validando configuración IA...")
        
        if not cls.IA_API_KEY:
            print("❌ API Key de IA no configurada")
            return False
        
        print(f"✅ Proveedor IA: {cls.IA_PROVIDER}")
        print(f"✅ Modelo por defecto: {cls.IA_MODELO_DEFAULT}")
        print(f"✅ URL API: {cls.obtener_url_api()}")
        
        modelos = cls.obtener_modelos_disponibles()
        print(f"✅ Modelos disponibles: {len(modelos)}")
        
        return True

# =============================================================================
# SEGUNDO: Definir ConfiguracionSimulacion
# =============================================================================

class ConfiguracionSimulacion:
    def __init__(self):
        # --- Variables OBLIGATORIAS (sin estas, el sistema no funciona) ---
        self.db_host = self._get_required("DB_HOST")
        self.db_user = self._get_required("DB_USER")
        self.db_password = self._get_required("DB_PASSWORD")
        self.db_name = self._get_required("DB_NAME")
        self.JWT_SECRET_KEY = self._get_required("JWT_SECRET_KEY")
        self.EMAIL_REMITENTE = self._get_required("EMAIL_REMITENTE_CORREO")
        self.EMAIL_PASSWORD = self._get_required("EMAIL_PASSWORD")
        self.OPENROUTER_API_KEY = self._get_required("OPENROUTER_API_KEY")
        
        # --- Variables OPCIONALES (con valores por defecto) ---
        self.db_port = int(os.getenv("DB_PORT", "3306"))
        self.JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
        self.ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
        self.EMAIL_SMTP_SERVER = os.getenv("EMAIL_SMTP_SERVER", "smtp.gmail.com")
        self.EMAIL_SMTP_PORT = int(os.getenv("EMAIL_SMTP_PORT", "587"))
        self.EMAIL_DESTINATARIO_ALERTA = os.getenv("EMAIL_DESTINATARIO_ALERTA", "ivangongora1092@gmail.com")
        self.campo_temperatura_id = int(os.getenv("CAMPO_TEMPERATURA_ID", "2"))
        self.campo_humedad_id = int(os.getenv("CAMPO_HUMEDAD_ID", "3"))
        
        # --- Configuración IA ---
        self.IA_PROVIDER = os.getenv("IA_PROVIDER", "openrouter")
        self.IA_MODELO_DEFAULT = os.getenv("IA_MODELO_DEFAULT", "deepseek/deepseek-chat:free")
        self.IA_MAX_TOKENS = int(os.getenv("IA_MAX_TOKENS", "2000"))
        self.IA_TIMEOUT = int(os.getenv("IA_TIMEOUT", "25"))
    
    def _get_required(self, env_var: str) -> str:
        """Obtener variable de entorno REQUERIDA o lanzar error"""
        value = os.getenv(env_var)
        if not value:
            raise ValueError(f"❌ Variable de entorno REQUERIDA no configurada: {env_var}")
        return value
    
    def mostrar_configuracion(self):
        """Mostrar configuración (sin mostrar valores sensibles)"""
        print("🔐 Configuración Cargada:")
        print(f"   📊 BD: {self.db_user}@{self.db_host}:{self.db_port}/{self.db_name}")
        print(f"   📧 Email: {self.EMAIL_REMITENTE}")
        print(f"   🤖 IA: {self.IA_PROVIDER.upper()} ({self.IA_MODELO_DEFAULT})")
        print(f"   🔑 API Key: {'✅ Configurada' if self.OPENROUTER_API_KEY else '❌ No'}")
        print(f"   🎯 JWT: {self.JWT_ALGORITHM} (expira: {self.ACCESS_TOKEN_EXPIRE_MINUTES}min)")

# =============================================================================
# TERCERO: Crear instancias y inicializar
# =============================================================================

# Instancia global de ConfiguracionSimulacion
try:
    configuracion = ConfiguracionSimulacion()
    configuracion.mostrar_configuracion()
    print("🎉 Configuración cargada exitosamente!")
except ValueError as e:
    print(f"🚨 Error de configuración: {e}")
    print("💡 Asegúrate de que tu archivo .env tenga todas las variables requeridas")
    # import sys
    # sys.exit(1)

# Instancia global de ConfigEnergetico (INICIALIZADA después de configuracion)
config_energetico = ConfigEnergetico()
ConfigEnergetico.inicializar_desde_configuracion(configuracion)

# Validar configuración IA
config_energetico.validar_configuracion_ia()