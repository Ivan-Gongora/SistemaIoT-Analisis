# app/principal.py (CÓDIGO ESTABLE Y LIMPIO)

from fastapi import FastAPI, UploadFile, File, Form 
from fastapi.responses import HTMLResponse 
from fastapi.staticfiles import StaticFiles 
from fastapi.middleware.cors import CORSMiddleware 
from dotenv import load_dotenv 

# 🚨 Cargar variables de entorno una vez
load_dotenv() 

from app.configuracion import ConfiguracionSimulacion

# Importación de Routers
from app.api.rutas.valores.valores import router as valores_router
from app.api.rutas.proyectos.proyectos import router_proyecto as router_proyecto
from app.api.rutas.dispositivos.dispositivos import router_dispositivo as router_dispositivo
from app.api.rutas.simulacion import router as simulacion_router 
from app.api.rutas.sensores.sensores import router_sensor as router_sensor
from app.api.rutas.usuarios.usuarios import router_usuario as router_usuario
from app.api.rutas.unidades_medida import router_unidades as router_unidades
from app.api.rutas.campos_sensor.campos_sensor import router_campos as router_campos
from app.api.rutas.recepcion.recepcion import router_recepcion as router_recepcion

from app.api.rutas.energetico.analisis import router as energetico_analisis_router
from app.api.rutas.energetico.proyecciones import router as energetico_proyecciones_router
from app.api.rutas.energetico.gestion_datos import router as energetico_gestion_datos_router # <-- ¡CORREGIDO!

from app.api.rutas.energetico.proyecciones import router as energetico_proyecciones_router
# Se importa el treading para doble ejecución de servicios sin detener uno
import threading, socket, time
from cryptography.fernet import Fernet

# ===========================================================
# CONFIGURACIÓN DE SEGURIDAD
# ===========================================================
PUERTO_DISCOVERY = 37020 
FERNET_KEY = b"g5967SRvdflzMRzDxV5BwRE5YfTMF-8PASNQ4RGPFL0="  # <--- clave Fernet generada
# COORDINADOR_IP = "192.168.1.75"  # IP fija del coordinador (opcional)
RATE_LIMIT_INTERVAL = 1.0  # segundos entre solicitudes válidas

fernet = Fernet(FERNET_KEY)
ultimo_tiempo = 0


def obtener_ip_local():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip_local = s.getsockname()[0]
    finally:
        s.close()
    return ip_local


def udp_discovery():
    global ultimo_tiempo

    mensaje_respuesta = obtener_ip_local().encode()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", PUERTO_DISCOVERY))
    print(f"Esperando broadcast UDP cifrado en el puerto {PUERTO_DISCOVERY}")

    while True:
        data, addr = sock.recvfrom(1024)
        ip_remota = addr[0]

        #Filtro de IP dispositivo
        #if COORDINADOR_IP and ip_remota != COORDINADOR_IP:
        #   print(f"Petición rechazada de IP no autorizada: {ip_remota}")
        #  continue

        # Rate limit 
        tiempo_actual = time.time()
        if tiempo_actual - ultimo_tiempo < RATE_LIMIT_INTERVAL:
            print("Demasiadas solicitudes, ignorando...")
            continue
        ultimo_tiempo = tiempo_actual

        try:
            # Desifrado del mensaje
            mensaje = fernet.decrypt(data).decode()
        except Exception:
            print(f"Mensaje no válido o no cifrado desde la ip remota: {ip_remota}")
            continue

        if mensaje != "DISCOVER_SERVER":
            print(f"Mensaje inesperado: {mensaje}")
            continue

        print(f"Solicitud válida y autenticada de ip remota: {ip_remota}")
        sock.sendto(mensaje_respuesta, addr)
        print(f"IP del servidor enviada: {mensaje_respuesta.decode()}")


# Lanzar hilo paralelo para escuchar broadcast
threading.Thread(target=udp_discovery, daemon=True).start()


aplicacion = FastAPI()

aplicacion.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["POST", "PUT", "GET", "DELETE"],
    allow_headers=["*"],
)

aplicacion.mount("/web", StaticFiles(directory="web"), name="web")

# -----------------------------------------------------
# INCLUSIÓN DE RUTAS (MANTENEMOS EL DOBLE ENRUTAMIENTO POR ESTABILIDAD)
# -----------------------------------------------------

