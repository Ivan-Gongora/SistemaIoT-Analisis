-- ------------------------------------------------------------
-- SCRIPT DE PRUEBA FINAL Y DEFINITIVO (COMPLETAMENTE LIMPIO)
-- ------------------------------------------------------------

-- PASO 0: DESHABILITAR LA VERIFICACIÓN DE CLAVES FORÁNEAS (Para TRUNCATE)
SET FOREIGN_KEY_CHECKS = 0;

-- LIMPIEZA DE TABLAS
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
-- PASO 1: CREACIÓN DE COLUMNA DE SECTOR (tipo_industria)
-- ************************************************************
-- Usamos IF NOT EXISTS para prevenir el ERROR 1060
ALTER TABLE proyectos ADD COLUMN IF NOT EXISTS tipo_industria VARCHAR(50) DEFAULT 'General';


-- ************************************************************
-- PASO 2: INSERCIONES DE ROLES, PERMISOS Y UNIDADES
-- ************************************************************

-- ROLES BASE
TRUNCATE TABLE roles;
INSERT INTO roles (id, nombre_rol, descripcion) VALUES
(1, 'Administrador', 'Control total del sistema'),
(2, 'Propietario', 'Dueño del proyecto con permisos de gestión'),
(3, 'Observador', 'Puede ver datos, pero no modificar configuraciones.'),
(4, 'Colaborador', 'Puede modificar y crear sensores/datos en proyectos invitados.'); -- 🚨 ROL AÑADIDO

-- UNIDADES DE MEDIDA
INSERT INTO unidades_medida (id, nombre, simbolo, descripcion) VALUES
(1, 'Celsius', '°C', 'Temperatura en grados Celsius'), 
(2, 'Humedad Relativa', '%', 'Porcentaje de humedad'), 
(3, 'Voltios', 'V', 'Tensión eléctrica');  

-- PERMISOS AMPLIADOS
INSERT INTO permisos (nombre_permiso, descripcion) VALUES
('GESTION_USUARIOS', 'Permite el control total de las cuentas de usuario.'),
('CRUD_PROYECTO', 'Permite crear, modificar y eliminar proyectos.'),
('VER_LISTA_GLOBAL', 'Permite ver una lista global de todos los proyectos/dispositivos.'),
('GESTIONAR_ACCESO', 'Permite invitar y remover a otros usuarios de un proyecto.'),
('CRUD_SENSOR', 'Permite crear/modificar/eliminar sensores y sus campos.'),
('CRUD_DATO_SENSOR', 'Permite crear/modificar/eliminar datos de sensores.');

-- ASIGNACIÓN DE PERMISOS (ROL_PERMISOS)
TRUNCATE TABLE rol_permisos;

-- 1. Admin (ID 1) obtiene TODOS
INSERT INTO rol_permisos (rol_id, permiso_id)
SELECT 1, id FROM permisos;

-- 2. Propietario (ID 2) obtiene CRUD_PROYECTO, GESTIONAR_ACCESO, CRUD_SENSOR, CRUD_DATO_SENSOR
INSERT INTO rol_permisos (rol_id, permiso_id)
SELECT 2, id FROM permisos WHERE nombre_permiso IN ('CRUD_PROYECTO', 'GESTIONAR_ACCESO', 'CRUD_SENSOR', 'CRUD_DATO_SENSOR');

-- 🚨 3. Colaborador (ID 4) obtiene solo manipulación de datos y sensores
INSERT INTO rol_permisos (rol_id, permiso_id)
SELECT 4, id FROM permisos WHERE nombre_permiso IN ('CRUD_SENSOR', 'CRUD_DATO_SENSOR');
-- ************************************************************
-- PASO 3: INSERCIÓN DE DATOS DE PRUEBA (USUARIOS Y PROYECTOS)
-- ************************************************************

-- -- USUARIOS (IDs 1 y 2)
-- INSERT INTO usuarios (id, nombre_usuario, nombre, apellido, email, contrasena, activo, fecha_registro, ultimo_login) VALUES
-- (1, 'admin_user', 'Iván', 'Góngora', 'ivan@ejemplo.com', '$2b$12$4pOr6.S0V9pC.I0tfkbFxuujiYLR0/5IjgU.nKj3Cwo2O5QenY2ki', TRUE, NOW(), NOW()), 
-- (2, 'observador', 'Ana', 'Pérez', 'ana@ejemplo.com', '$2b$12$4pOr6.S0V9pC.I0tfkbFxuujiYLR0/5IjgU.nKj3Cwo2O5QenY2ki', TRUE, NOW(), NULL);  


