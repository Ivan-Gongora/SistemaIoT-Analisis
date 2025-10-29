-- -----------------------------------------------------------
-- Paso 1: Creación y uso de la base de datos
-- -----------------------------------------------------------

-- 🚨 ATENCIÓN: Se usa el nombre de DB de tu archivo .env: sistemaiotV1_db
CREATE DATABASE IF NOT EXISTS sistemaiotA_db;

-- Usar la base de datos recién creada
USE sistemaiotA_db;

-- -----------------------------------------------------------
-- Paso 2: Tablas principales (Usuarios y Proyectos)
-- -----------------------------------------------------------

-- Tabla de usuarios
CREATE TABLE usuarios (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  nombre_usuario VARCHAR(150) NOT NULL UNIQUE,
  nombre VARCHAR(30) NOT NULL,
  apellido VARCHAR(30) NOT NULL,
  email VARCHAR(254) NOT NULL,
  contrasena VARCHAR(128) NOT NULL,
  activo BOOLEAN NOT NULL DEFAULT TRUE,
  fecha_registro DATETIME NOT NULL,
  ultimo_login DATETIME
);

-- Tabla de proyectos
CREATE TABLE proyectos (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(80) NOT NULL,
  descripcion TEXT NOT NULL,
  tipo_industria VARCHAR(50)NOT NULL DEFAULT 'General',
  usuario_id INT NOT NULL,
  FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

-- -----------------------------------------------------------
-- Paso 3: Tablas de configuración de datos
-- -----------------------------------------------------------

-- Tabla de unidades de medida
CREATE TABLE unidades_medida (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(20) NOT NULL,
  simbolo VARCHAR(10) NOT NULL,
  descripcion VARCHAR(100),
  magnitud_tipo VARCHAR(50) NOT NULL
);

-- -----------------------------------------------------------
-- Paso 4: Tablas de Hardware (Dispositivos y Sensores)
-- -----------------------------------------------------------

-- Tabla de dispositivos
CREATE TABLE dispositivos (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(80) NOT NULL,
  descripcion TEXT NOT NULL,
  tipo VARCHAR(40) NOT NULL,
  latitud DOUBLE,
  longitud DOUBLE,
  habilitado BOOLEAN NOT NULL,
  fecha_creacion DATETIME NOT NULL,
  proyecto_id INT NOT NULL,
  FOREIGN KEY (proyecto_id) REFERENCES proyectos(id)
);

-- Tabla de sensores
CREATE TABLE sensores (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(40) NOT NULL,
  tipo VARCHAR(40) NOT NULL,
  fecha_creacion DATETIME NOT NULL,
  habilitado BOOLEAN NOT NULL,
  dispositivo_id INT NOT NULL,
  FOREIGN KEY (dispositivo_id) REFERENCES dispositivos(id)
);

-- Tabla de campos de sensores
CREATE TABLE campos_sensores (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(30) NOT NULL,
  tipo_valor VARCHAR(40) NOT NULL,
  sensor_id INT NOT NULL,
  unidad_medida_id INT,
  FOREIGN KEY (sensor_id) REFERENCES sensores(id),
  FOREIGN KEY (unidad_medida_id) REFERENCES unidades_medida(id)
);

-- -----------------------------------------------------------
-- Paso 5: Tabla de registro de valores
-- -----------------------------------------------------------

-- Tabla de valores registrados
CREATE TABLE valores (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  valor VARCHAR(100) NOT NULL,
  fecha_hora_lectura DATETIME NOT NULL,
  fecha_dispositivo DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  campo_id INT NOT NULL,
  FOREIGN KEY (campo_id) REFERENCES campos_sensores(id)
);

-- -----------------------------------------------------------
-- Paso 6: Tablas de Roles y Permisos (Autorización)
-- -----------------------------------------------------------

-- Tabla para definir los roles
CREATE TABLE roles (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    nombre_rol VARCHAR(50) NOT NULL UNIQUE, -- Ej: 'Propietario', 'Editor', 'Observador'
    descripcion TEXT
);

-- Tabla de unión para asignar roles a usuarios en proyectos específicos
CREATE TABLE proyecto_usuarios (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    proyecto_id INT NOT NULL,
    usuario_id INT NOT NULL,
    rol_id INT NOT NULL,
    UNIQUE (proyecto_id, usuario_id), -- Un usuario solo puede tener un rol por proyecto
    FOREIGN KEY (proyecto_id) REFERENCES proyectos(id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    FOREIGN KEY (rol_id) REFERENCES roles(id)
);

-- Tabla de permisos
CREATE TABLE permisos (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    nombre_permiso VARCHAR(80) NOT NULL UNIQUE, -- 'crear_dispositivo', 'ver_reportes'
    descripcion TEXT
);

-- Tabla de unión Rol-Permisos
CREATE TABLE rol_permisos (
    rol_id INT NOT NULL,
    permiso_id INT NOT NULL,
    PRIMARY KEY (rol_id, permiso_id),
    FOREIGN KEY (rol_id) REFERENCES roles(id),
    FOREIGN KEY (permiso_id) REFERENCES permisos(id)
);

-- Crear el usuario con su contraseña
CREATE USER 'sistemaiot'@'localhost' IDENTIFIED BY 'raspberry';

-- Conceder todos los privilegios sobre la base de datos 'sistemaiota_db'
GRANT ALL PRIVILEGES ON sistemaiotA_db.* TO 'sistemaiot'@'localhost';

-- Aplicar los cambios de privilegios
FLUSH PRIVILEGES;

