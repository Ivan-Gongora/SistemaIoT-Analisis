-- ------------------------------------------------------------
-- SCRIPT DE INSERCIÓN DE DATOS DE PRUEBA INICIALES
-- ------------------------------------------------------------

-- PASO 0: DESHABILITAR VERIFICACIÓN DE CLAVES FORÁNEAS
SET FOREIGN_KEY_CHECKS = 0;

-- LIMPIEZA COMPLETA DE TABLAS (solo si es necesario)
TRUNCATE TABLE proyecto_usuarios;
TRUNCATE TABLE valores;
TRUNCATE TABLE campos_sensores;
TRUNCATE TABLE sensores;
TRUNCATE TABLE dispositivos;
TRUNCATE TABLE proyectos;
TRUNCATE TABLE usuarios;
TRUNCATE TABLE unidades_medida;
TRUNCATE TABLE roles;
TRUNCATE TABLE permisos;
TRUNCATE TABLE rol_permisos;

-- RESETEAR AUTO_INCREMENT
ALTER TABLE usuarios AUTO_INCREMENT = 1;
ALTER TABLE proyectos AUTO_INCREMENT = 1;
ALTER TABLE dispositivos AUTO_INCREMENT = 1;
ALTER TABLE sensores AUTO_INCREMENT = 1;
ALTER TABLE campos_sensores AUTO_INCREMENT = 1;
ALTER TABLE valores AUTO_INCREMENT = 1;
ALTER TABLE roles AUTO_INCREMENT = 1;
ALTER TABLE unidades_medida AUTO_INCREMENT = 1;
ALTER TABLE permisos AUTO_INCREMENT = 1;
ALTER TABLE proyecto_usuarios AUTO_INCREMENT = 1;

-- ************************************************************
-- INSERCIÓN DE DATOS BASE (ROLES, PERMISOS Y UNIDADES)
-- ************************************************************

-- ROLES DEL SISTEMA
INSERT INTO roles (nombre_rol, descripcion) VALUES
('Administrador', 'Control total del sistema'),
('Propietario', 'Dueño del proyecto con permisos de gestión'),
('Observador', 'Puede ver datos, pero no modificar configuraciones'),
('Colaborador', 'Puede modificar y crear sensores/datos en proyectos invitados');

-- UNIDADES DE MEDIDA
INSERT INTO unidades_medida (nombre, simbolo, descripcion, magnitud_tipo) VALUES
('Celsius', '°C', 'Temperatura en grados Celsius', 'Temperatura'),
('Humedad Relativa', '%', 'Porcentaje de humedad', 'Humedad'),
('Voltios', 'V', 'Tensión eléctrica', 'Electricidad'),
('Lux', 'lx', 'Intensidad de iluminación', 'Iluminación'),
('Kilowatt-hora', 'kWh', 'Consumo de energía eléctrica', 'Energía'),
('Watts', 'W', 'Potencia eléctrica', 'Potencia'),
('Booleano (Estado)', 'bool', 'Estado binario (0/1, On/Off)', 'Estado'),
('Segundo', 's', 'Unidad de tiempo', 'Tiempo'),
('HectoPascales', 'hPa', 'Presión atmosférica', 'Presión'),
('Metros', 'm', 'Distancia o longitud', 'Distancia'),
('Partes por millón', 'ppm', 'Concentración de gases o partículas', 'Concentración'),
('Fahrenheit', '°F', 'Temperatura en grados Fahrenheit', 'Temperatura'),
('Amperios', 'A', 'Corriente eléctrica (Intensidad)', 'Electricidad'),
('Miliamperios', 'mA', 'Corriente eléctrica (Intensidad)', 'Electricidad'),
('Pascales', 'Pa', 'Presión (Unidad SI)', 'Presión'),
('Bar', 'bar', 'Unidad de presión (1 bar ≈ 1 atm)', 'Presión'),
('Centímetros', 'cm', 'Distancia o longitud (para sensores ultrasónicos)', 'Distancia'),
('Gramos', 'g', 'Masa o peso', 'Masa'),
('Kilogramos', 'kg', 'Masa o peso', 'Masa'),
('Litros', 'L', 'Volumen de líquidos', 'Volumen'),
('Litros por minuto', 'L/min', 'Caudal o flujo de líquido', 'Flujo'),
('Decibelios', 'dB', 'Nivel de intensidad de sonido', 'Sonido'),
('Hertz', 'Hz', 'Frecuencia', 'Frecuencia'),
('Minuto', 'min', 'Unidad de tiempo', 'Tiempo'),
('Grados (Angulo)', '°', 'Medida angular (para servos, giroscopios)', 'Angulo'),
('Conteo (Unidad)', 'N/A', 'Para conteo de eventos o ítems (ej. pulsos)', 'Conteo'),
('Grados por segundo', '°/s', 'Velocidad angular (Usada en Giroscopios)', 'Velocidad Angular'),
('Kilómetros por hora', 'km/h', 'Velocidad lineal (Viento o vehicular)', 'Velocidad'),
('Metros por segundo', 'm/s', 'Velocidad lineal (Unidad SI)', 'Velocidad'),
('pH', 'pH', 'Nivel de acidez o alcalinidad (Calidad de agua/suelo)', 'pH'),
('Newton', 'N', 'Medida de fuerza (Usada en celdas de carga)', 'Fuerza'),
('Índice Ultravioleta', 'Índice UV', 'Intensidad de radiación solar UV', 'Radiación'),
('Factor de Potencia', 'PF', 'Eficiencia eléctrica (Adimensional, cos(φ))', 'Factor de Potencia');

