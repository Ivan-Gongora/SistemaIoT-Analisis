# app/configuracion.py

import os
# Asegúrate de que load_dotenv() se ejecute en algún punto antes de importar este archivo
# (Típicamente en app/principal.py)

class ConfiguracionSimulacion:
    # --- Configuración de Base de Datos MySQL ---
    db_host: str = os.getenv("DB_HOST", "localhost")
    db_port: int = int(os.getenv("DB_PORT", 3306))
    db_user: str = os.getenv("DB_USER", "sistemaiot") 
    db_password: str = os.getenv("DB_PASSWORD", "raspberry")
    db_name: str = os.getenv("DB_NAME", "sistemaiotA_db") 
    # ...

    # --- Configuración para JWT (¡NUEVA SECCIÓN!) ---
    # 🚨 CRÍTICO: Estas son las variables que faltaban y causaban el error
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "7Q5w0SJ9sMsUKSqrF2PJJ1ebEMrYZHHYAhXUIEipZqo") 
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30)) # 30 minutos por defecto

    # --- Configuración de Parámetros de la Simulación ---
    campo_temperatura_id: int = int(os.getenv("CAMPO_TEMPERATURA_ID", 2))
    campo_humedad_id: int = int(os.getenv("CAMPO_HUMEDAD_ID", 3))

    # --- Configuración para envío de correos ---
    EMAIL_SMTP_SERVER: str = os.getenv("EMAIL_SMTP_SERVER", "smtp.gmail.com")
    EMAIL_SMTP_PORT: int = int(os.getenv("EMAIL_SMTP_PORT", 587))
    
    EMAIL_REMITENTE: str = os.getenv("EMAIL_REMITENTE_CORREO") 
    EMAIL_PASSWORD: str = os.getenv("EMAIL_PASSWORD") 
    
    EMAIL_DESTINATARIO_ALERTA: str = os.getenv("EMAIL_DESTINATARIO_ALERTA", "ivangongora1092@gmail.com")


configuracion = ConfiguracionSimulacion()