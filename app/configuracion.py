import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

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
        self.DEEPSEEK_API_KEY = self._get_required("DEEPSEEK_API_KEY")
        
        # --- Variables OPCIONALES (con valores por defecto) ---
        self.db_port = int(os.getenv("DB_PORT", "3306"))
        self.JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
        self.ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
        self.EMAIL_SMTP_SERVER = os.getenv("EMAIL_SMTP_SERVER", "smtp.gmail.com")
        self.EMAIL_SMTP_PORT = int(os.getenv("EMAIL_SMTP_PORT", "587"))
        self.EMAIL_DESTINATARIO_ALERTA = os.getenv("EMAIL_DESTINATARIO_ALERTA", "ivangongora1092@gmail.com")
        self.campo_temperatura_id = int(os.getenv("CAMPO_TEMPERATURA_ID", "2"))
        self.campo_humedad_id = int(os.getenv("CAMPO_HUMEDAD_ID", "3"))
    
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
        print(f"   🔑 DeepSeek: {'✅ Configurado' if self.DEEPSEEK_API_KEY else '❌ No'}")
        print(f"   🎯 JWT: {self.JWT_ALGORITHM} (expira: {self.ACCESS_TOKEN_EXPIRE_MINUTES}min)")

# Instancia global - Esto fallará claramente si falta configuración
try:
    configuracion = ConfiguracionSimulacion()  # ← Nombre que busca principal.py
    configuracion.mostrar_configuracion()
    print("🎉 Configuración cargada exitosamente!")
except ValueError as e:
    print(f"🚨 Error de configuración: {e}")
    print("💡 Asegúrate de que tu archivo .env tenga todas las variables requeridas")
    # Puedes salir del programa o manejar el error según necesites
    # import sys
    # sys.exit(1)
    
    
# Añadir al final de configuracion.py
class ConfigEnergetico:
    # Ruta BASE - apunta al directorio app/
    BASE_DIR = Path(__file__).parent  # Esto apunta a /app
    
    # Ruta del CSV - está en app/data/recibos/
    RUTA_RECIBOS = BASE_DIR / "data" / "recibos" / "recibos_gdmth.csv"
    
    # Rutas para modelos ML (crear si no existen)
    RUTA_MODELOS = BASE_DIR / "modelos_ml"
    RUTA_MODELOS.mkdir(parents=True, exist_ok=True)
    
    # Parámetros del modelo
    HORIZONTE_PREDICCION = 12  # meses para proyecciones
    MESES_ENTRENAMIENTO = 24   # meses mínimos para entrenar modelos
    
    # Configuración de análisis
    MESES_ESTACIONALIDAD = 12