-- USUARIOS (Añadimos un usuario colaborador)
INSERT INTO usuarios (id, nombre_usuario, nombre, apellido, email, contrasena, activo, fecha_registro, ultimo_login) VALUES
(1, 'admin_user', 'Iván', 'Góngora', 'ivan@ejemplo.com', '$2b$12$4pOr6.S0V9pC.I0tfkbFxuujiYLR0/5IjgU.nKj3Cwo2O5QenY2ki', TRUE, NOW(), NOW()), 
(2, 'colaborador', 'Ana', 'Pérez', 'ana@ejemplo.com', '$2b$12$4pOr6.S0V9pC.I0tfkbFxuujiYLR0/5IjgU.nKj3Cwo2O5QenY2ki', TRUE, NOW(), NULL), -- 🚨 Ana ahora es la Colaboradora de prueba
(3, 'observador_solo', 'Roger', 'Smith', 'roger@ejemplo.com', '$2b$12$4pOr6.S0V9pC.I0tfkbFxuujiYLR0/5IjgU.nKj3Cwo2O5QenY2ki', TRUE, NOW(), NULL);




-- PROYECTOS (Asegúrate de que 'tipo_industria' esté incluido en el DDL y aquí no es necesario)
INSERT INTO proyectos (id, nombre, descripcion, usuario_id, tipo_industria) VALUES
(1, 'Invernadero Principal', 'Monitoreo de temperatura y humedad para el cultivo de tomates.', 1, 'Agricultura Precision'), 
(2, 'Estación Meteorológica', 'Recolección de datos ambientales generales en el tejado.', 1, 'Monitoreo Ambiental');

-- PROYECTO_USUARIOS (MEMBRESÍA)
TRUNCATE TABLE proyecto_usuarios;
INSERT INTO proyecto_usuarios (proyecto_id, usuario_id, rol_id) VALUES
(1, 1, 2), -- Iván (ID 1) es Propietario (ROL 2) del Proyecto 1
(1, 2, 4), -- 🚨 Ana (ID 2) es Colaborador (ROL 4) del Proyecto 1
(2, 1, 2); -- Iván (ID 1) es Propietario (ROL 2) del Proyecto 2

-- DISPOSITIVOS
INSERT INTO dispositivos (id, nombre, descripcion, tipo, latitud, longitud, habilitado, fecha_creacion, proyecto_id) VALUES
(1, 'NodeMCU Zona Norte', 'Dispositivo ESP8266 para medir cond. cerca de la puerta.', 'Microcontrolador', 20.5, -87.0, TRUE, NOW(), 1), 
(2, 'Estación Exterior', 'Dispositivo principal para datos exteriores.', 'Raspberry Pi', 20.501, -87.001, TRUE, NOW(), 2); 

-- SENSORES
INSERT INTO sensores (id, nombre, tipo, fecha_creacion, habilitado, dispositivo_id) VALUES
(1, 'DHT22-Aire', 'Temperatura/Humedad', NOW(), TRUE, 1), 
(2, 'DS18B20-Suelo', 'Temperatura', NOW(), TRUE, 1); 

-- CAMPOS SENSORES
INSERT INTO campos_sensores (id, nombre, tipo_valor, sensor_id, unidad_medida_id) VALUES
(1, 'Temperatura Ambiente', 'Float', 1, 1), 
(2, 'Humedad Relativa', 'Float', 1, 2), 
(3, 'Temperatura Suelo', 'Float', 2, 1); 

-- VALORES
INSERT INTO valores (valor, fecha_hora_lectura, campo_id) VALUES
('29.1', NOW(), 1), ('66.0', NOW(), 2), ('22.2', NOW(), 3);


-- PASO FINAL: HABILITAR LA VERIFICACIÓN DE CLAVES FORÁNEAS
SET FOREIGN_KEY_CHECKS = 1;