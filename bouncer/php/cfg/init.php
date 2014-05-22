<?php
/**
 *  Init.
 *  @package mirror
 *  @subpackage cfg
 */
require_once('config.php');  // config file that defines constants
require_once(LIB.'/util.php');  // util file for random functions (no SQL here)
$start = microtime_float();  // start timer
require_once(LIB.'/db.php');  // core mysql wrappers used in mirror functions
db_connect(DBHOST,DBUSER,DBPASS);  // open persistent connection to db
db_select(DBNAME);  // select db
if (!empty($protect)) {
    require_once('admin_init.php');
}
?>
