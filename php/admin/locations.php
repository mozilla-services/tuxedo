<?php
/**
 *  File locations.
 *  @package mirror
 *  @subpackage admin
 */
$protect=1;  // protect this page
require_once('../cfg/init.php');

// add mirror 
if (!empty($_POST['add-submit'])&&!empty($_POST['location_path'])) {
    if (mirror_insert_location($_POST['product_id'],$_POST['os_id'],$_POST['location_path'])) {
        set_msg('Location added successfully.');
        header('Location: '.PROTOCOL.'://'.$_SERVER['HTTP_HOST'].WEBPATH.'/admin/locations.php');
        exit;
    } else {
        set_error('Location could not be added because of an unknown error.');
    }
}

// process actions
if (!empty($_POST['submit'])) {
    if (!empty($_POST['location_id'])) {
        switch($_POST['action']) {
            case 'edit':
                if (!empty($_POST['doit'])) {
                    if (mirror_update_location($_POST['location_id'],$_POST['product_id'],$_POST['os_id'],$_POST['location_path'])) {
                        set_msg('Location updated successfully.');
                        header('Location: '.PROTOCOL.'://'.$_SERVER['HTTP_HOST'].WEBPATH.'/admin/locations.php');
                        exit;
                    } else {
                        set_error('Location update failed.');
                    }
                } else {
                    $title = 'Edit Location';
                    $nav = INC.'/admin_nav.php';
                    require_once(HEADER);
                    echo '<h2>Edit Location</h2>';
                    $posts = mirror_get_one_location($_POST['location_id']);
                    form_start();
                    include_once(INC.'/forms/location.php');
                    form_hidden('doit','1');
                    form_hidden('action','edit');
                    form_hidden('location_id',$_POST['location_id']);
                    form_submit('submit','','button1','Update');
                    form_end();
                    require_once(FOOTER);
                    exit;
                }
                break;
            case 'delete':
                if (mirror_delete_location($_POST['location_id'])) {
                    set_msg('Location deleted successfully.');
                } else {
                    set_error('Location could not be deleted.');
                }
                break;
        }
    } else {
        set_error('You must select a mirror to continue.');
    }
}

$title = 'Locations';
$nav = INC.'/admin_nav.php';
require_once(HEADER);
echo '<h2>Locations</h2>';
show_error();
show_msg();

$locations = mirror_get_locations();

$_GET['sort'] = (!empty($_GET['sort']))?$_GET['sort']:'product_name';
$_GET['order'] = (!empty($_GET['order']))?$_GET['order']:'ASC';
$locations = array_order_by($locations,$_GET['sort'],$_GET['order']);

$headers = array(
    'location_id'=>'',
    'product_name'=>'Product',
    'os_name'=>'OS',
    'location_path'=>'Path'
);

$actions = array(
    'edit'=>'Edit',
    'delete'=>'Delete'
);

form_start();
show_list($locations,$headers,'radio',$actions);
form_end();

echo '<h2>Add a Location</h2>';
form_start();
include_once(INC.'/forms/location.php');
form_submit('add-submit','','button1','Add Location');
form_end();

require_once(FOOTER);
?>
