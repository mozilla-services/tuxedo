-- incremental changes to make original bouncer DB work in Django

-- primary keys
ALTER TABLE `mirror_ip_to_country` ADD `id` INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY FIRST;

ALTER TABLE `mirror_location_mirror_map` DROP PRIMARY KEY ,ADD UNIQUE ( `location_id` , `mirror_id` ) ;
ALTER TABLE `mirror_location_mirror_map` ADD `id` INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY FIRST;

ALTER TABLE `mirror_mirror_region_map` DROP PRIMARY KEY , ADD UNIQUE ( `mirror_id` , `region_id` );
ALTER TABLE `mirror_mirror_region_map` ADD `id` INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY FIRST;

-- boolean fields
ALTER TABLE `mirror_location_mirror_map` CHANGE `location_active` `location_active` TINYINT NOT NULL DEFAULT '0' ;
UPDATE `mirror_location_mirror_map` SET location_active = 0 WHERE location_active = 1;
UPDATE `mirror_location_mirror_map` SET location_active = 1 WHERE location_active = 2;
ALTER TABLE `mirror_mirrors` CHANGE `mirror_active` `mirror_active` TINYINT NOT NULL DEFAULT '0' ;
UPDATE `mirror_mirrors` SET mirror_active = 0 WHERE mirror_active = 1;
UPDATE `mirror_mirrors` SET mirror_active = 1 WHERE mirror_active = 2;
ALTER TABLE `mirror_products` CHANGE `product_active` `product_active` TINYINT NOT NULL DEFAULT '1' ;
UPDATE `mirror_products` SET product_active = 0 WHERE product_active = 1;
UPDATE `mirror_products` SET product_active = 1 WHERE product_active = 2;

