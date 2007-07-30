<?php
/**
 *  Regions.
 *  @package mirror
 *  @subpackage admin
 */
$protect=1;  // protect this page
require_once('../cfg/init.php');

// add region
if (!empty($_POST['add-submit'])&&!empty($_POST['region_name'])) {
    if (mirror_insert_region($_POST['region_name'],$_POST['region_priority'])) {
        set_msg('Region added successfully.');
        header('Location: http://'.$_SERVER['HTTP_HOST'].WEBPATH.'/admin/regions.php');
        exit;
    } else {
        set_error('Region could not be added because of an unknown error.');
    }
}

// process actions
if (!empty($_POST['submit'])) {
    if (!empty($_POST['region_id'])) {
        switch($_POST['action']) {
            case 'edit':
                if (!empty($_POST['doit'])) {
                    if (mirror_update_region($_POST['region_id'],$_POST['region_name'],$_POST['region_priority'])) {
                        set_msg('Region updated successfully.');
                        header('Location: http://'.$_SERVER['HTTP_HOST'].WEBPATH.'/admin/regions.php');
                        exit;
                    } else {
                        set_error('Region update failed.');
                    }
                } else {
                    $title = 'Edit Region';
                    $nav = INC.'/admin_nav.php';
                    require_once(HEADER);
                    echo '<h2>Edit Region</h2>';
                    $posts = mirror_get_one_region($_POST['region_id']);
                    form_start();
                    include_once(INC.'/forms/region.php');
                    form_hidden('doit','1');
                    form_hidden('action','edit');
                    form_hidden('region_id',$_POST['region_id']);
                    form_submit('submit','','button1','Update');
                    form_end();
                    require_once(FOOTER);
                    exit;
                }
                break;
            case 'delete':
                if (!record_exists('mirror_mirror_region_map','region_id',$_POST['region_id'])&&mirror_delete_region($_POST['region_id'])) {
                    set_msg('Region deleted successfully.');
                } else {
                    set_error('Region cannot be deleted because it is linked to a mirror.');
                }
                break;
        }
    } else {
        set_error('You must select a region to continue.');
    }
}

$title = 'Regions';
$nav = INC.'/admin_nav.php';
require_once(HEADER);
echo '<h2>Regions</h2>';

show_error();
show_msg();

$regions = mirror_get_regions();

$_GET['sort']=(!empty($_GET['sort']))?$_GET['sort']:'region_name';
$_GET['order']=(!empty($_GET['order']))?$_GET['order']:'ASC';
$regions=array_order_by($regions,$_GET['sort'],$_GET['order']);

$headers = array(
    'region_id'=>'',
    'region_name'=>'Region Name',
    'mirrors'=>'Mirrors',
    'region_priority'=>'Priority'
);

$actions = array(
    'edit'=>'Edit',
    'delete'=>'Delete'
);

form_start();
show_list($regions,$headers,'radio',$actions);
form_end();

echo '<h2>Add a Region</h2>';
form_start();
include_once(INC.'/forms/region.php');
form_submit('add-submit','','button1','Add Region');
form_end();

require_once(FOOTER);
?>
