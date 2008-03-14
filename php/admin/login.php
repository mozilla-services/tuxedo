<?php
/**
 *  Admin login. 
 *  @package mirror
 *  @subpackage admin
 */
require_once('../cfg/init.php');
require_once(LIB.'/auth.php');

// authenticate
if (!empty($_POST['submit'])) {
    if ($auth = auth_mysql($_POST['username'],$_POST['password'])) {
        auth_create_session($auth);
        header('Location: '.PROTOCOL.'://'.$_SERVER['HTTP_HOST'].WEBPATH.'/admin/');
        exit;
    } else {
        $msg = 'Authentication failed.  Please check username and password and try again.';
    }
}

$title='Mozilla Mirror Manager Login';
$body_tags=' onload="document.getElementById(\'username\').focus();" ';
require_once(HEADER);
?>
<h1>Mozilla Mirror Manager Login</h1>
<?=(!empty($msg))?'<pre>'.$msg.'</pre>':null?>
<form name="form" id="form" method="post" action="./login.php" >
<div>
    <label for="username">Username:</label>
    <input type="text" name="username" id="username" size="30" maxlength="100" />
</div>
<br />
<div>
    <label for="password">Password:</label>
    <input type="password" name="password" id="password" size="30" maxlength="100" />
</div>
<br />
<input type="submit" name="submit" id="submit" class="button" value="Log In" />
</form>
<?php
require_once(FOOTER);
?>
