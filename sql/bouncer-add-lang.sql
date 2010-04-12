-- ONLY apply this if you are running pre-1.5 Bouncer without locale awareness!
-- if so, run this before incremental.sql

-- map products to languages. Do not add any mappings yet, i.e. assume all
-- current products are available in all languages. Sentry will sort out the
-- rest.
CREATE TABLE IF NOT EXISTS `mirror_product_langs` (
  `id` int(11) NOT NULL auto_increment,
  `product_id` int(11) NOT NULL,
  `language` varchar(30) NOT NULL,
  PRIMARY KEY  (`id`),
  UNIQUE KEY `product_id` (`product_id`,`language`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

-- put locale placeholder into all known locations
UPDATE `mirror_locations` SET location_path = REPLACE(location_path, 'en-US', ':lang');
