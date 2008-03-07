<?php
/**
 *  Mirror configuration document.
 *  @package mirror
 *  @subpackage cfg
 */
define('FILEPATH','/var/www/download');  // filepath of root dir
define('WEBPATH','');  // web path of root dir
define('LIB',FILEPATH.'/lib');  // path to lib dir
define('INC',FILEPATH.'/inc');  // path to inc dir 
define('HEADER',INC.'/header.php');  // header document
define('FOOTER',INC.'/footer.php');  // footer document
define('DBHOST', '');  // db host
define('DBNAME', '');  // db name
define('DBUSER', '');  // db user
define('DBPASS', '');  // db pass
define('LOGGING',1);  // enable logging? 1=on 0=off
define('CACHE',true);  // enable memcache?  true=on false=off (admin pages never cached)
define('CACHE_EXPIRE',60);  // how long to cache entries?
define('ALLOW_TEST_IP', false); // allow GeoIP testing by adding GET parameter &ip=11.22.33.44 ?
define('GEOIP',true); // enable GeoIP? true=on, false=off
define('MEMCACHE_NAMESPACE', 'ns'); // set memcache namespace.  Keep this string as short and simple as possible.

/**
 * Memcache configuration.
 * See http://php.oregonstate.edu/memcache for info.
 */
$memcache_config = array(
    'localhost' => array(
       'port' => '11211',
       'persistent' => true,
       'weight' => '1',
       'timeout' => '1',
       'retry_interval' => 15
    )
);

?>
