-- MySQL dump 10.13  Distrib 9.5.0, for Win64 (x86_64)
--
-- Host: localhost    Database: post_office
-- ------------------------------------------------------
-- Server version	9.5.0

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
SET @MYSQLDUMP_TEMP_LOG_BIN = @@SESSION.SQL_LOG_BIN;
SET @@SESSION.SQL_LOG_BIN= 0;

--
-- GTID state at the beginning of the backup 
--

SET @@GLOBAL.GTID_PURGED=/*!80000 '+'*/ '50fe6674-e022-11f0-bf7a-3024a93c6e67:1-174';

--
-- Table structure for table `accounts`
--

DROP TABLE IF EXISTS `accounts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `accounts` (
  `acc_no` varchar(15) NOT NULL,
  `name` varchar(100) NOT NULL,
  `address` varchar(255) DEFAULT NULL,
  `mobile` varchar(10) NOT NULL,
  `acc_type` enum('SB','RD','TD') NOT NULL,
  `balance` decimal(12,2) NOT NULL,
  `status` enum('Active','Closed') DEFAULT 'Active',
  PRIMARY KEY (`acc_no`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `accounts`
--

LOCK TABLES `accounts` WRITE;
/*!40000 ALTER TABLE `accounts` DISABLE KEYS */;
INSERT INTO `accounts` VALUES ('0102123875','anubhav','katia tola','9119621379','SB',30500.00,'Active'),('0106566089','anubhav','tareen bahadurganj','9119621379','SB',251466.91,'Active'),('0109764252','saumya','katia tola','9621049512','SB',30800.00,'Active'),('0204389590','saumya','katia tola','9621049512','RD',0.00,'Closed'),('0204915892','anubhav','katia tola','9119621379','RD',0.00,'Closed'),('0209209519','anubhav','tareen bahadurganj','9119621379','RD',0.00,'Closed'),('0303546592','anu','katiya tola','9119621379','TD',100000.00,'Active'),('0304635921','anubhav','katia tola','9119621379','TD',100000.00,'Closed'),('0305212647','anubhav','katia tola','9119621379','TD',100000.00,'Closed'),('0305577145','anubhav','katia tola','9119621379','TD',100000.00,'Closed'),('0305659200','anubhav','kat','9119621379','TD',0.00,'Closed'),('0309350185','anu','katiya tola','9119621379','TD',0.00,'Closed');
/*!40000 ALTER TABLE `accounts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `rd_details`
--

DROP TABLE IF EXISTS `rd_details`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `rd_details` (
  `acc_no` varchar(15) NOT NULL,
  `monthly_amount` decimal(10,2) NOT NULL,
  `months_completed` int DEFAULT '0',
  PRIMARY KEY (`acc_no`),
  CONSTRAINT `rd_details_ibfk_1` FOREIGN KEY (`acc_no`) REFERENCES `accounts` (`acc_no`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `rd_details`
--

LOCK TABLES `rd_details` WRITE;
/*!40000 ALTER TABLE `rd_details` DISABLE KEYS */;
INSERT INTO `rd_details` VALUES ('0204389590',500.00,60),('0204915892',500.00,60),('0209209519',500.00,60);
/*!40000 ALTER TABLE `rd_details` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `transactions`
--

DROP TABLE IF EXISTS `transactions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `transactions` (
  `txn_id` int NOT NULL AUTO_INCREMENT,
  `acc_no` varchar(15) DEFAULT NULL,
  `txn_type` varchar(20) DEFAULT NULL,
  `amount` decimal(10,2) DEFAULT NULL,
  `txn_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`txn_id`),
  KEY `acc_no` (`acc_no`),
  CONSTRAINT `transactions_ibfk_1` FOREIGN KEY (`acc_no`) REFERENCES `accounts` (`acc_no`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `transactions`
--

LOCK TABLES `transactions` WRITE;
/*!40000 ALTER TABLE `transactions` DISABLE KEYS */;
/*!40000 ALTER TABLE `transactions` ENABLE KEYS */;
UNLOCK TABLES;
SET @@SESSION.SQL_LOG_BIN = @MYSQLDUMP_TEMP_LOG_BIN;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-01-10 23:42:00
