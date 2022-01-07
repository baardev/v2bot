-- MariaDB dump 10.19  Distrib 10.6.5-MariaDB, for Linux (x86_64)
--
-- Host: localhost    Database: jmcap
-- ------------------------------------------------------
-- Server version	10.6.5-MariaDB-log

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `orders`
--

DROP TABLE IF EXISTS `orders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `orders` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `uid` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `pair` varchar(16) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `fees` float(16,6) NOT NULL DEFAULT 0.000000,
  `price` float(16,6) DEFAULT NULL,
  `stop_price` float(16,6) DEFAULT NULL,
  `upper_stop_price` float(16,6) DEFAULT NULL,
  `size` float(16,6) DEFAULT NULL,
  `funds` float(16,6) DEFAULT NULL,
  `record_time` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `order_time` datetime DEFAULT NULL,
  `side` varchar(16) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `type` varchar(16) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `state` varchar(16) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `session` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT '',
  `pct` float(16,6) NOT NULL DEFAULT 0.000000,
  `cap_pct` float(16,6) NOT NULL DEFAULT 0.000000,
  `credits` float(16,6) DEFAULT NULL,
  `netcredits` float(16,6) DEFAULT NULL,
  `runtot` float(16,6) DEFAULT NULL,
  `runtotnet` float(16,6) DEFAULT NULL,
  `bsuid` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `fintot` float(16,6) DEFAULT NULL,
  `mxint` float(16,6) NOT NULL DEFAULT 0.000000,
  `mxinttot` float(16,6) NOT NULL DEFAULT 0.000000,
  `SL` char(1) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `limit_price` float(16,6) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_fees` (`fees`),
  KEY `ix_price` (`price`),
  KEY `ix_size` (`size`),
  KEY `ix_record_time` (`record_time`),
  KEY `ix_order_time` (`order_time`),
  KEY `ix_funds` (`funds`),
  KEY `ix_side` (`side`),
  KEY `ix_session` (`session`),
  KEY `ix_credits` (`credits`),
  KEY `ix_netcredits` (`netcredits`),
  KEY `ix_runtot` (`runtot`),
  KEY `ix_runtotnet` (`runtotnet`),
  KEY `ix_bsuid` (`bsuid`),
  KEY `ix_fintot` (`fintot`),
  KEY `ix_uid` (`uid`),
  KEY `ix_pct` (`pct`),
  KEY `ix_mxint` (`mxint`),
  KEY `ix_mxinttot` (`mxinttot`),
  KEY `ix_SL` (`SL`)
) ENGINE=InnoDB AUTO_INCREMENT=6000 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orders`
--

LOCK TABLES `orders` WRITE;
/*!40000 ALTER TABLE `orders` DISABLE KEYS */;
/*!40000 ALTER TABLE `orders` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `trans`
--

DROP TABLE IF EXISTS `trans`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `trans` (
  `name` varchar(32) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '0',
  `symbol` varchar(8) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '0',
  `priceUsd` float NOT NULL DEFAULT 0,
  `lastUpdated` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `jsecs` float(15,0) DEFAULT NULL,
  PRIMARY KEY (`symbol`,`lastUpdated`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `trans`
--

LOCK TABLES `trans` WRITE;
/*!40000 ALTER TABLE `trans` DISABLE KEYS */;
/*!40000 ALTER TABLE `trans` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2022-01-07 12:30:18
