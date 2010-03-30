-- ONLY apply this if you are running pre-1.5 Bouncer without locale awareness!

-- if so, run this before incremental.sql

DROP TABLE IF EXISTS `mirror_langs`;
CREATE TABLE `mirror_langs` (
  `lang_id` int(10) unsigned NOT NULL auto_increment,
  `lang` varchar(10) NOT NULL default '',
  PRIMARY KEY  (`lang_id`),
  UNIQUE KEY `lang` (`lang`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='Locales' ;

ALTER TABLE `mirror_locations` ADD `lang_id` INT( 10 ) NULL ;

ALTER TABLE `mirror_locations` ADD UNIQUE `query` ( `location_id` , `product_id` , `os_id` , `lang_id` );


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

-- seconds set of languages, 2010/03/30
INSERT INTO `mirror_langs` (`lang`) VALUES
('af'),
('as'),
('bn-BD'),
('bn-IN'),
('hr'),
('eo'),
('et'),
('gl'),
('hi-IN'),
('is'),
('id'),
('kn'),
('kk'),
('lv'),
('ml'),
('mr'),
('oc'),
('or'),
('fa'),
('pt-PT'),
('rm'),
('sr'),
('si'),
('es-CL'),
('es-MX'),
('ta'),
('ta-LK'),
('te'),
('th'),
('uk'),
('vi'),
('cy');

-- set all existing locations' language to en-US
UPDATE `mirror_locations` SET lang_id = 10;

-- from each existing row, create location entries for all other languages
INSERT INTO mirror_locations (product_id, os_id, location_path, lang_id)
    SELECT `product_id`, `os_id`, REPLACE(`location_path`, 'en-US', lang.lang), lang.lang_id
        FROM `mirror_locations` AS loc, `mirror_langs` AS lang 
        WHERE lang.lang_id <> 10;

