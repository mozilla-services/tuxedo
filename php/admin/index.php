<?php
/**
 *  Regions.
 *  @package mirror
 *  @subpackage admin
 */
$protect=1;  // protect this page
require_once('../cfg/init.php');

// add mirror 
if (!empty($_POST['add-submit'])) {
    if (mirror_insert_mirror($_POST['mirror_name'],$_POST['region_id'],$_POST['mirror_baseurl'],$_POST['mirror_rating'])) {
        set_msg('Mirror added successfully.');
        header('Location: http://'.$_SERVER['HTTP_HOST'].WEBPATH.'/admin/');
        exit;
    } else {
        set_error('Mirror could not be added because of an unknown error.');
    }
}

// process actions
if (!empty($_POST['submit'])) {
    if (!empty($_POST['mirror_id'])) {
        switch($_POST['action']) {
            case 'edit':
                if (!empty($_POST['doit'])) {
                    if (mirror_update_mirror($_POST['mirror_id'],$_POST['mirror_name'],$_POST['region_id'],$_POST['mirror_baseurl'],$_POST['mirror_rating'])) {
                        set_msg('Mirror updated successfully.');
                        header('Location: http://'.$_SERVER['HTTP_HOST'].WEBPATH.'/admin/');
                        exit;
                    } else {
                        set_error('Mirror update failed.');
                    }
                } else {
                    $title = 'Edit Mirror';
                    $nav = INC.'/admin_nav.php';
                    require_once(HEADER);
                    echo '<h2>Edit Mirror</h2>';
                    $posts = mirror_get_one_mirror($_POST['mirror_id']);
                    form_start();
                    include_once(INC.'/forms/mirror.php');
                    form_hidden('doit','1');
                    form_hidden('action','edit');
                    form_hidden('mirror_id',$_POST['mirror_id']);
                    form_submit('submit','','button1','Update');
                    form_end();
                    require_once(FOOTER);
                    exit;
                }
                break;
            case 'delete':
                if (mirror_delete_mirror($_POST['mirror_id'])) {
                    set_msg('Mirror deleted successfully.');
                } else {
                    set_error('Mirror could not be deleted.');
                }
                break;
            case 'toggle':
                if (mirror_toggle($_POST['mirror_id'])) {
                    set_msg('Mirror enabled/disabled.');
                } else {
                    set_error('Mirror could not be enabled/disabled.');
                }
        }
    } else {
        set_error('You must select a mirror to continue.');
    }
}

$title = 'Mirrors';
$nav = INC.'/admin_nav.php';
require_once(HEADER);
echo '<h2>Mirrors</h2>';

show_error();
show_msg();

$mirrors = mirror_get_mirrors();

$_GET['sort']=(!empty($_GET['sort']))?$_GET['sort']:'mirror_active';
$_GET['order']=(!empty($_GET['order']))?$_GET['order']:'ASC';
$mirrors=array_order_by($mirrors,$_GET['sort'],$_GET['order']);

$headers = array(
    'mirror_id'=>'',
    'mirror_active'=>'Status',
    'mirror_rating'=>'Rating',
    'mirror_name'=>'Host Name',
    'mirror_baseurl'=>'Address',
    'region_name'=>'Region',
    'mirror_count'=>'Hits'
);

$actions = array(
    'toggle'=>'Enable/Disable',
    'edit'=>'Edit',
    'delete'=>'Delete'
);

form_start();
show_list($mirrors,$headers,'radio',$actions);
form_end();

echo '<h2>Add a Mirror</h2>';
form_start();
include_once(INC.'/forms/mirror.php');
form_submit('add-submit','','button1','Add Mirror');
form_end();

require_once(FOOTER);
?>
