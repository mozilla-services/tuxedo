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
