SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';

CREATE SCHEMA IF NOT EXISTS `mydb` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci ;
USE `mydb` ;

-- -----------------------------------------------------
-- Table `mydb`.`user`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `mydb`.`user` ;

CREATE TABLE IF NOT EXISTS `mydb`.`user` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `email` VARCHAR(200) NOT NULL,
  `name` VARCHAR(100) NOT NULL,
  `about` VARCHAR(200) NOT NULL,
  `username` VARCHAR(50) NOT NULL,
  `password` VARCHAR(100) NOT NULL,
  `isAnonymous` TINYINT(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `email_UNIQUE` (`email` ASC),
  UNIQUE INDEX `username_UNIQUE` (`username` ASC))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `mydb`.`forum`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `mydb`.`forum` ;

CREATE TABLE IF NOT EXISTS `mydb`.`forum` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(200) NOT NULL,
  `short_name` VARCHAR(100) NOT NULL,
  `user` VARCHAR(50) NOT NULL,
  `user_id` BIGINT UNSIGNED NOT NULL,
  PRIMARY KEY (`id`, `user_id`),
  INDEX `fk_forum_user1_idx` (`user_id` ASC),
  UNIQUE INDEX `short_name_UNIQUE` (`short_name` ASC),
  CONSTRAINT `fk_forum_user1`
    FOREIGN KEY (`user_id`)
    REFERENCES `mydb`.`user` (`id`)
    ON DELETE RESTRICT
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `mydb`.`thread`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `mydb`.`thread` ;

CREATE TABLE IF NOT EXISTS `mydb`.`thread` (
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
  `forum_id` BIGINT UNSIGNED NOT NULL,
  `user_id` BIGINT UNSIGNED NOT NULL,
  PRIMARY KEY (`id`, `forum_id`, `user_id`),
  INDEX `fk_thread_forum1_idx` (`forum_id` ASC),
  INDEX `fk_thread_user1_idx` (`user_id` ASC),
  UNIQUE INDEX `slug_UNIQUE` (`slug` ASC),
  CONSTRAINT `fk_thread_forum1`
    FOREIGN KEY (`forum_id`)
    REFERENCES `mydb`.`forum` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_thread_user1`
    FOREIGN KEY (`user_id`)
    REFERENCES `mydb`.`user` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `mydb`.`post`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `mydb`.`post` ;

CREATE TABLE IF NOT EXISTS `mydb`.`post` (
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
  `user_id` BIGINT UNSIGNED NOT NULL,
  `parent` BIGINT UNSIGNED NOT NULL,
  `thread_id` BIGINT UNSIGNED NOT NULL,
  PRIMARY KEY (`id`, `user_id`, `parent`, `thread_id`),
  INDEX `fk_post_user1_idx` (`user_id` ASC),
  INDEX `fk_post_post1_idx` (`parent` ASC),
  INDEX `fk_post_thread1_idx` (`thread_id` ASC),
  CONSTRAINT `fk_post_user1`
    FOREIGN KEY (`user_id`)
    REFERENCES `mydb`.`user` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_post_post1`
    FOREIGN KEY (`parent`)
    REFERENCES `mydb`.`post` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_post_thread1`
    FOREIGN KEY (`thread_id`)
    REFERENCES `mydb`.`thread` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `mydb`.`followers`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `mydb`.`followers` ;

CREATE TABLE IF NOT EXISTS `mydb`.`followers` (
  `follower` BIGINT UNSIGNED NOT NULL,
  `followee` BIGINT UNSIGNED NOT NULL,
  `isFollowing` TINYINT(1) NOT NULL DEFAULT 0,
  INDEX `fk_followers_user1_idx` (`follower` ASC),
  INDEX `fk_followers_user2_idx` (`followee` ASC),
  PRIMARY KEY (`follower`, `followee`),
  CONSTRAINT `fk_followers_user1`
    FOREIGN KEY (`follower`)
    REFERENCES `mydb`.`user` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_followers_user2`
    FOREIGN KEY (`followee`)
    REFERENCES `mydb`.`user` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `mydb`.`subscription`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `mydb`.`subscription` ;

CREATE TABLE IF NOT EXISTS `mydb`.`subscription` (
  `thread_id` BIGINT UNSIGNED NOT NULL,
  `user_id` BIGINT UNSIGNED NOT NULL,
  `isSubscribed` TINYINT(1) NOT NULL DEFAULT 0,
  INDEX `fk_subscription_thread1_idx` (`thread_id` ASC),
  INDEX `fk_subscription_user1_idx` (`user_id` ASC),
  PRIMARY KEY (`thread_id`, `user_id`),
  CONSTRAINT `fk_subscription_thread1`
    FOREIGN KEY (`thread_id`)
    REFERENCES `mydb`.`thread` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_subscription_user1`
    FOREIGN KEY (`user_id`)
    REFERENCES `mydb`.`user` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

SET SQL_MODE = '';
GRANT USAGE ON *.* TO test_user;
 DROP USER test_user;
SET SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';
CREATE USER 'test_user' IDENTIFIED BY 'test_pass';

GRANT ALL ON `mydb`.* TO 'test_user';

SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
