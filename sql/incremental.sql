-- incremental changes to make original bouncer DB work in Django

ALTER TABLE `mirror_ip_to_country` ADD `id` INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY FIRST;

ALTER TABLE `mirror_location_mirror_map` DROP PRIMARY KEY ,ADD UNIQUE ( `location_id` , `mirror_id` ) ;
ALTER TABLE `mirror_location_mirror_map` ADD `id` INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY FIRST;

ALTER TABLE `mirror_mirror_region_map` DROP PRIMARY KEY , ADD UNIQUE ( `mirror_id` , `region_id` );
ALTER TABLE `mirror_mirror_region_map` ADD `id` INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY FIRST;
