<?php
/**
 *  Operating Systems.
 *  @package mirror
 *  @subpackage admin
 */
$protect=1;  // protect this page
require_once('../cfg/init.php');

// add os
if (!empty($_POST['add-submit'])&&!empty($_POST['os_name'])) {
    if (mirror_insert_os($_POST['os_name'],$_POST['os_priority'])) {
        set_msg('OS added successfully.');
        header('Location: '.PROTOCOL.'://'.$_SERVER['HTTP_HOST'].WEBPATH.'/admin/os.php');
        exit;
    } else {
        set_error('OS could not be added because of an unknown error.');
    }
}

// process actions
if (!empty($_POST['submit'])) {
    if (!empty($_POST['os_id'])) {
        switch($_POST['action']) {
            case 'edit':
                if (!empty($_POST['doit'])) {
                    if (mirror_update_os($_POST['os_id'],$_POST['os_name'],$_POST['os_priority'])) {
                        set_msg('OS updated successfully.');
                        header('Location: '.PROTOCOL.'://'.$_SERVER['HTTP_HOST'].WEBPATH.'/admin/os.php');
                        exit;
                    } else {
                        set_error('OS update failed.');
                    }
                } else {
                    $title = 'Edit OS';
                    $nav = INC.'/admin_nav.php';
                    require_once(HEADER);
                    echo '<h2>Edit OS</h2>';
                    $posts = mirror_get_one_os($_POST['os_id']);
                    form_start();
                    include_once(INC.'/forms/os.php');
                    form_hidden('doit','1');
                    form_hidden('action','edit');
                    form_hidden('os_id',$_POST['os_id']);
                    form_submit('submit','','button1','Update');
                    form_end();
                    require_once(FOOTER);
                    exit;
                }
                break;
            case 'delete':
                if (!record_exists('mirror_locations','os_id',$_POST['os_id'])&&mirror_delete_os($_POST['os_id'])) {
                    set_msg('OS deleted successfully.');
                } else {
                    set_error('OS cannot be deleted because it is being used by a file location.');
                }
                break;
        }
    } else {
        set_error('You must select a os to continue.');
    }
}

$title = 'Operating Systems';
$nav = INC.'/admin_nav.php';
require_once(HEADER);
echo '<h2>Operating Systems</h1>';

show_error();
show_msg();

$oss = mirror_get_oss();

$_GET['sort']=(!empty($_GET['sort']))?$_GET['sort']:'os_name';
$_GET['order']=(!empty($_GET['order']))?$_GET['order']:'ASC';
$oss=array_order_by($oss,$_GET['sort'],$_GET['order']);

$headers = array(
    'os_id'=>'',
    'os_name'=>'OS Name',
    'os_priority'=>'Priority'
);

$actions = array(
    'edit'=>'Edit',
    'delete'=>'Delete'
);

form_start();
show_list($oss,$headers,'radio',$actions);
form_end();

echo '<h2>Add a OS</h2>';
form_start();
include_once(INC.'/forms/os.php');
form_submit('add-submit','','button1','Add OS');
form_end();

require_once(FOOTER);
?>
