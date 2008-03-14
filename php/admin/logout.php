<?php
/**
 *  Admin logout. 
 *  @package mirror
 *  @subpackage admin
 */
require_once('../cfg/init.php');
require_once(LIB.'/auth.php');
auth_logout();
header('Location: '.PROTOCOL.'://'.$_SERVER['HTTP_HOST'].WEBPATH.'/admin/login.php');
exit;
?>
