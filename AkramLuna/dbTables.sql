-- --------------------------------------------------------
-- Host:                         127.0.0.1
-- Server version:               10.3.24-MariaDB - mariadb.org binary distribution
-- Server OS:                    Win64
-- HeidiSQL Version:             11.0.0.6104
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;


-- Dumping database structure for stockdb_akramluna
CREATE DATABASE IF NOT EXISTS `stockdb_akramluna` /*!40100 DEFAULT CHARACTER SET latin1 */;
USE `stockdb_akramluna`;

-- Dumping structure for table stockdb_akramluna.stockdailydata
CREATE TABLE IF NOT EXISTS `stockdailydata` (
  `ticker` varchar(50) NOT NULL,
  `dateMeasure` date NOT NULL,
  `ev` float DEFAULT NULL,
  `evToEbit` float DEFAULT NULL,
  `evToEbitda` float DEFAULT NULL,
  `pbRatio` float DEFAULT NULL,
  `peRatio` float DEFAULT NULL,
  `psRatio` float DEFAULT NULL,
  PRIMARY KEY (`ticker`,`dateMeasure`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Data exporting was unselected.

-- Dumping structure for table stockdb_akramluna.stockfinancials
CREATE TABLE IF NOT EXISTS `stockfinancials` (
  `ticker` varchar(50) NOT NULL,
  `dateCal` date NOT NULL,
  `dateReport` date DEFAULT NULL,
  `price` float DEFAULT NULL,
  `netinc` int(11) DEFAULT NULL,
  `marketcap` int(11) DEFAULT NULL,
  `accoci` int(11) DEFAULT NULL,
  `assets` int(11) DEFAULT NULL,
  `assetsavg` int(11) DEFAULT NULL,
  `assetturnover` float DEFAULT NULL,
  `bvps` float DEFAULT NULL,
  `capex` int(11) DEFAULT NULL,
  `cashneq` int(11) DEFAULT NULL,
  `cor` int(11) DEFAULT NULL,
  `currentratio` float DEFAULT NULL,
  `de` float DEFAULT NULL,
  `debt` int(11) DEFAULT NULL,
  `deferredrev` int(11) DEFAULT NULL,
  `depamor` int(11) DEFAULT NULL,
  `ebit` int(11) DEFAULT NULL,
  `ebitda` int(11) DEFAULT NULL,
  `ebitdamargin` float DEFAULT NULL,
  `eps` float DEFAULT NULL,
  `equity` int(11) DEFAULT NULL,
  `ev` int(11) DEFAULT NULL,
  `evebit` float DEFAULT NULL,
  `evebidta` float DEFAULT NULL,
  `fcf` int(11) DEFAULT NULL,
  `fcfps` float DEFAULT NULL,
  `gp` int(11) DEFAULT NULL,
  `grossmargin` float DEFAULT NULL,
  `intangibles` int(11) DEFAULT NULL,
  `invcap` int(11) DEFAULT NULL,
  `inventory` int(11) DEFAULT NULL,
  `investments` int(11) DEFAULT NULL,
  `liabilities` int(11) DEFAULT NULL,
  `ncf` int(11) DEFAULT NULL,
  `ncfbus` int(11) DEFAULT NULL,
  `ncfcommon` int(11) DEFAULT NULL,
  `netmargin` float DEFAULT NULL,
  `opex` int(11) DEFAULT NULL,
  `opinc` int(11) DEFAULT NULL,
  `payables` int(11) DEFAULT NULL,
  `pb` float DEFAULT NULL,
  `pe` float DEFAULT NULL,
  `ps` float DEFAULT NULL,
  `receivables` int(11) DEFAULT NULL,
  `revenue` int(11) DEFAULT NULL,
  `rnd` int(11) DEFAULT NULL,
  `roa` float DEFAULT NULL,
  `roe` float DEFAULT NULL,
  `roic` float DEFAULT NULL,
  `ros` float DEFAULT NULL,
  `sbcomp` int(11) DEFAULT NULL,
  `sgna` int(11) DEFAULT NULL,
  `sharesbas` int(11) DEFAULT NULL,
  `shareswa` int(11) DEFAULT NULL,
  `shareswadil` int(11) DEFAULT NULL,
  `sps` float DEFAULT NULL,
  `tangibles` int(11) DEFAULT NULL,
  `taxassets` int(11) DEFAULT NULL,
  `taxexp` int(11) DEFAULT NULL,
  `taxliabilities` int(11) DEFAULT NULL,
  `tbvps` float DEFAULT NULL,
  `workingcapital` int(11) DEFAULT NULL,
  PRIMARY KEY (`ticker`,`dateCal`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Data exporting was unselected.

-- Dumping structure for table stockdb_akramluna.stockmain
CREATE TABLE IF NOT EXISTS `stockmain` (
  `ticker` varchar(20) NOT NULL,
  `lastUpdate` timestamp NULL DEFAULT NULL,
  `name` varchar(50) DEFAULT NULL,
  `currency` varchar(10) DEFAULT NULL,
  `comanySite` varchar(50) DEFAULT NULL,
  `firstPriceDate` date DEFAULT NULL,
  `older1Year` char(1) DEFAULT NULL,
  `sector` varchar(50) DEFAULT NULL,
  `industry` varchar(50) DEFAULT NULL,
  `famaindustry` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`ticker`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Data exporting was unselected.

-- Dumping structure for table stockdb_akramluna.stocknews
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

-- Data exporting was unselected.

-- Dumping structure for table stockdb_akramluna.stockprices
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

-- Data exporting was unselected.

/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IF(@OLD_FOREIGN_KEY_CHECKS IS NULL, 1, @OLD_FOREIGN_KEY_CHECKS) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