-- PERMISOS DEL SISTEMA
INSERT INTO permisos (nombre_permiso, descripcion) VALUES
('GESTION_USUARIOS', 'Permite el control total de las cuentas de usuario'),
('CRUD_PROYECTO', 'Permite crear, modificar y eliminar proyectos'),
('VER_LISTA_GLOBAL', 'Permite ver una lista global de todos los proyectos/dispositivos'),
('GESTIONAR_ACCESO', 'Permite invitar y remover a otros usuarios de un proyecto'),
('CRUD_SENSOR', 'Permite crear/modificar/eliminar sensores y sus campos'),
('CRUD_DATO_SENSOR', 'Permite crear/modificar/eliminar datos de sensores');

-- ASIGNACIÓN DE PERMISOS A ROLES
INSERT INTO rol_permisos (rol_id, permiso_id) VALUES
-- Administrador (todos los permisos)
(1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6),
-- Propietario (gestión de proyectos, acceso, sensores y datos)
(2, 2), (2, 4), (2, 5), (2, 6),
-- Colaborador (solo manipulación de sensores y datos)
(4, 5), (4, 6);

-- ************************************************************
-- INSERCIÓN DE USUARIOS Y PROYECTOS DE PRUEBA
-- ************************************************************

-- USUARIOS DE PRUEBA (contraseña: "testpass" hasheada con bcrypt)
INSERT INTO usuarios (nombre_usuario, nombre, apellido, email, contrasena, activo, fecha_registro, ultimo_login) VALUES
('admin_user', 'Iván', 'Góngora', 'ivan@ejemplo.com', '$2b$12$4pOr6.S0V9pC.I0tfkbFxuujiYLR0/5IjgU.nKj3Cwo2O5QenY2ki', TRUE, NOW(), NOW()),
('colaborador', 'Ana', 'Pérez', 'ana@ejemplo.com', '$2b$12$4pOr6.S0V9pC.I0tfkbFxuujiYLR0/5IjgU.nKj3Cwo2O5QenY2ki', TRUE, NOW(), NULL),
('observador', 'Roger', 'Smith', 'roger@ejemplo.com', '$2b$12$4pOr6.S0V9pC.I0tfkbFxuujiYLR0/5IjgU.nKj3Cwo2O5QenY2ki', TRUE, NOW(), NULL);

-- PROYECTOS DE PRUEBA
INSERT INTO proyectos (nombre, descripcion, usuario_id, tipo_industria) VALUES
('Invernadero Principal', 'Monitoreo de temperatura y humedad para el cultivo de tomates', 1, 'Agricultura Precision'),
('Estación Meteorológica', 'Recolección de datos ambientales generales en el tejado', 1, 'Monitoreo Ambiental');

-- ASIGNACIÓN DE USUARIOS A PROYECTOS
INSERT INTO proyecto_usuarios (proyecto_id, usuario_id, rol_id) VALUES
(1, 1, 2), -- Iván como Propietario del Proyecto 1
(1, 2, 4), -- Ana como Colaborador del Proyecto 1
(2, 1, 2); -- Iván como Propietario del Proyecto 2

-- DISPOSITIVOS DE PRUEBA
INSERT INTO dispositivos (nombre, descripcion, tipo, latitud, longitud, habilitado, fecha_creacion, proyecto_id) VALUES
('NodeMCU Zona Norte', 'Dispositivo ESP8266 para medir condiciones cerca de la puerta', 'Microcontrolador', 20.5, -87.0, TRUE, NOW(), 1),
('Estación Exterior', 'Dispositivo principal para datos exteriores', 'Raspberry Pi', 20.501, -87.001, TRUE, NOW(), 2);

-- SENSORES DE PRUEBA
INSERT INTO sensores (nombre, tipo, fecha_creacion, habilitado, dispositivo_id) VALUES
('DHT22-Aire', 'Temperatura/Humedad', NOW(), TRUE, 1),
('DS18B20-Suelo', 'Temperatura', NOW(), TRUE, 1);

-- CAMPOS DE SENSORES DE PRUEBA
INSERT INTO campos_sensores (nombre, tipo_valor, sensor_id, unidad_medida_id) VALUES
('Temperatura Ambiente', 'Float', 1, 1),
('Humedad Relativa', 'Float', 1, 2),
('Temperatura Suelo', 'Float', 2, 1);

-- DATOS DE VALORES DE PRUEBA (opcional - para demostración)
INSERT INTO valores (valor, fecha_medicion, campo_sensor_id) VALUES
(25.5, NOW() - INTERVAL 1 HOUR, 1),
(65.2, NOW() - INTERVAL 1 HOUR, 2),
(22.8, NOW() - INTERVAL 1 HOUR, 3),
(26.1, NOW(), 1),
(63.8, NOW(), 2),
(23.2, NOW(), 3);

-- PASO FINAL: HABILITAR VERIFICACIÓN DE CLAVES FORÁNEAS
SET FOREIGN_KEY_CHECKS = 1;

-- CONFIRMACIÓN DE INSERCIÓN
SELECT 'Datos de prueba insertados exitosamente' AS Estado;