# Bloque 1: Sin prefijo /api
aplicacion.include_router(valores_router)
aplicacion.include_router(router_proyecto)
aplicacion.include_router(router_dispositivo)
aplicacion.include_router(router_sensor)
aplicacion.include_router(router_usuario)

aplicacion.include_router(valores_router, prefix="/api") # MOVIDO AL INICIO para priorizar /valores/historico/
# Bloque 2: Con prefijo /api (ESTE ES EL QUE DEBE USAR VUE.JS)
aplicacion.include_router(router_proyecto, prefix="/api") 
aplicacion.include_router(router_dispositivo, prefix="/api") 
aplicacion.include_router(simulacion_router, prefix="/api") 
aplicacion.include_router(router_sensor, prefix="/api")
aplicacion.include_router(router_usuario, prefix="/api")
aplicacion.include_router(router_unidades, prefix="/api", tags=["Unidades de Medida"])
aplicacion.include_router(router_campos, prefix="/api", tags=["Campos de Sensor"])
aplicacion.include_router(router_recepcion, prefix="/api", tags=["Recepción de Datos"])

aplicacion.include_router(energetico_analisis_router, prefix="/api")
aplicacion.include_router(energetico_proyecciones_router, prefix="/api")
aplicacion.include_router(energetico_gestion_datos_router, prefix="/api")


