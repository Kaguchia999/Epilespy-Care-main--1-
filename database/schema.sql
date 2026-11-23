-- MySQL dump 10.13  Distrib 8.0.43, for Win64 (x86_64)
--
-- Host: localhost    Database: epilepsy_care
-- ------------------------------------------------------
-- Server version	8.0.43

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
-- Current Database: `epilepsy_care`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `epilepsy_care` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

USE `epilepsy_care`;

--
-- Table structure for table `administrator`
--

DROP TABLE IF EXISTS `administrator`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `administrator` (
  `admin_id` int NOT NULL AUTO_INCREMENT,
  `full_name` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `status` varchar(10) NOT NULL DEFAULT 'active',
  PRIMARY KEY (`admin_id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `administrator`
--

LOCK TABLES `administrator` WRITE;
/*!40000 ALTER TABLE `administrator` DISABLE KEYS */;
INSERT INTO `administrator` VALUES (1,'Cynthia Kaguchia','kaguchiacynthia2@gmail.com','$2b$12$m1dZVnSfK3nkfgg5Zt.yROB.GVpBOz98byIBE5whNoErQTfEYeYVK','active'),(2,'Annabel Gacheri','annabelgacheri@gmail.com','$2b$12$luMfwFZvRXZ48MxvCzI.c./h94IRS1Y7jr.i/B1XvYI48NBGFEHuW','active');
/*!40000 ALTER TABLE `administrator` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auditlog`
--

DROP TABLE IF EXISTS `auditlog`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auditlog` (
  `audit_id` int NOT NULL AUTO_INCREMENT,
  `admin_id` int NOT NULL,
  `action` varchar(100) NOT NULL,
  `target` varchar(100) DEFAULT NULL,
  `logged_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`audit_id`),
  KEY `admin_id` (`admin_id`),
  CONSTRAINT `auditlog_ibfk_1` FOREIGN KEY (`admin_id`) REFERENCES `administrator` (`admin_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auditlog`
--

LOCK TABLES `auditlog` WRITE;
/*!40000 ALTER TABLE `auditlog` DISABLE KEYS */;
/*!40000 ALTER TABLE `auditlog` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `caregiver`
--

DROP TABLE IF EXISTS `caregiver`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `caregiver` (
  `caregiver_id` int NOT NULL AUTO_INCREMENT,
  `full_name` varchar(100) NOT NULL,
  `phone` varchar(15) DEFAULT NULL,
  `email` varchar(100) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `status` varchar(10) NOT NULL DEFAULT 'active',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`caregiver_id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `caregiver`
--

LOCK TABLES `caregiver` WRITE;
/*!40000 ALTER TABLE `caregiver` DISABLE KEYS */;
/*!40000 ALTER TABLE `caregiver` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `caregivercontact`
--

DROP TABLE IF EXISTS `caregivercontact`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `caregivercontact` (
  `contact_id` int NOT NULL AUTO_INCREMENT,
  `patient_id` int NOT NULL,
  `contact_name` varchar(100) NOT NULL,
  `phone` varchar(15) NOT NULL,
  `relationship` varchar(30) DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`contact_id`),
  KEY `patient_id` (`patient_id`),
  CONSTRAINT `caregivercontact_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patient` (`patient_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `caregivercontact`
--

LOCK TABLES `caregivercontact` WRITE;
/*!40000 ALTER TABLE `caregivercontact` DISABLE KEYS */;
/*!40000 ALTER TABLE `caregivercontact` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `consultationnote`
--

DROP TABLE IF EXISTS `consultationnote`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `consultationnote` (
  `note_id` int NOT NULL AUTO_INCREMENT,
  `summary_id` int NOT NULL,
  `doctor_id` int NOT NULL,
  `note_text` text NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`note_id`),
  KEY `summary_id` (`summary_id`),
  KEY `doctor_id` (`doctor_id`),
  CONSTRAINT `consultationnote_ibfk_1` FOREIGN KEY (`summary_id`) REFERENCES `consultationsummary` (`summary_id`),
  CONSTRAINT `consultationnote_ibfk_2` FOREIGN KEY (`doctor_id`) REFERENCES `doctor` (`doctor_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `consultationnote`
--

LOCK TABLES `consultationnote` WRITE;
/*!40000 ALTER TABLE `consultationnote` DISABLE KEYS */;
/*!40000 ALTER TABLE `consultationnote` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `consultationsummary`
--

DROP TABLE IF EXISTS `consultationsummary`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `consultationsummary` (
  `summary_id` int NOT NULL AUTO_INCREMENT,
  `patient_id` int NOT NULL,
  `period_start` date NOT NULL,
  `period_end` date NOT NULL,
  `adherence_rate` decimal(5,2) DEFAULT NULL,
  `file_path` varchar(255) DEFAULT NULL,
  `generated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`summary_id`),
  KEY `patient_id` (`patient_id`),
  CONSTRAINT `consultationsummary_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patient` (`patient_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `consultationsummary`
--

LOCK TABLES `consultationsummary` WRITE;
/*!40000 ALTER TABLE `consultationsummary` DISABLE KEYS */;
/*!40000 ALTER TABLE `consultationsummary` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `doctor`
--

DROP TABLE IF EXISTS `doctor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `doctor` (
  `doctor_id` int NOT NULL AUTO_INCREMENT,
  `full_name` varchar(100) NOT NULL,
  `EMAIL` varchar(100) NOT NULL,
  `password_hash` varchar(100) NOT NULL,
  `registration_no` varchar(30) NOT NULL,
  `facility` varchar(100) DEFAULT NULL,
  `approval_status` varchar(12) NOT NULL DEFAULT 'pending',
  `approved_by` int DEFAULT NULL,
  `approved_at` datetime DEFAULT NULL,
  PRIMARY KEY (`doctor_id`),
  UNIQUE KEY `EMAIL` (`EMAIL`),
  UNIQUE KEY `registration_no` (`registration_no`),
  KEY `approved_by` (`approved_by`),
  CONSTRAINT `doctor_ibfk_1` FOREIGN KEY (`approved_by`) REFERENCES `administrator` (`admin_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `doctor`
--

LOCK TABLES `doctor` WRITE;
/*!40000 ALTER TABLE `doctor` DISABLE KEYS */;
/*!40000 ALTER TABLE `doctor` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `doselog`
--

DROP TABLE IF EXISTS `doselog`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `doselog` (
  `dose_id` int NOT NULL AUTO_INCREMENT,
  `schedule_id` int NOT NULL,
  `dose_date` date NOT NULL,
  `status` varchar(10) NOT NULL,
  `logged_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`dose_id`),
  KEY `schedule_id` (`schedule_id`),
  CONSTRAINT `doselog_ibfk_1` FOREIGN KEY (`schedule_id`) REFERENCES `reminderschedule` (`schedule_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `doselog`
--

LOCK TABLES `doselog` WRITE;
/*!40000 ALTER TABLE `doselog` DISABLE KEYS */;
/*!40000 ALTER TABLE `doselog` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `errorlog`
--

DROP TABLE IF EXISTS `errorlog`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `errorlog` (
  `error_id` int NOT NULL AUTO_INCREMENT,
  `module` varchar(50) NOT NULL,
  `message` text NOT NULL,
  `logged_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`error_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `errorlog`
--

LOCK TABLES `errorlog` WRITE;
/*!40000 ALTER TABLE `errorlog` DISABLE KEYS */;
/*!40000 ALTER TABLE `errorlog` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `helpmessagetemplate`
--

DROP TABLE IF EXISTS `helpmessagetemplate`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `helpmessagetemplate` (
  `template_id` int NOT NULL AUTO_INCREMENT,
  `template_text` text NOT NULL,
  `is_current` tinyint(1) NOT NULL DEFAULT '1',
  `updated_by` int NOT NULL,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`template_id`),
  KEY `updated_by` (`updated_by`),
  CONSTRAINT `helpmessagetemplate_ibfk_1` FOREIGN KEY (`updated_by`) REFERENCES `administrator` (`admin_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `helpmessagetemplate`
--

LOCK TABLES `helpmessagetemplate` WRITE;
/*!40000 ALTER TABLE `helpmessagetemplate` DISABLE KEYS */;
/*!40000 ALTER TABLE `helpmessagetemplate` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `helprequest`
--

DROP TABLE IF EXISTS `helprequest`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `helprequest` (
  `request_id` int NOT NULL AUTO_INCREMENT,
  `patient_id` int NOT NULL,
  `contact_id` int NOT NULL,
  `template_id` int NOT NULL,
  `requested_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `status` varchar(10) NOT NULL DEFAULT 'pending',
  `failure_reason` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`request_id`),
  KEY `patient_id` (`patient_id`),
  KEY `contact_id` (`contact_id`),
  KEY `template_id` (`template_id`),
  CONSTRAINT `helprequest_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patient` (`patient_id`),
  CONSTRAINT `helprequest_ibfk_2` FOREIGN KEY (`contact_id`) REFERENCES `caregivercontact` (`contact_id`),
  CONSTRAINT `helprequest_ibfk_3` FOREIGN KEY (`template_id`) REFERENCES `helpmessagetemplate` (`template_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `helprequest`
--

LOCK TABLES `helprequest` WRITE;
/*!40000 ALTER TABLE `helprequest` DISABLE KEYS */;
/*!40000 ALTER TABLE `helprequest` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `helprequestacknowledgement`
--

DROP TABLE IF EXISTS `helprequestacknowledgement`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `helprequestacknowledgement` (
  `ack_id` int NOT NULL AUTO_INCREMENT,
  `request_id` int NOT NULL,
  `caregiver_id` int NOT NULL,
  `acknowledged_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`ack_id`),
  KEY `request_id` (`request_id`),
  KEY `caregiver_id` (`caregiver_id`),
  CONSTRAINT `helprequestacknowledgement_ibfk_1` FOREIGN KEY (`request_id`) REFERENCES `helprequest` (`request_id`),
  CONSTRAINT `helprequestacknowledgement_ibfk_2` FOREIGN KEY (`caregiver_id`) REFERENCES `caregiver` (`caregiver_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `helprequestacknowledgement`
--

LOCK TABLES `helprequestacknowledgement` WRITE;
/*!40000 ALTER TABLE `helprequestacknowledgement` DISABLE KEYS */;
/*!40000 ALTER TABLE `helprequestacknowledgement` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `locksetting`
--

DROP TABLE IF EXISTS `locksetting`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `locksetting` (
  `lock_id` int NOT NULL AUTO_INCREMENT,
  `patient_id` int NOT NULL,
  `lock_type` varchar(10) NOT NULL DEFAULT 'none',
  `pin_hash` varchar(255) DEFAULT NULL,
  `biometric_enabled` tinyint(1) NOT NULL DEFAULT '0',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`lock_id`),
  UNIQUE KEY `patient_id` (`patient_id`),
  CONSTRAINT `locksetting_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patient` (`patient_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `locksetting`
--

LOCK TABLES `locksetting` WRITE;
/*!40000 ALTER TABLE `locksetting` DISABLE KEYS */;
/*!40000 ALTER TABLE `locksetting` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `medication`
--

DROP TABLE IF EXISTS `medication`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `medication` (
  `med_id` int NOT NULL AUTO_INCREMENT,
  `patient_id` int NOT NULL,
  `ref_id` int DEFAULT NULL,
  `medication_name` varchar(100) NOT NULL,
  `strength` varchar(30) DEFAULT NULL,
  `dose_amount` varchar(30) DEFAULT NULL,
  `instructions` text,
  `is_active` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`med_id`),
  KEY `patient_id` (`patient_id`),
  KEY `ref_id` (`ref_id`),
  CONSTRAINT `medication_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patient` (`patient_id`),
  CONSTRAINT `medication_ibfk_2` FOREIGN KEY (`ref_id`) REFERENCES `medicationreference` (`ref_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `medication`
--

LOCK TABLES `medication` WRITE;
/*!40000 ALTER TABLE `medication` DISABLE KEYS */;
/*!40000 ALTER TABLE `medication` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `medicationreference`
--

DROP TABLE IF EXISTS `medicationreference`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `medicationreference` (
  `ref_id` int NOT NULL AUTO_INCREMENT,
  `generic_name` varchar(100) NOT NULL,
  `common_form` varchar(30) DEFAULT NULL,
  `typical_unit` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`ref_id`),
  UNIQUE KEY `generic_name` (`generic_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `medicationreference`
--

LOCK TABLES `medicationreference` WRITE;
/*!40000 ALTER TABLE `medicationreference` DISABLE KEYS */;
/*!40000 ALTER TABLE `medicationreference` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `patient`
--

DROP TABLE IF EXISTS `patient`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `patient` (
  `patient_id` int NOT NULL AUTO_INCREMENT,
  `full_name` varchar(100) NOT NULL,
  `phone` varchar(15) DEFAULT NULL,
  `email` varchar(100) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `status` varchar(10) NOT NULL DEFAULT 'active',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`patient_id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `patient`
--

LOCK TABLES `patient` WRITE;
/*!40000 ALTER TABLE `patient` DISABLE KEYS */;
/*!40000 ALTER TABLE `patient` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `patientcaregiverlink`
--

DROP TABLE IF EXISTS `patientcaregiverlink`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `patientcaregiverlink` (
  `link_id` int NOT NULL AUTO_INCREMENT,
  `patient_id` int NOT NULL,
  `caregiver_id` int NOT NULL,
  `can_view_dose_status` tinyint(1) NOT NULL DEFAULT '0',
  `status` varchar(10) NOT NULL DEFAULT 'pending',
  `invited_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`link_id`),
  UNIQUE KEY `patient_id` (`patient_id`,`caregiver_id`),
  KEY `caregiver_id` (`caregiver_id`),
  CONSTRAINT `patientcaregiverlink_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patient` (`patient_id`),
  CONSTRAINT `patientcaregiverlink_ibfk_2` FOREIGN KEY (`caregiver_id`) REFERENCES `caregiver` (`caregiver_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `patientcaregiverlink`
--

LOCK TABLES `patientcaregiverlink` WRITE;
/*!40000 ALTER TABLE `patientcaregiverlink` DISABLE KEYS */;
/*!40000 ALTER TABLE `patientcaregiverlink` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `reminderschedule`
--

DROP TABLE IF EXISTS `reminderschedule`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `reminderschedule` (
  `schedule_id` int NOT NULL AUTO_INCREMENT,
  `med_id` int NOT NULL,
  `reminder_time` time NOT NULL,
  `days_of_the_week` varchar(20) DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`schedule_id`),
  KEY `med_id` (`med_id`),
  CONSTRAINT `reminderschedule_ibfk_1` FOREIGN KEY (`med_id`) REFERENCES `medication` (`med_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `reminderschedule`
--

LOCK TABLES `reminderschedule` WRITE;
/*!40000 ALTER TABLE `reminderschedule` DISABLE KEYS */;
/*!40000 ALTER TABLE `reminderschedule` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `seizurerecord`
--

DROP TABLE IF EXISTS `seizurerecord`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `seizurerecord` (
  `seizure_id` int NOT NULL AUTO_INCREMENT,
  `patient_id` int NOT NULL,
  `seizure_datetime` datetime NOT NULL,
  `duration_secs` int DEFAULT NULL,
  `seizure_type` varchar(50) DEFAULT NULL,
  `notes` text,
  PRIMARY KEY (`seizure_id`),
  KEY `patient_id` (`patient_id`),
  CONSTRAINT `seizurerecord_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patient` (`patient_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `seizurerecord`
--

LOCK TABLES `seizurerecord` WRITE;
/*!40000 ALTER TABLE `seizurerecord` DISABLE KEYS */;
/*!40000 ALTER TABLE `seizurerecord` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sharingconsent`
--

DROP TABLE IF EXISTS `sharingconsent`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sharingconsent` (
  `consent_id` int NOT NULL AUTO_INCREMENT,
  `summary_id` int NOT NULL,
  `doctor_id` int NOT NULL,
  `shared_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `revoked_at` datetime DEFAULT NULL,
  PRIMARY KEY (`consent_id`),
  KEY `summary_id` (`summary_id`),
  KEY `doctor_id` (`doctor_id`),
  CONSTRAINT `sharingconsent_ibfk_1` FOREIGN KEY (`summary_id`) REFERENCES `consultationsummary` (`summary_id`),
  CONSTRAINT `sharingconsent_ibfk_2` FOREIGN KEY (`doctor_id`) REFERENCES `doctor` (`doctor_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sharingconsent`
--

LOCK TABLES `sharingconsent` WRITE;
/*!40000 ALTER TABLE `sharingconsent` DISABLE KEYS */;
/*!40000 ALTER TABLE `sharingconsent` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sideeffectrecord`
--

DROP TABLE IF EXISTS `sideeffectrecord`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sideeffectrecord` (
  `side_effect_id` int NOT NULL AUTO_INCREMENT,
  `patient_id` int NOT NULL,
  `med_id` int NOT NULL,
  `effect_datetime` datetime NOT NULL,
  `effect` varchar(100) NOT NULL,
  `severity` int DEFAULT NULL,
  `notes` text,
  PRIMARY KEY (`side_effect_id`),
  KEY `patient_id` (`patient_id`),
  KEY `med_id` (`med_id`),
  CONSTRAINT `sideeffectrecord_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patient` (`patient_id`),
  CONSTRAINT `sideeffectrecord_ibfk_2` FOREIGN KEY (`med_id`) REFERENCES `medication` (`med_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sideeffectrecord`
--

LOCK TABLES `sideeffectrecord` WRITE;
/*!40000 ALTER TABLE `sideeffectrecord` DISABLE KEYS */;
/*!40000 ALTER TABLE `sideeffectrecord` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `symptomrecord`
--

DROP TABLE IF EXISTS `symptomrecord`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `symptomrecord` (
  `symptom_id` int NOT NULL AUTO_INCREMENT,
  `patient_id` int NOT NULL,
  `symptom_datetime` datetime NOT NULL,
  `symptom` varchar(100) NOT NULL,
  `severity` int DEFAULT NULL,
  `notes` text,
  PRIMARY KEY (`symptom_id`),
  KEY `patient_id` (`patient_id`),
  CONSTRAINT `symptomrecord_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patient` (`patient_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `symptomrecord`
--

LOCK TABLES `symptomrecord` WRITE;
/*!40000 ALTER TABLE `symptomrecord` DISABLE KEYS */;
/*!40000 ALTER TABLE `symptomrecord` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-11-23 19:36:25
