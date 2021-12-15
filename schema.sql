DROP TABLE IF EXISTS `orders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `orders` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `uid` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `pair` varchar(16) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `fees` float(16,6) DEFAULT NULL,
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
  `pct` float(16,6) DEFAULT NULL,
  `cap_pct` float(16,6) DEFAULT NULL,
  `credits` float(16,6) DEFAULT NULL,
  `netcredits` float(16,6) DEFAULT NULL,
  `runtot` float(16,6) DEFAULT NULL,
  `runtotnet` float(16,6) DEFAULT NULL,
  `bsuid` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `fintot` float DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=279718 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