@aplicacion.get("/", response_class=HTMLResponse)
async def read_root():
    with open("web/index.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)







# import os
# from dotenv import load_dotenv
# from fastapi import FastAPI, HTTPException, status
# from fastapi.responses import HTMLResponse, FileResponse
# from fastapi.staticfiles import StaticFiles
# from fastapi.middleware.cors import CORSMiddleware

# # Cargar variables de entorno desde .env al inicio
# load_dotenv()

# # Importar routers de la API
# from app.api.rutas.simulacion import router as simulacion_router
# from app.api.rutas.proyectos.proyectos import router_proyecto as router_proyecto
# from app.api.rutas.dispositivos.dispositivos import router_dispositivo as router_dispositivo
# # Asumo que 'endpoints' es otro router que tenías. Si no lo usas, puedes eliminarlo.
# from app.servicios.endpoints import router as valores_router

# # Inicializar la aplicación FastAPI
# aplicacion = FastAPI(
#     title="API de Simulación IoT",
#     description="API para simular datos de sensores IoT y gestionar alertas.",
#     version="1.0.0"
# )

# # Configuración de CORS
# origins = [
#     "http://localhost:8080",  # Puerto de desarrollo típico de Vue CLI
#     "http://127.0.0.1:8080",
#     "http://localhost:5173",  # Puerto de desarrollo típico de Vite (si lo usas)
#     "http://127.0.0.1:5173",
#     # Agrega aquí cualquier otro dominio donde vayas a desplegar tu frontend en producción
# ]
# aplicacion.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # --- Rutas de API ---
# # Asegúrate de que los prefijos sean correctos y no se superpongan accidentalmente.
# aplicacion.include_router(valores_router) # Si no tiene prefijo, se monta en la raíz
# aplicacion.include_router(router_proyecto, prefix="/api")
# aplicacion.include_router(router_dispositivo, prefix="/api")
# aplicacion.include_router(simulacion_router, prefix="/api")


# # --- SERVIR ARCHIVOS ESTÁTICOS DE VUE.JS ---
# # Define la ruta a tu carpeta 'dist' de Vue.js
# # Esta ruta asume que 'principal.py' está en 'tu_proyecto/app/'
# # y 'dist' está en 'tu_proyecto/vue/frontend-vue/dist/'
# FRONTEND_DIST_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "vue", "frontend-vue", "dist")

# # Verificar si el directorio 'dist' existe.
# # Es crucial que ejecutes 'npm run build' en tu proyecto Vue.js para que esta carpeta exista.
# if not os.path.isdir(FRONTEND_DIST_DIR):
#     print(f"Advertencia: El directorio del frontend '{FRONTEND_DIST_DIR}' no se encontró.")
#     print("Asegúrate de haber ejecutado 'npm run build' en la carpeta 'vue/frontend-vue'.")
#     # Puedes optar por levantar un error aquí si el frontend es esencial
#     # raise RuntimeError(f"Directorio de frontend no encontrado: {FRONTEND_DIST_DIR}")

# # Monta la carpeta 'dist' de Vue.js en la URL '/static'.
# # Los archivos como 'app.js', 'styles.css' (y sus hashes) serán accesibles vía /static/...
# aplicacion.mount("/static", StaticFiles(directory=FRONTEND_DIST_DIR), name="static")

# # Ruta para servir el 'index.html' de tu aplicación Vue.js para el routing del lado del cliente.
# # Esta ruta debe ser la ÚLTIMA definida, ya que capturará todas las demás rutas no API.
# @aplicacion.get("/{full_path:path}", response_class=HTMLResponse)
# async def serve_vue_app(full_path: str):
#     index_file_path = os.path.join(FRONTEND_DIST_DIR, "index.html")
#     # Si el archivo index.html no se encuentra (ej. 'npm run build' no se ejecutó),
#     # devuelve un error 404 para evitar que la aplicación se "cuelgue".
#     if not os.path.exists(index_file_path):
#         raise HTTPException(status_code=404, detail="Frontend index.html no encontrado. ¿Has compilado tu proyecto Vue.js?")
#     return FileResponse(index_file_path)

# # Ruta raíz para servir la aplicación Vue.js.
# # Cuando alguien acceda directamente a http://localhost:8001/, se le entregará el index.html.
# @aplicacion.get("/")
# async def read_root():
#     index_file_path = os.path.join(FRONTEND_DIST_DIR, "index.html")
#     if not os.path.exists(index_file_path):
#         raise HTTPException(status_code=404, detail="Frontend index.html no encontrado. ¿Has compilado tu proyecto Vue.js?")
#     return FileResponse(index_file_path)







# @aplicacion.post("/simular/")
# async def simular_datos(
#     file: UploadFile = File(...),
#     proyecto_id: int = Form(...),    # Nuevo parámetro del formulario
#     dispositivo_id: int = Form(...) # Nuevo parámetro del formulario
# ):
#     try:
#         file_content = await file.read()
#         print(f"Archivo recibido: {file.filename}, tamaño: {len(file_content)} bytes")
#         print(f"IDs recibidos: Proyecto={proyecto_id}, Dispositivo={dispositivo_id}")

#         # Pasa los IDs a la función de servicio
#         resultados = await simular_datos_csv(file_content, proyecto_id, dispositivo_id)

#         return {"message": "Simulación y carga de datos en DB completada.", "resultados": resultados}

#     except ValueError as e:
#         return {"message": "Error en la validación del CSV", "details": str(e)}
#     except Exception as e:
#         return {"message": "Error inesperado durante la simulación", "details": str(e)}
# app/principal.py




# @aplicacion.post("/api/simular/") # Se le añade el prefijo /api explícitamente
# async def simular_datos(
#     file: UploadFile = File(...),
#     sensor_mappings: str = Form(...), # sensor_mappings viene como JSON string
#     proyecto_id: int = Form(...),
#     dispositivo_id: int = Form(...)
# ):
#     try:
#         import json # Importa json aquí si solo se usa en esta función
#         parsed_sensor_mappings = json.loads(sensor_mappings)

#         file_content = await file.read()
#         print(f"Archivo recibido: {file.filename}, tamaño: {len(file_content)} bytes")
#         print(f"IDs recibidos: Proyecto={proyecto_id}, Dispositivo={dispositivo_id}")
#         # print(f"Mapeos recibidos: {parsed_sensor_mappings}") # No imprimir en producción, solo para depuración

#         # Pasa los IDs de proyecto y dispositivo a simular_datos_csv
#         resultados = await simular_datos_csv(
#             file_content,
#             parsed_sensor_mappings,
#             proyecto_id,  # Nuevo parámetro
#             dispositivo_id # Nuevo parámetro
#         )

#         return {"message": "Simulación y carga de datos en DB completada.", "resultados": resultados}

#     except json.JSONDecodeError:
#         return {"message": "Error en el formato JSON de los mapeos de sensores.", "details": "El string 'sensor_mappings' no es un JSON válido."}, 400
#     except ValueError as e:
#         return {"message": "Error en la validación del CSV o mapeo", "details": str(e)}, 400
#     except Exception as e:
#         print(f"Error inesperado durante la simulación: {e}") # Para depuración
#         return {"message": "Error inesperado durante la simulación", "details": str(e)}, 500
