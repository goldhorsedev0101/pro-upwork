-- --------------------------------------------------------
-- Host:                         127.0.0.1
-- Server Version:               10.3.28-MariaDB - mariadb.org binary distribution
-- Server Betriebssystem:        Win64
-- HeidiSQL Version:             11.0.0.5919
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;


-- Exportiere Datenbank Struktur für stockdb_akramluna
CREATE DATABASE IF NOT EXISTS `stockdb_akramluna` /*!40100 DEFAULT CHARACTER SET latin1 */;
USE `stockdb_akramluna`;

-- Exportiere Struktur von Tabelle stockdb_akramluna.stockdailydata
CREATE TABLE IF NOT EXISTS `stockdailydata` (
  `ticker` varchar(50) NOT NULL,
  `dateMeasure` date NOT NULL,
  `ev` float DEFAULT NULL,
  `evToEbit` float DEFAULT NULL,
  `evToEbitda` float DEFAULT NULL,
  `marketCap` float DEFAULT NULL,
  `pbRatio` float DEFAULT NULL,
  `peRatio` float DEFAULT NULL,
  `psRatio` float DEFAULT NULL,
  PRIMARY KEY (`ticker`,`dateMeasure`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Daten Export vom Benutzer nicht ausgewählt

-- Exportiere Struktur von Tabelle stockdb_akramluna.stockfinancials
CREATE TABLE IF NOT EXISTS `stockfinancials` (
  `ticker` varchar(50) NOT NULL,
  `dateCal` date NOT NULL,
  `dateReport` date DEFAULT NULL,
  `price` float DEFAULT NULL,
  `netinc` bigint(20) DEFAULT NULL,
  `marketcap` bigint(20) DEFAULT NULL,
  `assets` bigint(20) DEFAULT NULL,
  `capex` bigint(20) DEFAULT NULL,
  `cashneq` bigint(20) DEFAULT NULL,
  `currentratio` float DEFAULT NULL,
  `debt` bigint(20) DEFAULT NULL,
  `ebit` bigint(20) DEFAULT NULL,
  `ebitda` bigint(20) DEFAULT NULL,
  `ebitdamargin` float DEFAULT NULL,
  `eps` float DEFAULT NULL,
  `equity` bigint(20) DEFAULT NULL,
  `ev` bigint(20) DEFAULT NULL,
  `evebit` float DEFAULT NULL,
  `evebidta` float DEFAULT NULL,
  `fcf` bigint(20) DEFAULT NULL,
  `fcfps` float DEFAULT NULL,
  `gp` bigint(20) DEFAULT NULL,
  `grossmargin` float DEFAULT NULL,
  `inventory` bigint(20) DEFAULT NULL,
  `investments` bigint(20) DEFAULT NULL,
  `liabilities` bigint(20) DEFAULT NULL,
  `ncf` bigint(20) DEFAULT NULL,
  `netmargin` float DEFAULT NULL,
  `payables` bigint(20) DEFAULT NULL,
  `pb` float DEFAULT NULL,
  `pe` float DEFAULT NULL,
  `ps` float DEFAULT NULL,
  `receivables` bigint(20) DEFAULT NULL,
  `revenue` bigint(20) DEFAULT NULL,
  `rnd` bigint(20) DEFAULT NULL,
  `roa` float DEFAULT NULL,
  `roe` float DEFAULT NULL,
  `roic` float DEFAULT NULL,
  `ros` float DEFAULT NULL,
  `tangibles` bigint(20) DEFAULT NULL,
  `workingcapital` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`ticker`,`dateCal`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Daten Export vom Benutzer nicht ausgewählt

-- Exportiere Struktur von Tabelle stockdb_akramluna.stockmain
CREATE TABLE IF NOT EXISTS `stockmain` (
  `ticker` varchar(20) NOT NULL,
  `lastUpdate` datetime DEFAULT NULL,
  `name` varchar(50) DEFAULT NULL,
  `currency` varchar(10) DEFAULT NULL,
  `exchange` varchar(50) DEFAULT NULL,
  `actPrice` float DEFAULT NULL,
  `fiftyDayRangeFrom` float DEFAULT NULL,
  `fiftyDayRangeTo` float DEFAULT NULL,
  `marketCap` float DEFAULT NULL,
  `beta` float DEFAULT NULL,
  `price1YEst` float DEFAULT NULL,
  `companySite` varchar(50) DEFAULT NULL,
  `firstPriceDate` date DEFAULT NULL,
  `older1Year` char(1) DEFAULT NULL,
  `sector` varchar(50) DEFAULT NULL,
  `industry` varchar(50) DEFAULT NULL,
  `famaindustry` varchar(50) DEFAULT NULL,
  `nextEarningsDate` date DEFAULT NULL,
  `lastDividendDate` date DEFAULT NULL,
  `forwardDividend` float DEFAULT NULL,
  `dividendYield` float DEFAULT NULL,
  PRIMARY KEY (`ticker`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Daten Export vom Benutzer nicht ausgewählt

-- Exportiere Struktur von Tabelle stockdb_akramluna.stocknews
CREATE TABLE IF NOT EXISTS `stocknews` (
  `benzingaID` int(11) NOT NULL,
  `ticker` varchar(50) DEFAULT NULL,
  `datetimeNews` datetime DEFAULT NULL,
  `sourceNews` varchar(50) DEFAULT NULL,
  `textNews` varchar(255) DEFAULT NULL,
  `urlNews` varchar(255) DEFAULT NULL,
  `tagsNews` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`benzingaID`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Daten Export vom Benutzer nicht ausgewählt

-- Exportiere Struktur von Tabelle stockdb_akramluna.stockprices
CREATE TABLE IF NOT EXISTS `stockprices` (
  `ticker` varchar(50) NOT NULL,
  `datePrice` date NOT NULL,
  `open` float DEFAULT NULL,
  `high` float DEFAULT NULL,
  `low` float DEFAULT NULL,
  `close` float DEFAULT NULL,
  `adjClose` float DEFAULT NULL,
  `volume` float DEFAULT NULL,
  PRIMARY KEY (`ticker`,`datePrice`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Daten Export vom Benutzer nicht ausgewählt

/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IF(@OLD_FOREIGN_KEY_CHECKS IS NULL, 1, @OLD_FOREIGN_KEY_CHECKS) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
