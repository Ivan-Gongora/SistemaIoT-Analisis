-- MySQL dump 10.13  Distrib 8.0.42, for Linux (x86_64)
--
-- Host: localhost    Database: sistemaiotA_db
-- ------------------------------------------------------
-- Server version	8.0.42-0ubuntu0.20.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `campos_sensores`
--

DROP TABLE IF EXISTS `campos_sensores`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `campos_sensores` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(30) NOT NULL,
  `tipo_valor` varchar(40) NOT NULL,
  `sensor_id` int NOT NULL,
  `unidad_medida_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `sensor_id` (`sensor_id`),
  KEY `unidad_medida_id` (`unidad_medida_id`),
  CONSTRAINT `campos_sensores_ibfk_1` FOREIGN KEY (`sensor_id`) REFERENCES `sensores` (`id`),
  CONSTRAINT `campos_sensores_ibfk_2` FOREIGN KEY (`unidad_medida_id`) REFERENCES `unidades_medida` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `campos_sensores`
--

LOCK TABLES `campos_sensores` WRITE;
/*!40000 ALTER TABLE `campos_sensores` DISABLE KEYS */;
INSERT INTO `campos_sensores` VALUES (1,'Temperatura Ambiente','Float',1,1),(2,'Humedad Relativa','Float',1,2),(3,'Temperatura Suelo','Float',2,1);
/*!40000 ALTER TABLE `campos_sensores` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `dispositivos`
--

DROP TABLE IF EXISTS `dispositivos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dispositivos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(80) NOT NULL,
  `descripcion` text NOT NULL,
  `tipo` varchar(40) NOT NULL,
  `latitud` double DEFAULT NULL,
  `longitud` double DEFAULT NULL,
  `habilitado` tinyint(1) NOT NULL,
  `fecha_creacion` datetime NOT NULL,
  `proyecto_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `proyecto_id` (`proyecto_id`),
  CONSTRAINT `dispositivos_ibfk_1` FOREIGN KEY (`proyecto_id`) REFERENCES `proyectos` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `dispositivos`
--

LOCK TABLES `dispositivos` WRITE;
/*!40000 ALTER TABLE `dispositivos` DISABLE KEYS */;
INSERT INTO `dispositivos` VALUES (1,'NodeMCU Zona Norte','Dispositivo ESP8266 para medir cond. cerca de la puerta.','Microcontrolador',20.5,-87,1,'2025-10-14 19:37:43',1),(2,'Estación Exterior','Dispositivo principal para datos exteriores.','Raspberry Pi',20.501,-87.001,1,'2025-10-14 19:37:43',2);
/*!40000 ALTER TABLE `dispositivos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `permisos`
--

DROP TABLE IF EXISTS `permisos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `permisos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre_permiso` varchar(80) NOT NULL,
  `descripcion` text,
  PRIMARY KEY (`id`),
  UNIQUE KEY `nombre_permiso` (`nombre_permiso`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `permisos`
--

LOCK TABLES `permisos` WRITE;
/*!40000 ALTER TABLE `permisos` DISABLE KEYS */;
/*!40000 ALTER TABLE `permisos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `proyecto_usuarios`
--

DROP TABLE IF EXISTS `proyecto_usuarios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `proyecto_usuarios` (
  `id` int NOT NULL AUTO_INCREMENT,
  `proyecto_id` int NOT NULL,
  `usuario_id` int NOT NULL,
  `rol_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `proyecto_id` (`proyecto_id`,`usuario_id`),
  KEY `usuario_id` (`usuario_id`),
  KEY `rol_id` (`rol_id`),
  CONSTRAINT `proyecto_usuarios_ibfk_1` FOREIGN KEY (`proyecto_id`) REFERENCES `proyectos` (`id`),
  CONSTRAINT `proyecto_usuarios_ibfk_2` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`),
  CONSTRAINT `proyecto_usuarios_ibfk_3` FOREIGN KEY (`rol_id`) REFERENCES `roles` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `proyecto_usuarios`
--

LOCK TABLES `proyecto_usuarios` WRITE;
/*!40000 ALTER TABLE `proyecto_usuarios` DISABLE KEYS */;
INSERT INTO `proyecto_usuarios` VALUES (1,1,1,2),(2,1,2,3);
/*!40000 ALTER TABLE `proyecto_usuarios` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `proyectos`
--

DROP TABLE IF EXISTS `proyectos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `proyectos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(80) NOT NULL,
  `descripcion` text NOT NULL,
  `usuario_id` int NOT NULL,
  `tipo_industria` varchar(50) NOT NULL DEFAULT 'General',
  PRIMARY KEY (`id`),
  KEY `usuario_id` (`usuario_id`),
  CONSTRAINT `proyectos_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `proyectos`
--

