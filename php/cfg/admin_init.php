<?php
/**
 *  Admin initialization.
 *  @package mirror
 *  @subpackage cfg
 */
require_once(LIB.'/auth.php');  // auth functions
require_once(LIB.'/forms.php'); // form library
require_once(LIB.'/list.php');  // list library

if (!auth_is_valid_session()) {
    header('Location: http://'.$_SERVER['HTTP_HOST'].WEBPATH.'/admin/login.php');
    exit;
}
?>
