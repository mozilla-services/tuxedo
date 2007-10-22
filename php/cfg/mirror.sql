-- phpMyAdmin SQL Dump
-- version 2.6.0-pl2
-- http://www.phpmyadmin.net
-- 
-- Server version: 4.0.20
-- PHP Version: 4.3.4
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
-- Table structure for table `mirror_langs`
-- 

CREATE TABLE `mirror_langs` (
  `lang_id` int(10) unsigned NOT NULL auto_increment,
  `lang` varchar(10) NOT NULL default '',
  PRIMARY KEY  (`lang_id`),
  UNIQUE KEY `lang` (`lang`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='Locales' ;

-- 
-- Dumping data for table `mirror_langs`
-- 

INSERT INTO `mirror_langs` (`lang_id`, `lang`) VALUES 
(1, 'ar'),
(3, 'be'),
(2, 'bg'),
(4, 'ca'),
(5, 'cs'),
(6, 'da'),
(7, 'de'),
(8, 'el'),
(9, 'en-GB'),
(10, 'en-US'),
(11, 'es-AR'),
(12, 'es-ES'),
(13, 'eu'),
(14, 'fi'),
(15, 'fr'),
(16, 'fy-NL'),
(17, 'ga-IE'),
(18, 'gu-IN'),
(19, 'he'),
(20, 'hu'),
(21, 'hy-AM'),
(22, 'it'),
(23, 'ja'),
(24, 'ja-JP-mac'),
(25, 'ka'),
(26, 'ko'),
(27, 'ku'),
(28, 'lt'),
(29, 'mk'),
(30, 'mn'),
(31, 'nb-NO'),
(32, 'nl'),
(33, 'nn-NO'),
(34, 'pa-IN'),
(35, 'pl'),
(36, 'pt-BR'),
(37, 'ro'),
(38, 'ru'),
(39, 'sk'),
(40, 'sl'),
(41, 'sq'),
(42, 'sv-SE'),
(43, 'tr'),
(44, 'zh-CN'),
(45, 'zh-TW');

-- --------------------------------------------------------

-- 
-- Table structure for table `mirror_location_mirror_map`
-- 

CREATE TABLE `mirror_location_mirror_map` (
  `location_id` int(10) unsigned NOT NULL default '0',
  `mirror_id` int(10) unsigned NOT NULL default '0',
  `location_active` enum('0','1') NOT NULL default '0',
  PRIMARY KEY  (`location_id`,`mirror_id`)
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
  `lang_id` int(10) default NULL,
  PRIMARY KEY  (`location_id`,`product_id`,`os_id`)
  UNIQUE KEY `query` (`location_id`,`product_id`,`os_id`,`lang_id`)
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
  `mirror_count` bigint(20) unsigned NOT NULL default '0',
  PRIMARY KEY  (`mirror_id`),
  UNIQUE KEY `mirror_name` (`mirror_name`),
  KEY `mirror_count` (`mirror_count`)
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
  `product_name` varchar(255) NOT NULL default '',
  `product_priority` int(11) NOT NULL default '0',
  `product_count` bigint(20) unsigned NOT NULL default '0',
  `product_active` enum('0','1') NOT NULL default '1',
  `product_checknow` tinyint(1) unsigned NOT NULL default '1',
  PRIMARY KEY  (`product_id`),
  UNIQUE KEY `product_name` (`product_name`),
  KEY `product_count` (`product_count`),
  KEY `product_active` (`product_active`),
  KEY `product_checknow` (`product_checknow`)
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
) TYPE=InnoDB AUTO_INCREMENT=12 ;

-- 
-- Dumping data for table `mirror_regions`
-- 

INSERT INTO `mirror_regions` (`region_id`, `region_name`, `region_priority`) VALUES 
(3, 'Europe', 2),
(4, 'North America', 1),
(9, 'Australia', 3),
(10, 'Asia', 3),
(11, 'South America', 3);

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
