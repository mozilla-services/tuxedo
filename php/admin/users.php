<?php
/**
 *  Users.
 *  @package mirror
 *  @subpackage admin
 */
$protect=1;  // protect this page
require_once('../cfg/init.php');

// add user 
if (!empty($_POST['add-submit'])&&!empty($_POST['username'])&&!empty($_POST['password'])&&!empty($_POST['rpassword'])) {
    if (mirror_insert_user($_POST['username'],$_POST['password'],$_POST['rpassword'],$_POST['user_firstname'],$_POST['user_lastname'],$_POST['user_email'])) {
        set_msg('User added successfully.');
        header('Location: '.PROTOCOL.'://'.$_SERVER['HTTP_HOST'].WEBPATH.'/admin/users.php');
        exit;
    } else {
        set_error('User could not be added because of an unknown error.');
    }
}

// process actions
if (!empty($_POST['submit'])) {
    if (!empty($_POST['user_id'])) {
        switch($_POST['action']) {
            case 'edit':
                if (!empty($_POST['doit'])) {
                    if (mirror_update_user($_POST['user_id'],$_POST['username'],$_POST['password'],$_POST['rpassword'],$_POST['user_firstname'],$_POST['user_lastname'],$_POST['user_email'])) {
                        set_msg('User updated successfully.');
                        header('Location: '.PROTOCOL.'://'.$_SERVER['HTTP_HOST'].WEBPATH.'/admin/users.php');
                        exit;
                    } else {
                        set_error('User update failed.');
                    }
                } else {
                    $title = 'Edit User';
                    $nav = INC.'/admin_nav.php';
                    require_once(HEADER);
                    echo '<h2>Edit User</h2>';
                    $posts = mirror_get_one_user($_POST['user_id']);
                    form_start();
                    include_once(INC.'/forms/user.php');
                    form_hidden('doit','1');
                    form_hidden('action','edit');
                    form_hidden('user_id',$_POST['user_id']);
                    form_submit('submit','','button1','Update');
                    form_end();
                    require_once(FOOTER);
                    exit;
                }
                break;
            case 'delete':
                if ($_POST['user_id']==$_SESSION['user']['user_id']) {
                    set_error('You cannot delete yourself.');
                } elseif (mirror_delete_user($_POST['user_id'])) {
                    set_msg('User deleted successfully.');
                } else {
                    set_error('User could not be deleted because of an error.');
                }
                break;
        }
    } else {
        set_error('You must select a user to continue.');
    }
}

$title = 'Users';
$nav = INC.'/admin_nav.php';
require_once(HEADER);
echo '<h2>Users</h2>';

show_error();
show_msg();

$users = mirror_get_users();

$_GET['sort'] = (!empty($_GET['sort']))?$_GET['sort']:'user_lastname';
$_GET['order'] = (!empty($_GET['order']))?$_GET['order']:'ASC';
$users = array_order_by($users,$_GET['sort'],$_GET['order']);

$headers = array(
    'user_id'=>'',
    'user_lastname'=>'Last',
    'user_firstname'=>'First',
    'user_email'=>'Email',
    'username'=>'Username'
);

$actions = array(
    'edit'=>'Edit',
    'delete'=>'Delete'
);

form_start();
show_list($users,$headers,'radio',$actions);
form_end();

echo '<h2>Add a User</h2>';
form_start();
include_once(INC.'/forms/user.php');
form_submit('add-submit','','button1','Add User');
form_end();

require_once(FOOTER);
?>
