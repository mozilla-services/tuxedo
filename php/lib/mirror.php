<?php
/**
 *  Application functions.  Dependent on lib/db.php!
 *  @package mirror
 *  @subpackage lib
 *  @todo add transactions once innodb table types are in place 
 */

/**
 *  Get an alpha-list of regions for select list.
 *  @return array $regions
 */
function mirror_get_regions_select()
{
    $regions = db_get("SELECT region_id,region_name FROM mirror_regions ORDER BY region_name ASC",MYSQL_ASSOC); 
    foreach ($regions as $region) {
        $retval[$region['region_id']]=$region['region_name'];
    }
    return $retval;
}

/**
 *  Get an priority-list of regions for select list.
 *  @return array $regions
 */
function mirror_get_regions_select_priority()
{
    $regions = db_get("SELECT region_id,region_name FROM mirror_regions ORDER BY region_priority ASC",MYSQL_ASSOC); 
    foreach ($regions as $region) {
        $retval[$region['region_id']]=$region['region_name'];
    }
    return $retval;
}

/**
 *  Insert region.
 *  @param string $name
 *  @param int $priority
 *  @return bool
 */ 
function mirror_insert_region($name,$priority)
{
    return db_query("INSERT INTO mirror_regions(region_name,region_priority) VALUES('{$name}',{$priority})");
}

/**
 *  Update region.
 *  @param int $id
 *  @param string $name
 *  @param int $priority
 *  @return bool
 */ 
function mirror_update_region($id,$name,$priority)
{
    return db_query("UPDATE mirror_regions SET region_name='{$name}',region_priority={$priority} WHERE region_id={$id}");
}

/**
 *  Get one region.
 *  @param int $id
 *  @return array
 */
function mirror_get_one_region($id)
{
    return db_get_one("SELECT * FROM mirror_regions WHERE region_id = {$id}");
}

/**
 *  Delete a region.
 *  @param int $id
 *  @return bool
 */
function mirror_delete_region($id)
{
    return db_query("DELETE FROM mirror_regions WHERE region_id={$id}");
}

/**
 *  Get an alpha-list of mirrors for select list.
 *  @return array $mirrors
 */
function mirror_get_mirrors_select()
{
    $mirrors = db_get("SELECT mirror_id,mirror_name FROM mirror_mirrors ORDER BY mirror_name ASC",MYSQL_ASSOC); 
    foreach ($mirrors as $mirror) {
        $retval[$mirror['mirror_id']]=$mirror['mirror_name'];
    }
    return $retval;
}

/**
 *  Get regions.
 *  @return array
 */
