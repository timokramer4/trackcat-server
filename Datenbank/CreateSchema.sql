-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema TrackCatDB
-- -----------------------------------------------------
DROP SCHEMA IF EXISTS `TrackCatDB` ;

-- -----------------------------------------------------
-- Schema TrackCatDB
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `TrackCatDB` DEFAULT CHARACTER SET utf8 ;
USE `TrackCatDB` ;

-- -----------------------------------------------------
-- Table `TrackCatDB`.`users`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `TrackCatDB`.`users` (
  `idusers` INT NOT NULL AUTO_INCREMENT,
  `firstName` VARCHAR(45) NOT NULL,
  `lastName` VARCHAR(45) NOT NULL,
  `eMail` VARCHAR(45) NOT NULL,
  `password` VARCHAR(45) NOT NULL,
  `dateOfBirth` INT NULL,
  `weight` FLOAT NULL,
  `gender` TINYINT(1) NULL,
  `dateOfRegistration` INT NOT NULL,
  `lastLogin` INT NOT NULL,
  `darkTheme` TINYINT(1) NOT NULL,
  `showHelp` TINYINT(1) NOT NULL,
  `image` TEXT NULL,
  `timeStamp` INT NOT NULL,
  PRIMARY KEY (`idusers`),
  UNIQUE INDEX `eMail_UNIQUE` (`eMail` ASC) )
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
