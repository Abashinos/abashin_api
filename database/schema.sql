SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';

CREATE SCHEMA IF NOT EXISTS `dbms` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci ;
USE `dbms` ;

-- -----------------------------------------------------
-- Table `dbms`.`user`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `dbms`.`user` ;

CREATE TABLE IF NOT EXISTS `dbms`.`user` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `email` VARCHAR(200) NOT NULL,
  `name` VARCHAR(100) NOT NULL,
  `about` VARCHAR(200) NOT NULL,
  `username` VARCHAR(50) NOT NULL,
  `password` VARCHAR(100) NOT NULL,
  `isAnonymous` TINYINT(1) NOT NULL,
  PRIMARY KEY (`email`),
  UNIQUE INDEX `email_UNIQUE` (`email` ASC),
  UNIQUE INDEX `username_UNIQUE` (`username` ASC),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `dbms`.`forum`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `dbms`.`forum` ;

CREATE TABLE IF NOT EXISTS `dbms`.`forum` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(200) NOT NULL,
  `short_name` VARCHAR(100) NOT NULL,
  `user` VARCHAR(50) NOT NULL,
  `user_email` VARCHAR(200) NOT NULL,
  PRIMARY KEY (`user_email`, `short_name`),
  UNIQUE INDEX `short_name_UNIQUE` (`short_name` ASC),
  INDEX `fk_forum_user1_idx` (`user_email` ASC),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC),
  CONSTRAINT `fk_forum_user1`
    FOREIGN KEY (`user_email`)
    REFERENCES `dbms`.`user` (`email`)
    ON DELETE RESTRICT
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `dbms`.`thread`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `dbms`.`thread` ;

CREATE TABLE IF NOT EXISTS `dbms`.`thread` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `message` TEXT NOT NULL,
  `title` VARCHAR(200) NOT NULL,
  `slug` VARCHAR(200) NOT NULL,
  `isClosed` TINYINT(1) NOT NULL,
  `isDeleted` TINYINT(1) NOT NULL,
  `date` DATETIME NOT NULL,
  `likes` INT UNSIGNED NOT NULL DEFAULT 0,
  `dislikes` INT UNSIGNED NOT NULL DEFAULT 0,
  `points` INT NOT NULL,
  `user` VARCHAR(50) NOT NULL,
  `forum` VARCHAR(100) NOT NULL,
  `user_email` VARCHAR(200) NOT NULL,
  `forum_short_name` VARCHAR(100) NOT NULL,
  PRIMARY KEY (`user_email`, `forum_short_name`, `slug`),
  UNIQUE INDEX `slug_UNIQUE` (`slug` ASC),
  INDEX `fk_thread_user1_idx` (`user_email` ASC),
  INDEX `fk_thread_forum1_idx` (`forum_short_name` ASC),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC),
  CONSTRAINT `fk_thread_user1`
    FOREIGN KEY (`user_email`)
    REFERENCES `dbms`.`user` (`email`)
    ON DELETE RESTRICT
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_thread_forum1`
    FOREIGN KEY (`forum_short_name`)
    REFERENCES `dbms`.`forum` (`short_name`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `dbms`.`post`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `dbms`.`post` ;

CREATE TABLE IF NOT EXISTS `dbms`.`post` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `date` DATETIME NOT NULL,
  `isApproved` TINYINT(1) NOT NULL,
  `isDeleted` TINYINT(1) NOT NULL,
  `isHighlighted` TINYINT(1) NOT NULL,
  `isEdited` TINYINT(1) NOT NULL,
  `isSpam` TINYINT(1) NOT NULL,
  `message` TEXT NOT NULL,
  `points` INT NOT NULL,
  `likes` INT UNSIGNED NOT NULL DEFAULT 0,
  `dislikes` INT UNSIGNED NOT NULL DEFAULT 0,
  `user` VARCHAR(50) NOT NULL,
  `forum` VARCHAR(100) NOT NULL,
  `parent` BIGINT UNSIGNED NOT NULL,
  `user_email` VARCHAR(200) NOT NULL,
  `thread_slug` VARCHAR(200) NOT NULL,
  PRIMARY KEY (`id`, `parent`, `user_email`, `thread_slug`),
  INDEX `fk_post_user1_idx` (`user_email` ASC),
  INDEX `fk_post_thread1_idx` (`thread_slug` ASC),
  INDEX `fk_post_post1_idx` (`parent` ASC),
  CONSTRAINT `fk_post_user1`
    FOREIGN KEY (`user_email`)
    REFERENCES `dbms`.`user` (`email`)
    ON DELETE RESTRICT
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_post_thread1`
    FOREIGN KEY (`thread_slug`)
    REFERENCES `dbms`.`thread` (`slug`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_post_post1`
    FOREIGN KEY (`parent`)
    REFERENCES `dbms`.`post` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `dbms`.`followers`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `dbms`.`followers` ;

CREATE TABLE IF NOT EXISTS `dbms`.`followers` (
  `follower` VARCHAR(200) NOT NULL,
  `followee` VARCHAR(200) NOT NULL,
  `isFollowing` TINYINT(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`follower`, `followee`),
  INDEX `fk_followers_user2_idx` (`followee` ASC),
  CONSTRAINT `fk_followers_user1`
    FOREIGN KEY (`follower`)
    REFERENCES `dbms`.`user` (`email`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_followers_user2`
    FOREIGN KEY (`followee`)
    REFERENCES `dbms`.`user` (`email`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `dbms`.`subscription`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `dbms`.`subscription` ;

CREATE TABLE IF NOT EXISTS `dbms`.`subscription` (
  `user_email` VARCHAR(200) NOT NULL,
  `thread_id` BIGINT UNSIGNED NOT NULL,
  `isSubscribed` TINYINT(1) NOT NULL DEFAULT 0,
  INDEX `fk_subscription_thread1_idx` (`thread_id` ASC),
  PRIMARY KEY (`user_email`, `thread_id`),
  INDEX `fk_subscription_user1_idx` (`user_email` ASC),
  CONSTRAINT `fk_subscription_thread1`
    FOREIGN KEY (`thread_id`)
    REFERENCES `dbms`.`thread` (`id`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_subscription_user1`
    FOREIGN KEY (`user_email`)
    REFERENCES `dbms`.`user` (`email`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

SET SQL_MODE = '';
GRANT USAGE ON *.* TO test_user;
 DROP USER test_user;
SET SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';
CREATE USER 'test_user' IDENTIFIED BY 'test_pass';

GRANT ALL ON `dbms`.* TO 'test_user';

SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