function mirror_get_regions()
{
    return db_get("
        SELECT 
            mirror_regions.*,
            COUNT(mirror_id) as mirrors
        FROM 
            mirror_regions
        LEFT JOIN
            mirror_mirror_region_map
        ON
            mirror_regions.region_id = mirror_mirror_region_map.region_id
        GROUP BY
            mirror_regions.region_id 
    ",MYSQL_ASSOC);
}

/***** MIRRORS *****/
/**
 *  Insert mirror.
 *  @param string $name
 *  @param int $region_id
 *  @param string $baseurl
 *  @param int $rating
 *  @return bool
 */
function mirror_insert_mirror($name,$region_id,$baseurl,$rating)
{
    return (db_query("INSERT INTO mirror_mirrors(mirror_name,mirror_baseurl,mirror_rating) VALUES('{$name}','{$baseurl}','{$rating}')") && db_query("INSERT INTO mirror_mirror_region_map(mirror_id,region_id) VALUES('".db_insert_id()."','$region_id')"))?true:false;
}

/**
 *  Update mirror.
 *  @param string $name
 *  @param int $region_id
 *  @param string $baseurl
 *  @param int $rating
 *  @return bool
 */
function mirror_update_mirror($id,$name,$region_id,$baseurl,$rating)
{
    return (db_query("UPDATE mirror_mirrors SET mirror_name='{$name}',mirror_baseurl='{$baseurl}',mirror_rating='{$rating}' WHERE mirror_id={$id}") && db_query("UPDATE mirror_mirror_region_map SET region_id={$region_id} WHERE mirror_id={$id}"))?true:false;
}

/**
 *  Delete mirror.
 *  @return bool
 */
function mirror_delete_mirror($mirror_id)
{
    return (db_query("DELETE FROM mirror_mirrors WHERE mirror_id={$mirror_id}")&&db_query("DELETE FROM mirror_mirror_region_map WHERE mirror_id={$mirror_id}"))?true:false;
}

/**
 *  Get one mirror record.
 *  @param int $mirror_id
 *  @return array mirror information
 */
function mirror_get_one_mirror($mirror_id)
{
    return db_get_one("SELECT mirror_mirrors.*,region_id FROM mirror_mirrors,mirror_mirror_region_map WHERE mirror_mirrors.mirror_id={$mirror_id} AND mirror_mirrors.mirror_id=mirror_mirror_region_map.mirror_id");
}

/**
 *  Get list of mirrors.
 *  @return array
 */
function mirror_get_mirrors()
{
    return db_get("
        SELECT 
            mirror_mirrors.*,
            IF(mirror_mirrors.mirror_active='0','DISABLED','ok') as mirror_active,
            region_name
        FROM 
            mirror_mirrors,
            mirror_regions,
            mirror_mirror_region_map
        WHERE
            mirror_regions.region_id = mirror_mirror_region_map.region_id AND
            mirror_mirrors.mirror_id = mirror_mirror_region_map.mirror_id
    ",MYSQL_ASSOC);
}

/***** PRODUCTS *****/
/**
 *  Insert product.
 *  @param string $name
 *  @param int $priority
 *  @return bool
 */ 
function mirror_insert_product($name,$priority)
{
    return db_query("INSERT INTO mirror_products(product_name,product_priority) VALUES('{$name}',{$priority})");
}

/**
 *  Update product.
 *  @param int $id
 *  @param string $name
 *  @param int $priority
 *  @return bool
 */ 
function mirror_update_product($id,$name,$priority)
{
    return db_query("UPDATE mirror_products SET product_name='{$name}',product_priority={$priority} WHERE product_id={$id}");
}

/**
 *  Get one product.
 *  @param int $id
 *  @return array
 */
function mirror_get_one_product($id)
{
    return db_get_one("SELECT * FROM mirror_products WHERE product_id = {$id}");
}

/**
 *  Delete a product.
 *  @param int $id
 *  @return bool
 */
function mirror_delete_product($id)
{
    return db_query("DELETE FROM mirror_products WHERE product_id={$id}");
}

/**
 *  Get products.
 *  @return array
 */
function mirror_get_products()
{
    return db_get("
        SELECT 
            *,
            IF(mirror_products.product_checknow='0','no','YES') as product_checknow
        FROM 
            mirror_products
    ",MYSQL_ASSOC);
}

/***** OPERATING SYSTEMS *****/
/**
 *  Insert os.
 *  @param string $name
 *  @param int $priority
 *  @return bool
 */ 
function mirror_insert_os($name,$priority)
{
    return db_query("INSERT INTO mirror_os(os_name,os_priority) VALUES('{$name}',{$priority})");
}

/**
 *  Update os.
 *  @param int $id
 *  @param string $name
 *  @param int $priority
 *  @return bool
 */ 
function mirror_update_os($id,$name,$priority)
{
    return db_query("UPDATE mirror_os SET os_name='{$name}',os_priority={$priority} WHERE os_id={$id}");
}

/**
 *  Get one os.
 *  @param int $id
 *  @return array
 */
function mirror_get_one_os($id)
{
    return db_get_one("SELECT * FROM mirror_os WHERE os_id = {$id}");
}

/**
 *  Delete a os.
 *  @param int $id
 *  @return bool
 */
function mirror_delete_os($id)
{
    return db_query("DELETE FROM mirror_os WHERE os_id={$id}");
}

/**
 *  Get operating systems.
 *  @return array
 */
function mirror_get_oss()
{
    return db_get("
        SELECT 
            *
        FROM 
            mirror_os
    ",MYSQL_ASSOC);
}

/**
 *  Get an alpha-list of operating systems for select list.
 *  @return array $oss
 */
function mirror_get_oss_select()
{
    $oss = db_get("SELECT os_id,os_name FROM mirror_os ORDER BY os_name ASC",MYSQL_ASSOC); 
    foreach ($oss as $os) {
        $retval[$os['os_id']]=$os['os_name'];
    }
    return $retval;
}

/**
 *  Get an priority-list of operating systems for select list.
 *  @return array $oss
 */
function mirror_get_oss_select_priority()
{
    $oss = db_get("SELECT os_id,os_name FROM mirror_os ORDER BY os_priority ASC",MYSQL_ASSOC); 
    foreach ($oss as $os) {
        $retval[$os['os_id']]=$os['os_name'];
    }
    return $retval;
}

/**
 *  Get an alpha-list of products for select list.
 *  @return array $products
 */
function mirror_get_products_select()
{
    $products = db_get("SELECT product_id,product_name FROM mirror_products ORDER BY product_name ASC",MYSQL_ASSOC); 
    foreach ($products as $product) {
        $retval[$product['product_id']]=$product['product_name'];
    }
    return $retval;
}

/**
 *  Get an priority-list of operating systems for select list.
 *  @return array $oss
 */
function mirror_get_products_select_priority()
{
    $products = db_get("SELECT product_id,product_name FROM mirror_products ORDER BY product_priority ASC",MYSQL_ASSOC); 
    foreach ($products as $product) {
        $retval[$product['product_id']]=$product['product_name'];
    }
    return $retval;
}

/***** LOCATIONS *****/
/**
 *  Insert a new location.
 *  @param int $product
 *  @param int $os
 *  @param int $lang
 *  @param string $path
 *  @return bool
 */
function mirror_insert_location($product,$os,$lang,$path)
{
    if (is_null($lang)) $lang = 'NULL';
    return db_query("INSERT INTO mirror_locations(product_id,os_id,lang_id,location_path) VALUES({$product},{$os},{$lang},'{$path}')");
}

/**
 *  Update a location.
 *  @param int $location
 *  @param int $product
 *  @param int $os
 *  @param int $language
 *  @param string $path
 *  @return bool
 */
function mirror_update_location($location,$product,$os,$lang,$path)
{
    return db_query("UPDATE mirror_locations SET product_id={$product},os_id={$os},lang_id={$lang},location_path='{$path}' WHERE location_id={$location}");
}

/**
 *  Delete a location.
 *  @param int $id
 *  @return bool
 */
function mirror_delete_location($id)
{
    return db_query("DELETE FROM mirror_locations WHERE location_id={$id}");
}

/**
 *  Get locations.
 *  @return array $locations array containing all location information.
 */
function mirror_get_locations()
{
    return db_get("
        SELECT 
            location_id,
            product_name,
            os_name,
            location_path,
            lang
        FROM 
            mirror_locations AS loc,
            mirror_products AS prod,
            mirror_os AS os
        LEFT JOIN
            mirror_langs AS langs ON (loc.lang_id = langs.lang_id)
        WHERE
            loc.product_id = prod.product_id AND
            loc.os_id = os.os_id
    "); 
}

/**
 *  Get one location.
 *  @param int $id
 *  @return array
 */
function mirror_get_one_location($id)
{
    return db_get_one("SELECT * FROM mirror_locations WHERE location_id = {$id}");
}

/***** LANGUAGES *****/

/**
 *  Insert a new language.
 *  @param string $lang
 *  @return bool
 */
function mirror_insert_lang($lang)
{
    $lang = addslashes($lang);
    return db_query("INSERT INTO mirror_langs (lang) VALUES('{$lang}')");
}

/**
 *  Update a language.
 *  @param int $lang_id
 *  @param int $lang
 *  @return bool
 */
function mirror_update_lang($lang_id, $lang)
{
    $lang_id = addslashes($lang_id);
    $lang = addslashes($lang);
    return db_query("UPDATE mirror_langs SET lang='{$lang}' WHERE lang_id={$lang_id}");
}

/**
 *  Delete a language.
 *  @param int $id
 *  @return bool
 */
function mirror_delete_lang($id)
{
    $id = addslashes($id);
    return db_query("DELETE FROM mirror_langs WHERE lang_id={$id}");
}

/**
 *  Get languages.
 *  @return array $angs array containing all language information.
 */
function mirror_get_langs()
{
    return db_get("
        SELECT 
            lang_id,
            lang
        FROM 
            mirror_langs
    "); 
}

/**
 *  Get one language.
 *  @param int $id
 *  @return array
 */
function mirror_get_one_lang($id)
{
    $id = addslashes($id);
    return db_get_one("SELECT * FROM mirror_langs WHERE lang_id = {$id}");
}

/**
 *  Get an alpha-list of languages for select list.
 *  @return array $langs
 */
function mirror_get_langs_select()
{
    $langs = db_get("SELECT lang_id,lang FROM mirror_langs ORDER BY lang ASC",MYSQL_ASSOC); 
    foreach ($langs as $lang) {
        $retval[$lang['lang_id']]=$lang['lang'];
    }
    return $retval;
}

/***** USERS *****/

/**
 *  Insert a new user.
 *  @param string $username
 *  @param string $password
 *  @param string $rpassword (re-entered password)
 *  @param string $firstname
 *  @param string $lastname
 *  @param string $email
 *  @return bool
 */
function mirror_insert_user($username,$password,$rpassword,$firstname,$lastname,$email)
{
    if ($password==$rpassword) {
        return db_query("INSERT INTO mirror_users(username,password,user_firstname,user_lastname,user_email) VALUES('{$username}',MD5('{$password}'),'{$firstname}','{$lastname}','{$email}')");
    } else {
        set_error('User could not be added because passwords did not match.');
    }
}

/**
 *  Update a user.
 *  @param int $user
 *  @param string $username
 *  @param string $password
 *  @param string $rpassword (re-entered password)
 *  @param string $firstname
 *  @param string $lastname
 *  @param string $email
 *  @return bool
 */
function mirror_update_user($user,$username,$password,$rpassword,$firstname,$lastname,$email)
{
    $query = ($password==$rpassword&&!empty($password))?"UPDATE mirror_users SET username='{$username}',password=MD5('{$password}'),user_firstname='{$firstname}',user_lastname='{$lastname}',user_email='{$email}' WHERE user_id={$user}":"UPDATE mirror_users SET username='{$username}',user_firstname='{$firstname}',user_lastname='{$lastname}',user_email='{$email}' WHERE user_id={$user}";
    return db_query($query);
}

/**
 *  Delete a user.
 *  @param int $id
 *  @return bool
 */
function mirror_delete_user($id)
{
    return db_query("DELETE FROM mirror_users WHERE user_id={$id}");
}

/**
 *  Get users.
 *  @return array $users array containing all user information.
 */
function mirror_get_users()
{
    return db_get("SELECT * FROM mirror_users"); 
}

/**
 *  Get one user.
 *  @param int $id
 *  @return array
 */
function mirror_get_one_user($id)
{
    return db_get_one("SELECT * FROM mirror_users WHERE user_id = {$id}");
}

/**
 *  Enable or disable a mirror.
 *  @param int $mirror
 *  @return bool
 */
function mirror_toggle($mirror)
{
    return (db_toggle_bool('mirror_mirrors','mirror_id','mirror_active',$mirror))?true:false;
}

/**
 *  Get mirror statistics.
 *  @return array $stats
 */
function mirror_get_mirror_stats()
{
    return db_get("
        SELECT
            *,
            COUNT(mirror_log.mirror_id) as count
        FROM
            mirror_mirrors,
            mirror_log,
            mirror_regions,
            mirror_mirror_region_map
        WHERE
            mirror_log.mirror_id = mirror_mirrors.mirror_id AND
            mirror_mirrors.mirror_id = mirror_mirror_region_map.mirror_id AND
            mirror_regions.region_id = mirror_mirror_region_map.region_id
        GROUP BY
            mirror_log.mirror_id 
    ");
}

/**
 *  Get product statistics.
 *  @return array $stats
 */
function mirror_get_product_stats()
{
    return db_get("
        SELECT
            *,
            COUNT(mirror_locations.product_id) as count
        FROM
            mirror_log,
            mirror_locations,
            mirror_products
        WHERE
            mirror_log.location_id = mirror_locations.location_id AND
            mirror_locations.product_id = mirror_products.product_id
        GROUP BY
            mirror_locations.product_id
    ");
}

/**
 * Toggle product checking.
 * @param int $product product id
 */
function product_toggle($id)
{
    return (db_toggle_int('mirror_products','product_id','product_checknow',$id));
}
?>
