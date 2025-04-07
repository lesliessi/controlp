-- MySQL dump 10.13  Distrib 8.0.36, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: frielec
-- ------------------------------------------------------
-- Server version	8.0.37

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `cliente`
--

DROP TABLE IF EXISTS `cliente`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cliente` (
  `cedula` int NOT NULL,
  PRIMARY KEY (`cedula`),
  CONSTRAINT `persona_cedula_cliente` FOREIGN KEY (`cedula`) REFERENCES `persona` (`cedula`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cliente`
--

LOCK TABLES `cliente` WRITE;
/*!40000 ALTER TABLE `cliente` DISABLE KEYS */;
INSERT INTO `cliente` VALUES (22222222);
/*!40000 ALTER TABLE `cliente` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cliente_realiza_pedido`
--

DROP TABLE IF EXISTS `cliente_realiza_pedido`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cliente_realiza_pedido` (
  `cedula` int NOT NULL,
  `codigo_pedido` int NOT NULL,
  `fecha_pedido` date NOT NULL,
  KEY `cliente_cedula_cliente_realiza_pedido` (`cedula`),
  KEY `pedido_codigo_pedido_cliente_realiza_pedido` (`codigo_pedido`),
  CONSTRAINT `cliente_cedula_cliente_realiza_pedido` FOREIGN KEY (`cedula`) REFERENCES `cliente` (`cedula`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `pedido_codigo_pedido_cliente_realiza_pedido` FOREIGN KEY (`codigo_pedido`) REFERENCES `pedido` (`codigo_pedido`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cliente_realiza_pedido`
--

LOCK TABLES `cliente_realiza_pedido` WRITE;
/*!40000 ALTER TABLE `cliente_realiza_pedido` DISABLE KEYS */;
/*!40000 ALTER TABLE `cliente_realiza_pedido` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `direccion`
--

DROP TABLE IF EXISTS `direccion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `direccion` (
  `codigo_direccion` int NOT NULL AUTO_INCREMENT,
  `calle` varchar(50) NOT NULL,
  `sector` varchar(50) NOT NULL,
  `numero_casa` int DEFAULT NULL,
  `municipio` varchar(50) NOT NULL,
  `estado` varchar(50) NOT NULL,
  PRIMARY KEY (`codigo_direccion`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `direccion`
--

LOCK TABLES `direccion` WRITE;
/*!40000 ALTER TABLE `direccion` DISABLE KEYS */;
INSERT INTO `direccion` VALUES (1,'Ezequiel Zamora','Las Arepas',56,'Guanipa','Anzoátegui'),(2,'Bolívar','Simón Bolívar',10,'Anaco','Anzoátegui'),(3,'Zulia','Ezequiel Zamora',18,'San José de Guanipa','Anzoátegui');
/*!40000 ALTER TABLE `direccion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `empleado`
--

DROP TABLE IF EXISTS `empleado`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `empleado` (
  `cedula` int NOT NULL,
  `cargo` varchar(50) DEFAULT NULL,
  `tipo` varchar(50) NOT NULL,
  PRIMARY KEY (`cedula`),
  CONSTRAINT `persona_cedula_empleado` FOREIGN KEY (`cedula`) REFERENCES `persona` (`cedula`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `empleado`
--

LOCK TABLES `empleado` WRITE;
/*!40000 ALTER TABLE `empleado` DISABLE KEYS */;
INSERT INTO `empleado` VALUES (5545156,'Técnico jefe','Técnico'),(10937317,'Vicepresidente','Administrativo'),(11222333,'','técnico'),(12662744,'','tecnico'),(15654321,'Economista','tecnico'),(17796935,'Asistente','Técnico'),(19951456,'Líder','Rapero'),(20554221,'','tecnico'),(30131981,NULL,'técnico'),(30420965,'','Técnico'),(30523856,'NEGRO','GATO'),(34137567,'Contadora','Administrativo'),(154878965,'','ssghsg');
/*!40000 ALTER TABLE `empleado` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `historial`
--

DROP TABLE IF EXISTS `historial`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `historial` (
  `codigo_historial` int NOT NULL AUTO_INCREMENT,
  `ultima_sesion` datetime NOT NULL,
  PRIMARY KEY (`codigo_historial`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `historial`
--

LOCK TABLES `historial` WRITE;
/*!40000 ALTER TABLE `historial` DISABLE KEYS */;
/*!40000 ALTER TABLE `historial` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pedido`
--

DROP TABLE IF EXISTS `pedido`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pedido` (
  `codigo_pedido` int NOT NULL AUTO_INCREMENT,
  `cedula_empleado` int NOT NULL,
  `servicio` varchar(200) NOT NULL,
  `precio` double NOT NULL,
  PRIMARY KEY (`codigo_pedido`),
  KEY `empleado_cedula_pedido` (`cedula_empleado`),
  CONSTRAINT `empleado_cedula_pedido` FOREIGN KEY (`cedula_empleado`) REFERENCES `empleado` (`cedula`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pedido`
--

LOCK TABLES `pedido` WRITE;
/*!40000 ALTER TABLE `pedido` DISABLE KEYS */;
INSERT INTO `pedido` VALUES (2,30131981,'Mantenimiento preventivo a aire acondicionado',20);
/*!40000 ALTER TABLE `pedido` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pedido_corresponde_a_servicio`
--

DROP TABLE IF EXISTS `pedido_corresponde_a_servicio`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pedido_corresponde_a_servicio` (
  `codigo_pedido` int NOT NULL,
  `codigo_servicio` int NOT NULL,
  KEY `pedido_codigo_pedido_pedido_corresponde_a_servico` (`codigo_pedido`),
  KEY `servicio_codigo_servicio_pedido_corresponde_a_servicio` (`codigo_servicio`),
  CONSTRAINT `pedido_codigo_pedido_pedido_corresponde_a_servico` FOREIGN KEY (`codigo_pedido`) REFERENCES `pedido` (`codigo_pedido`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `servicio_codigo_servicio_pedido_corresponde_a_servicio` FOREIGN KEY (`codigo_servicio`) REFERENCES `servicio` (`codigo_servicio`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pedido_corresponde_a_servicio`
--

LOCK TABLES `pedido_corresponde_a_servicio` WRITE;
/*!40000 ALTER TABLE `pedido_corresponde_a_servicio` DISABLE KEYS */;
/*!40000 ALTER TABLE `pedido_corresponde_a_servicio` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `persona`
--

DROP TABLE IF EXISTS `persona`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `persona` (
  `cedula` int NOT NULL,
  `nombre` varchar(50) NOT NULL,
  `apellido` varchar(50) NOT NULL,
  `telefono` bigint NOT NULL,
  PRIMARY KEY (`cedula`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `persona`
--

LOCK TABLES `persona` WRITE;
/*!40000 ALTER TABLE `persona` DISABLE KEYS */;
INSERT INTO `persona` VALUES (1234567,'Sesu','Mude',4148321345),(1441212,'Sesu','Mude',4149291111),(5545156,'David','Pan',4147898526),(7854123,'upa','papa',4125698745),(8776545,'Mingyu','Kim',4248569874),(10554231,'Michael','Jason',4149228771),(10937317,'Wusven','Ohana',4147815911),(11222333,'Kairi','Ilvin',4141120311),(12313121,'Irel','King',4142211234),(12345678,'María','Pérez',4161234567),(12500300,'Dario','Sanche',4145334212),(12662744,'Mario','Perez',4124432112),(15654321,'Jei','Balvin',4122314567),(17796935,'Federico','Rodríguez',4145254789),(19951456,'Seungcheol','Choi',4147895412),(20500300,'Irel','King',4148229167),(20512650,'Nacho','Frito',4142211224),(20545820,'Wenas','Taldes',4165826090),(20554221,'Fredy','Navarro',4123321298),(20555444,'Viktor','Gome',4142221166),(22222222,'Gabriel','Ramírez',12332434252),(28772621,'Viktor','Gome',4123214233),(30131981,'Bernardo','Kim',4248282920),(30320761,'Taco','Mora',4127228193),(30420965,'Leslie','Rodríguez',4248665971),(30523856,'jijI','GATO',4145789652),(34137567,'Sofia','Rodríguez',4144524523),(58968963,'María','Pérez',4127897896),(154878965,'ssg','shshs',1189248814);
/*!40000 ALTER TABLE `persona` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `persona_tiene_direccion`
--

DROP TABLE IF EXISTS `persona_tiene_direccion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `persona_tiene_direccion` (
  `cedula` int NOT NULL,
  `codigo_direccion` int NOT NULL,
  KEY `persona_cedula_persona_tiene_direccion` (`cedula`),
  KEY `direccion_codigo_direccion_persona_tiene_direccion` (`codigo_direccion`),
  CONSTRAINT `direccion_codigo_direccion_persona_tiene_direccion` FOREIGN KEY (`codigo_direccion`) REFERENCES `direccion` (`codigo_direccion`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `persona_cedula_persona_tiene_direccion` FOREIGN KEY (`cedula`) REFERENCES `persona` (`cedula`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `persona_tiene_direccion`
--

LOCK TABLES `persona_tiene_direccion` WRITE;
/*!40000 ALTER TABLE `persona_tiene_direccion` DISABLE KEYS */;
INSERT INTO `persona_tiene_direccion` VALUES (22222222,2),(12345678,1),(58968963,3);
/*!40000 ALTER TABLE `persona_tiene_direccion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `rol`
--

DROP TABLE IF EXISTS `rol`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `rol` (
  `codigo_rol` int NOT NULL,
  `descripcion` varchar(50) NOT NULL,
  PRIMARY KEY (`codigo_rol`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `rol`
--

LOCK TABLES `rol` WRITE;
/*!40000 ALTER TABLE `rol` DISABLE KEYS */;
INSERT INTO `rol` VALUES (1,'administrador'),(2,'usuario regular');
/*!40000 ALTER TABLE `rol` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `servicio`
--

DROP TABLE IF EXISTS `servicio`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `servicio` (
  `codigo_servicio` int NOT NULL AUTO_INCREMENT,
  `tipo` varchar(50) NOT NULL,
  `descripcion` varchar(50) NOT NULL,
  PRIMARY KEY (`codigo_servicio`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `servicio`
--

LOCK TABLES `servicio` WRITE;
/*!40000 ALTER TABLE `servicio` DISABLE KEYS */;
/*!40000 ALTER TABLE `servicio` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuario`
--

DROP TABLE IF EXISTS `usuario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuario` (
  `codigo_usuario` int NOT NULL AUTO_INCREMENT,
  `cedula` int NOT NULL,
  `usuario` varchar(50) NOT NULL,
  `respuesta_seguridad` varchar(50) NOT NULL,
  `rol` int NOT NULL,
  `contraseña` blob,
  PRIMARY KEY (`codigo_usuario`),
  KEY `empleado_cedula_usuario` (`cedula`),
  CONSTRAINT `empleado_cedula_usuario` FOREIGN KEY (`cedula`) REFERENCES `empleado` (`cedula`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuario`
--

LOCK TABLES `usuario` WRITE;
/*!40000 ALTER TABLE `usuario` DISABLE KEYS */;
INSERT INTO `usuario` VALUES (2,30131981,'berdardokim','amarillo',2,_binary '123456'),(9,11222333,'Kairilvi','rojo',2,_binary '123'),(10,15654321,'Jeibalvi','verde',2,_binary '123456'),(11,34137567,'sofia093','azul',2,_binary '123456'),(12,5545156,'david78','gris',2,_binary '123456'),(14,19951456,'scoups','rojo',2,_binary '$2b$12$k2MVE22dJ.b3Is1HCbFyzOtCkXfJ9tIFTQzWELOpq3rwMyGHg9EDS'),(15,17796935,'kiko05','verde',2,_binary '$2b$12$BZDGluHIltEYSiGagCNe/etVdOJx3Mgiy8XaiNth2o3qiTYCPCfuS'),(16,30523856,'jiji','negro',2,_binary '$2b$12$lGBuQzzc6pb/lIQJT7CzZOIUPKeNOr9LgYuLm5daheOi0sdSVhfzq'),(17,154878965,'bodoque','rojo',2,_binary '$2b$12$jOXe45JMlbFEgpcbBA1it.FQdWc8.I9gyRnFhoavqE/f9fcNBV2je'),(18,10937317,'admin','vinotinto',1,_binary '$2b$12$2mNdRtVofdqSzRVxQwZtNueXu1lqRLHNjZUJq83Lq/lQxmvb1uOau'),(19,30420965,'leslie176','verde',2,_binary '$2b$12$KloQtoqc2tTxeQr4fxmxJejy0sT/5aUoPKaGp2udmkTYwPaymRgrS');
/*!40000 ALTER TABLE `usuario` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuario_genera_historial`
--

DROP TABLE IF EXISTS `usuario_genera_historial`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuario_genera_historial` (
  `codigo_historial` int NOT NULL,
  `codigo_usuario` int NOT NULL,
  KEY `historial_codigo_historial_usuario_genera_historial` (`codigo_historial`),
  KEY `usuario_codigo_usuario_usuario_genera_historial` (`codigo_usuario`),
  CONSTRAINT `historial_codigo_historial_usuario_genera_historial` FOREIGN KEY (`codigo_historial`) REFERENCES `historial` (`codigo_historial`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `usuario_codigo_usuario_usuario_genera_historial` FOREIGN KEY (`codigo_usuario`) REFERENCES `usuario` (`codigo_usuario`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuario_genera_historial`
--

LOCK TABLES `usuario_genera_historial` WRITE;
/*!40000 ALTER TABLE `usuario_genera_historial` DISABLE KEYS */;
/*!40000 ALTER TABLE `usuario_genera_historial` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuario_tiene_rol`
--

DROP TABLE IF EXISTS `usuario_tiene_rol`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuario_tiene_rol` (
  `codigo_rol` int NOT NULL,
  `codigo_usuario` int NOT NULL,
  KEY `rol_codigo_rol_usuario_tiene_rol` (`codigo_rol`),
  KEY `usuario_codigo_usuario_usuario_tiene_rol` (`codigo_usuario`),
  CONSTRAINT `rol_codigo_rol_usuario_tiene_rol` FOREIGN KEY (`codigo_rol`) REFERENCES `rol` (`codigo_rol`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `usuario_codigo_usuario_usuario_tiene_rol` FOREIGN KEY (`codigo_usuario`) REFERENCES `usuario` (`codigo_usuario`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuario_tiene_rol`
--

LOCK TABLES `usuario_tiene_rol` WRITE;
/*!40000 ALTER TABLE `usuario_tiene_rol` DISABLE KEYS */;
INSERT INTO `usuario_tiene_rol` VALUES (2,2),(2,9),(2,10),(2,11),(2,12);
/*!40000 ALTER TABLE `usuario_tiene_rol` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-08-12 10:02:44
