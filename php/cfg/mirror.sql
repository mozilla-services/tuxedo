-- phpMyAdmin SQL Dump
-- version 2.6.0-pl2
-- http://www.phpmyadmin.net
-- 
-- Host: db1.osuosl.org
-- Generation Time: Nov 03, 2004 at 11:26 PM
-- Server version: 4.0.20
-- PHP Version: 4.3.4
-- 
-- Database: `mozilla-mirror`
-- 

-- --------------------------------------------------------

-- 
-- Table structure for table `mirror_ip_to_country`
-- 

DROP TABLE IF EXISTS `mirror_ip_to_country`;
CREATE TABLE `mirror_ip_to_country` (
  `ip_start` int(12) NOT NULL default '0',
  `ip_end` int(12) NOT NULL default '0',
  `country_code` char(2) NOT NULL default '',
  `country_abbrev` char(3) NOT NULL default '',
  `country_name` varchar(64) NOT NULL default '',
  KEY `ip_start` (`ip_start`),
  KEY `ip_end` (`ip_end`)
) TYPE=InnoDB;

-- --------------------------------------------------------

-- 
-- Table structure for table `mirror_locations`
-- 

DROP TABLE IF EXISTS `mirror_locations`;
CREATE TABLE `mirror_locations` (
  `location_id` int(10) unsigned NOT NULL auto_increment,
  `product_id` int(10) unsigned NOT NULL default '0',
  `os_id` int(10) unsigned NOT NULL default '0',
  `location_path` varchar(255) NOT NULL default '',
  PRIMARY KEY  (`location_id`,`product_id`,`os_id`)
) TYPE=InnoDB AUTO_INCREMENT=7 ;

-- --------------------------------------------------------

-- 
-- Table structure for table `mirror_mirror_region_map`
-- 

DROP TABLE IF EXISTS `mirror_mirror_region_map`;
CREATE TABLE `mirror_mirror_region_map` (
  `mirror_id` int(10) unsigned NOT NULL default '0',
  `region_id` int(10) unsigned NOT NULL default '0',
  PRIMARY KEY  (`mirror_id`,`region_id`)
) TYPE=InnoDB;

-- --------------------------------------------------------

-- 
-- Table structure for table `mirror_mirrors`
-- 

DROP TABLE IF EXISTS `mirror_mirrors`;
CREATE TABLE `mirror_mirrors` (
  `mirror_id` int(10) unsigned NOT NULL auto_increment,
  `mirror_name` varchar(32) NOT NULL default '',
  `mirror_baseurl` varchar(255) NOT NULL default '',
  `mirror_rating` int(11) NOT NULL default '0',
  `mirror_active` enum('0','1') NOT NULL default '0',
  PRIMARY KEY  (`mirror_id`),
  UNIQUE KEY `mirror_name` (`mirror_name`)
) TYPE=InnoDB AUTO_INCREMENT=40 ;

-- --------------------------------------------------------

-- 
-- Table structure for table `mirror_os`
-- 

DROP TABLE IF EXISTS `mirror_os`;
CREATE TABLE `mirror_os` (
  `os_id` int(10) unsigned NOT NULL auto_increment,
  `os_name` varchar(32) NOT NULL default '',
  `os_priority` int(11) NOT NULL default '0',
  PRIMARY KEY  (`os_id`,`os_name`)
) TYPE=InnoDB AUTO_INCREMENT=6 ;

-- --------------------------------------------------------

-- 
-- Table structure for table `mirror_products`
-- 

DROP TABLE IF EXISTS `mirror_products`;
CREATE TABLE `mirror_products` (
  `product_id` int(10) unsigned NOT NULL auto_increment,
  `product_name` varchar(32) NOT NULL default '',
  `product_priority` int(11) NOT NULL default '0',
  PRIMARY KEY  (`product_id`),
  UNIQUE KEY `product_name` (`product_name`)
) TYPE=InnoDB AUTO_INCREMENT=6 ;

-- --------------------------------------------------------

-- 
-- Table structure for table `mirror_regions`
-- 

DROP TABLE IF EXISTS `mirror_regions`;
CREATE TABLE `mirror_regions` (
  `region_id` int(10) unsigned NOT NULL auto_increment,
  `region_name` varchar(255) NOT NULL default '',
  `region_priority` int(11) NOT NULL default '0',
  PRIMARY KEY  (`region_id`),
  UNIQUE KEY `region_name` (`region_name`)
) TYPE=InnoDB AUTO_INCREMENT=11 ;

-- --------------------------------------------------------

-- 
-- Table structure for table `mirror_sessions`
-- 

DROP TABLE IF EXISTS `mirror_sessions`;
CREATE TABLE `mirror_sessions` (
  `session_id` varchar(32) NOT NULL default '',
  `username` varchar(16) NOT NULL default '',
  PRIMARY KEY  (`session_id`)
) TYPE=InnoDB;

-- --------------------------------------------------------

-- 
-- Table structure for table `mirror_users`
-- 

DROP TABLE IF EXISTS `mirror_users`;
CREATE TABLE `mirror_users` (
  `user_id` int(10) unsigned NOT NULL auto_increment,
  `username` varchar(32) NOT NULL default '',
  `password` varchar(32) NOT NULL default '',
  `user_firstname` varchar(255) NOT NULL default '',
  `user_lastname` varchar(255) NOT NULL default '',
  `user_email` varchar(255) NOT NULL default '',
  PRIMARY KEY  (`user_id`,`username`,`password`),
  UNIQUE KEY `user_email` (`user_email`)
) TYPE=InnoDB AUTO_INCREMENT=8 ;
