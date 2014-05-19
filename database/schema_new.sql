SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------
-- -----------------------------------------------------
-- Schema dbms
-- -----------------------------------------------------
DROP SCHEMA IF EXISTS `dbms` ;
CREATE SCHEMA IF NOT EXISTS `dbms` DEFAULT CHARACTER SET utf8 ;
USE `dbms` ;

-- -----------------------------------------------------
-- Table `dbms`.`user`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `dbms`.`user` ;

CREATE TABLE IF NOT EXISTS `dbms`.`user` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `email` VARCHAR(100) NOT NULL,
  `name` VARCHAR(100) NULL,
  `about` VARCHAR(150) NULL,
  `username` VARCHAR(50) NULL DEFAULT NULL,
  `isAnonymous` TINYINT(1) NOT NULL,
  UNIQUE INDEX `id_UNIQUE` (`id` ASC),
  PRIMARY KEY (`email`))
ENGINE = InnoDB
AUTO_INCREMENT = 143
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `dbms`.`followers`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `dbms`.`followers` ;

CREATE TABLE IF NOT EXISTS `dbms`.`followers` (
  `follower` VARCHAR(100) NOT NULL,
  `followee` VARCHAR(100) NOT NULL,
  INDEX `fk_follower_idx` USING BTREE (`follower`(15) ASC),
  INDEX `fk_followee_idx` (`followee`(15) ASC),
  CONSTRAINT `fk_follower`
    FOREIGN KEY (`follower`)
    REFERENCES `dbms`.`user` (`email`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_followee`
    FOREIGN KEY (`followee`)
    REFERENCES `dbms`.`user` (`email`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `dbms`.`forum`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `dbms`.`forum` ;

CREATE TABLE IF NOT EXISTS `dbms`.`forum` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(100) NOT NULL,
  `short_name` VARCHAR(80) NOT NULL,
  `user` VARCHAR(100) NOT NULL DEFAULT '',
  PRIMARY KEY (`short_name`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC),
  INDEX `fk_forum_user1_idx` USING BTREE (`user`(15) ASC),
  CONSTRAINT `fk_forum_user1`
    FOREIGN KEY (`user`)
    REFERENCES `dbms`.`user` (`email`)
    ON UPDATE NO ACTION)
ENGINE = InnoDB
AUTO_INCREMENT = 105
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `dbms`.`thread`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `dbms`.`thread` ;

CREATE TABLE IF NOT EXISTS `dbms`.`thread` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `message` TEXT NOT NULL,
  `title` VARCHAR(150) NOT NULL,
  `slug` VARCHAR(80) NOT NULL,
  `isClosed` TINYINT(1) NOT NULL,
  `isDeleted` TINYINT(1) NOT NULL,
  `date` DATETIME NOT NULL,
  `likes` INT(10) UNSIGNED NOT NULL DEFAULT '0',
  `dislikes` INT(10) UNSIGNED NOT NULL DEFAULT '0',
  `points` INT(11) NOT NULL DEFAULT '0',
  `user` VARCHAR(100) NOT NULL DEFAULT '',
  `forum` VARCHAR(80) NOT NULL DEFAULT '',
  `posts` INT(10) UNSIGNED NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  INDEX `user_date` USING BTREE (`user`(15) ASC, `date` ASC),
  INDEX `forum_date` (`forum`(20) ASC, `date` ASC),
  CONSTRAINT `fk_thread_forum1`
    FOREIGN KEY (`forum`)
    REFERENCES `dbms`.`forum` (`short_name`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_thread_user1`
    FOREIGN KEY (`user`)
    REFERENCES `dbms`.`user` (`email`)
    ON UPDATE NO ACTION)
ENGINE = InnoDB
AUTO_INCREMENT = 88
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `dbms`.`post`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `dbms`.`post` ;

CREATE TABLE IF NOT EXISTS `dbms`.`post` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `date` DATETIME NOT NULL,
  `isApproved` TINYINT(1) NOT NULL,
  `isDeleted` TINYINT(1) NOT NULL,
  `isHighlighted` TINYINT(1) NOT NULL,
  `isEdited` TINYINT(1) NOT NULL,
  `isSpam` TINYINT(1) NOT NULL,
  `message` TEXT NOT NULL,
  `points` INT(11) NOT NULL DEFAULT '0',
  `likes` INT(10) UNSIGNED NOT NULL DEFAULT '0',
  `dislikes` INT(10) UNSIGNED NOT NULL DEFAULT '0',
  `parent` INT UNSIGNED NULL,
  `user` VARCHAR(100) NOT NULL,
  `thread` INT UNSIGNED NOT NULL,
  `forum` VARCHAR(80) NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_post_user1_idx` (`user`(15) ASC),
  INDEX `fk_post_thread1_idx` (`thread` ASC),
  INDEX `fk_post_forum_date_idx` (`forum`(20) ASC, `date` ASC),
  INDEX `fk_post_forum_user_idx` USING BTREE (`forum`(20) ASC, `user`(15) ASC),
  CONSTRAINT `fk_post_thread1`
    FOREIGN KEY (`thread`)
    REFERENCES `dbms`.`thread` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_post_forum1`
    FOREIGN KEY (`forum`)
    REFERENCES `dbms`.`forum` (`short_name`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_post_user1`
    FOREIGN KEY (`user`)
    REFERENCES `dbms`.`user` (`email`)
    ON UPDATE NO ACTION)
ENGINE = InnoDB
AUTO_INCREMENT = 73
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `dbms`.`subscription`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `dbms`.`subscription` ;

CREATE TABLE IF NOT EXISTS `dbms`.`subscription` (
  `user` VARCHAR(100) NOT NULL DEFAULT '',
  `thread` INT UNSIGNED NOT NULL DEFAULT '0',
  INDEX `fk_subscription_thread1_idx` USING BTREE (`thread` ASC),
  INDEX `fk_subscription_user1_idx` (`user`(15) ASC),
  CONSTRAINT `fk_subscription_thread1`
    FOREIGN KEY (`thread`)
    REFERENCES `dbms`.`thread` (`id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_subscription_user1`
    FOREIGN KEY (`user`)
    REFERENCES `dbms`.`user` (`email`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
