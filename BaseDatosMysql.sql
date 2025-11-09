-- -----------------------------------------------------------
-- Paso 1: Creación y uso de la base de datos
-- -----------------------------------------------------------

CREATE DATABASE IF NOT EXISTS sistemaiotA_db;
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Tabla de proyectos
CREATE TABLE proyectos (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(80) NOT NULL,
  descripcion TEXT NOT NULL,
  tipo_industria VARCHAR(50) NOT NULL DEFAULT 'General',
  usuario_id INT NOT NULL,
  FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Tabla de sensores
CREATE TABLE sensores (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(40) NOT NULL,
  tipo VARCHAR(40) NOT NULL,
  fecha_creacion DATETIME NOT NULL,
  habilitado BOOLEAN NOT NULL,
  dispositivo_id INT NOT NULL,
  FOREIGN KEY (dispositivo_id) REFERENCES dispositivos(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Tabla de campos de sensores
CREATE TABLE campos_sensores (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(30) NOT NULL,
  tipo_valor VARCHAR(40) NOT NULL,
  sensor_id INT NOT NULL,
  unidad_medida_id INT,
  FOREIGN KEY (sensor_id) REFERENCES sensores(id),
  FOREIGN KEY (unidad_medida_id) REFERENCES unidades_medida(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -----------------------------------------------------------
-- Paso 5: Tabla de registro de valores (OPTIMIZADA)
-- -----------------------------------------------------------

-- Tabla de valores registrados - OPTIMIZADA PARA ALTO VOLUMEN
CREATE TABLE valores (
  id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  valor DECIMAL(15,6) NOT NULL,
  fecha_hora_lectura DATETIME NOT NULL,
  fecha_hora_registro DATETIME NOT NULL,
  campo_id INT NOT NULL,
  
  FOREIGN KEY (campo_id) REFERENCES campos_sensores(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -----------------------------------------------------------
-- Paso 6: Tablas de Roles y Permisos
-- -----------------------------------------------------------

-- Tabla para definir los roles
CREATE TABLE roles (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    nombre_rol VARCHAR(50) NOT NULL UNIQUE,
    descripcion TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Tabla de unión para asignar roles a usuarios en proyectos específicos
CREATE TABLE proyecto_usuarios (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    proyecto_id INT NOT NULL,
    usuario_id INT NOT NULL,
    rol_id INT NOT NULL,
    UNIQUE (proyecto_id, usuario_id),
    FOREIGN KEY (proyecto_id) REFERENCES proyectos(id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    FOREIGN KEY (rol_id) REFERENCES roles(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Tabla de permisos
CREATE TABLE permisos (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    nombre_permiso VARCHAR(80) NOT NULL UNIQUE,
    descripcion TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Tabla de unión Rol-Permisos
CREATE TABLE rol_permisos (
    rol_id INT NOT NULL,
    permiso_id INT NOT NULL,
    PRIMARY KEY (rol_id, permiso_id),
    FOREIGN KEY (rol_id) REFERENCES roles(id),
    FOREIGN KEY (permiso_id) REFERENCES permisos(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -----------------------------------------------------------
-- Paso 7: Tabla de recibos de energía
-- -----------------------------------------------------------

CREATE TABLE recibos_energia (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    periodo DATE NOT NULL,
    fecha_carga DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    consumo_total_kwh DECIMAL(10, 2) NOT NULL,
    demanda_maxima_kw DECIMAL(10, 2) NOT NULL,
    costo_total DECIMAL(10, 2) NOT NULL,
    dias_facturados INT NOT NULL,
    factor_potencia DECIMAL(5, 2) NULL,
    tarifa VARCHAR(50) NULL,
    kwh_punta DECIMAL(10, 2) NULL,
    lote_nombre VARCHAR(255) NOT NULL DEFAULT 'default',
    
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    UNIQUE (usuario_id, lote_nombre, periodo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -----------------------------------------------------------
-- Paso 8: Tabla de agregados para reporting (OPCIONAL PERIÓDICO)
-- -----------------------------------------------------------

CREATE TABLE valores_agregados (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  campo_id INT NOT NULL,
  fecha DATE NOT NULL,
  hora TINYINT NOT NULL,
  valor_sum DECIMAL(15,6) NULL DEFAULT NULL,
  valor_min DECIMAL(15,6),
  valor_max DECIMAL(15,6),
  valor_avg DECIMAL(15,6),
  total_registros INT,
  
  UNIQUE KEY uk_campo_fecha_hora (campo_id, fecha, hora),
  INDEX idx_fecha_campo (fecha, campo_id),
  
  FOREIGN KEY (campo_id) REFERENCES campos_sensores(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -----------------------------------------------------------
-- Paso 9: ÍNDICES CRÍTICOS PARA OPTIMIZACIÓN
-- -----------------------------------------------------------

-- Índices para la tabla valores (ESENCIALES para rendimiento)
CREATE INDEX idx_valores_campo_fecha ON valores(campo_id, fecha_hora_lectura);
CREATE INDEX idx_valores_fecha_campo ON valores(fecha_hora_lectura, campo_id);
CREATE INDEX idx_valores_fecha ON valores(fecha_hora_lectura);
CREATE INDEX idx_valores_campo ON valores(campo_id);

-- Índices adicionales para otras tablas
CREATE INDEX idx_proyectos_usuario ON proyectos(usuario_id);
CREATE INDEX idx_dispositivos_proyecto ON dispositivos(proyecto_id);
CREATE INDEX idx_sensores_dispositivo ON sensores(dispositivo_id);
CREATE INDEX idx_campos_sensor ON campos_sensores(sensor_id);

-- -----------------------------------------------------------
-- Paso 10: TRIGGER para fecha automática en valores
-- -----------------------------------------------------------

DELIMITER $$
CREATE TRIGGER set_fecha_registro_valores
BEFORE INSERT ON valores
FOR EACH ROW
BEGIN
    IF NEW.fecha_hora_registro IS NULL THEN
        SET NEW.fecha_hora_registro = NOW();
    END IF;
END$$
DELIMITER ;

-- -----------------------------------------------------------
-- Paso 11: USUARIO Y PERMISOS
-- -----------------------------------------------------------
-- -----------------------------------------------------------
-- Paso 11: USUARIO Y PERMISOS (VERSIÓN MEJORADA)
-- -----------------------------------------------------------

-- 4️⃣ Eliminar usuario si ya existe
DROP USER IF EXISTS 'sistemaiot'@'localhost';

-- 5️⃣ Crear el usuario con contraseña
CREATE USER 'sistemaiot'@'localhost' IDENTIFIED BY 'raspberry';

-- 6️⃣ Otorgar privilegios completos sobre la base de datos
GRANT ALL PRIVILEGES ON sistemaiotA_db.* TO 'sistemaiot'@'localhost';

-- 7️⃣ Aplicar los cambios para que sean permanentes
FLUSH PRIVILEGES;

SELECT 'Base de datos IoT creada exitosamente!' as Mensaje;