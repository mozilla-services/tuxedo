<?php
/**
 *  Home-cooked auth libraries - because PEAR is fat.
 *  @package mirror
 *  @subpackage lib
 *  @todo re-enforce one-per-user session limit
 */

/**
 *  Check admin session against sessions table in database.
 *  @return bool
 */
function auth_is_valid_session()
{
    if (!empty($_COOKIE['mozilla-mirror-admin'])) {  // check cookie
        $res = db_query("SELECT * FROM mirror_sessions WHERE session_id = '{$_COOKIE['mozilla-mirror-admin']}'");  // check db for id
        if ($res && db_numrows($res)>0) {
            $buf = db_fetch($res,MYSQL_ASSOC);
            // comment line below to disable gc and allow multiple sessions per username
            db_query("DELETE FROM mirror_sessions WHERE username='{$buf['username']}' AND session_id != '{$_COOKIE['mozilla-mirror-admin']}'");  // garbage collection
            $user = db_fetch(db_query("SELECT * FROM mirror_users WHERE username='{$buf['username']}'"),MYSQL_ASSOC);
            if (empty($_SESSION)) {
                auth_create_session($user);  // if session isn't started, create it and push user data
            }
            return true;
        }
    }
    return false;
}

/**
 *  Authentication a user.
 *  @param string $username
 *  @param string $password
 *  @return array|bool array containing user data or false on failure
 */
function auth_mysql($username,$password)
{
    if (empty($username)||empty($password)) {
        return false;
    } 
    $username = trim(strip_tags(addslashes($username)));
    $password = trim(strip_tags(addslashes($password)));
    $res = db_query("SELECT * FROM mirror_users WHERE username='{$username}' AND password=MD5('{$password}')");
    if ($res && db_numrows($res)>0) {
        return db_fetch($res,MYSQL_ASSOC);
    } else {
        return false;
    }
}

/**
 *  Start a valid session.
 *  @param array $user array containing user information.
 */
function auth_create_session($user,$secure=0)
{
    session_name('mozilla-mirror-admin');
    session_set_cookie_params(0,'/',$_SERVER['HTTP_HOST'],$secure);
    session_start();
    db_query("INSERT INTO mirror_sessions(session_id,username) VALUES('".session_id()."','{$user['username']}')");
    $_SESSION['user']=$user;
}

/**
 *  Logout.
 */
function auth_logout()
{
    // comment line below to keep gc from deleting other sessions for this user
    db_query("DELETE FROM mirror_sessions WHERE session_id='{$_COOKIE['mozilla-mirror-admin']}' OR username='{$_SESSION['user']['username']}'");
    $_COOKIE = array(); 
    $_SESSION = array();
}
?>