LOCK TABLES `proyectos` WRITE;
/*!40000 ALTER TABLE `proyectos` DISABLE KEYS */;
INSERT INTO `proyectos` VALUES (1,'Invernadero Principal','Monitoreo de temperatura y humedad para el cultivo de tomates.',1,'Agricultura Precision'),(2,'Estación Meteorológica','Recolección de datos ambientales generales en el tejado.',1,'Monitoreo Ambiental');
/*!40000 ALTER TABLE `proyectos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `rol_permisos`
--

DROP TABLE IF EXISTS `rol_permisos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `rol_permisos` (
  `rol_id` int NOT NULL,
  `permiso_id` int NOT NULL,
  PRIMARY KEY (`rol_id`,`permiso_id`),
  KEY `permiso_id` (`permiso_id`),
  CONSTRAINT `rol_permisos_ibfk_1` FOREIGN KEY (`rol_id`) REFERENCES `roles` (`id`),
  CONSTRAINT `rol_permisos_ibfk_2` FOREIGN KEY (`permiso_id`) REFERENCES `permisos` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `rol_permisos`
--

LOCK TABLES `rol_permisos` WRITE;
/*!40000 ALTER TABLE `rol_permisos` DISABLE KEYS */;
/*!40000 ALTER TABLE `rol_permisos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `roles`
--

DROP TABLE IF EXISTS `roles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `roles` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre_rol` varchar(50) NOT NULL,
  `descripcion` text,
  PRIMARY KEY (`id`),
  UNIQUE KEY `nombre_rol` (`nombre_rol`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `roles`
--

LOCK TABLES `roles` WRITE;
/*!40000 ALTER TABLE `roles` DISABLE KEYS */;
INSERT INTO `roles` VALUES (1,'Administrador','Control total del sistema'),(2,'Propietario','Dueño del proyecto con permisos de gestión'),(3,'Observador','Puede ver datos, pero no modificar configuraciones.');
/*!40000 ALTER TABLE `roles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sensores`
--

DROP TABLE IF EXISTS `sensores`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sensores` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(40) NOT NULL,
  `tipo` varchar(40) NOT NULL,
  `fecha_creacion` datetime NOT NULL,
  `habilitado` tinyint(1) NOT NULL,
  `dispositivo_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `dispositivo_id` (`dispositivo_id`),
  CONSTRAINT `sensores_ibfk_1` FOREIGN KEY (`dispositivo_id`) REFERENCES `dispositivos` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sensores`
--

LOCK TABLES `sensores` WRITE;
/*!40000 ALTER TABLE `sensores` DISABLE KEYS */;
INSERT INTO `sensores` VALUES (1,'DHT22-Aire','Temperatura/Humedad','2025-10-14 19:37:43',1,1),(2,'DS18B20-Suelo','Temperatura','2025-10-14 19:37:43',1,1);
/*!40000 ALTER TABLE `sensores` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `unidades_medida`
--

DROP TABLE IF EXISTS `unidades_medida`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `unidades_medida` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(20) NOT NULL,
  `simbolo` varchar(10) NOT NULL,
  `descripcion` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `unidades_medida`
--

LOCK TABLES `unidades_medida` WRITE;
/*!40000 ALTER TABLE `unidades_medida` DISABLE KEYS */;
INSERT INTO `unidades_medida` VALUES (1,'Celsius','°C','Temperatura en grados Celsius'),(2,'Humedad Relativa','%','Porcentaje de humedad'),(3,'Voltios','V','Tensión eléctrica');
/*!40000 ALTER TABLE `unidades_medida` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuarios`
--

DROP TABLE IF EXISTS `usuarios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuarios` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre_usuario` varchar(150) NOT NULL,
  `nombre` varchar(30) NOT NULL,
  `apellido` varchar(30) NOT NULL,
  `email` varchar(254) NOT NULL,
  `contrasena` varchar(128) NOT NULL,
  `activo` tinyint(1) NOT NULL DEFAULT '1',
  `fecha_registro` datetime NOT NULL,
  `ultimo_login` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `nombre_usuario` (`nombre_usuario`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuarios`
--

LOCK TABLES `usuarios` WRITE;
/*!40000 ALTER TABLE `usuarios` DISABLE KEYS */;
INSERT INTO `usuarios` VALUES (1,'admin_user','Iván','Góngora','ivan@ejemplo.com','$2b$12$4pOr6.S0V9pC.I0tfkbFxuujiYLR0/5IjgU.nKj3Cwo2O5QenY2ki',1,'2025-10-14 19:37:43','2025-10-14 19:42:10'),(2,'observador','Ana','Pérez','ana@ejemplo.com','$2b$12$4pOr6.S0V9pC.I0tfkbFxuujiYLR0/5IjgU.nKj3Cwo2O5QenY2ki',1,'2025-10-14 19:37:43',NULL);
/*!40000 ALTER TABLE `usuarios` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `valores`
--

DROP TABLE IF EXISTS `valores`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `valores` (
  `id` int NOT NULL AUTO_INCREMENT,
  `valor` varchar(100) NOT NULL,
  `fecha_hora_lectura` datetime NOT NULL,
  `fecha_dispositivo` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `campo_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `campo_id` (`campo_id`),
  CONSTRAINT `valores_ibfk_1` FOREIGN KEY (`campo_id`) REFERENCES `campos_sensores` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `valores`
--

LOCK TABLES `valores` WRITE;
/*!40000 ALTER TABLE `valores` DISABLE KEYS */;
INSERT INTO `valores` VALUES (1,'29.1','2025-10-14 19:37:43','2025-10-14 19:37:43',1),(2,'66.0','2025-10-14 19:37:43','2025-10-14 19:37:43',2),(3,'22.2','2025-10-14 19:37:43','2025-10-14 19:37:43',3);
/*!40000 ALTER TABLE `valores` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-10-14 20:04:19
