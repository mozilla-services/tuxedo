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
    $success = true;
    if (empty($_POST['langs']))
        // language-independent
        $success = mirror_insert_location($_POST['product_id'],$_POST['os_id'],null,$_POST['location_path']);
    else {
        // support multiple languages
        $loc_replace = (strpos($_POST['location_path'], '%LANG') !== 0); // placeholder replacement necessary?
        foreach ($_POST['langs'] as $_lang) {
            if ($loc_replace) {
                // replace language placeholder in location path
                $_langname = mirror_get_one_lang($_lang);
                $_loc = str_replace('%LANG%', $_langname['lang'], $_POST['location_path']);
            }
            $success = mirror_insert_location($_POST['product_id'],$_POST['os_id'],$_lang,$_loc) && $success;
        }
    }
    if ($success) {
        set_msg('Location added successfully.');
        header('Location: http://'.$_SERVER['HTTP_HOST'].WEBPATH.'/admin/locations.php');
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
                    if (mirror_update_location($_POST['location_id'],$_POST['product_id'],$_POST['os_id'],$_POST['lang_id'],$_POST['location_path'])) {
                        set_msg('Location updated successfully.');
                        header('Location: http://'.$_SERVER['HTTP_HOST'].WEBPATH.'/admin/locations.php');
                        exit;
                    } else {
                        set_error('Location update failed.');
                    }
                } else {
                    $title = 'Edit Location';
                    $nav = INC.'/admin_nav.php';
                    require_once(HEADER);
                    echo '<h2>Edit Location</h2>';
                    $loc_id = $_POST['location_id'][0];
                    $posts = mirror_get_one_location($loc_id);
                    form_start();
                    include_once(INC.'/forms/location-edit.php');
                    form_hidden('doit','1');
                    form_hidden('action','edit');
                    form_hidden('location_id',$loc_id);
                    form_submit('submit','','button1','Update');
                    form_end();
                    require_once(FOOTER);
                    exit;
                }
                break;
            case 'delete':
                // delete all selected items
                $delete_success = true;
                foreach ($_POST['location_id'] as $loc_id)
                    $delete_success = (mirror_delete_location($loc_id) && $delete_success);
                
                if ($delete_success) {
                    set_msg('Location(s) deleted successfully.');
                } else {
                    set_error('Location(s) could not be deleted.');
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
    'lang'=>'Language',
    'location_path'=>'Path'
);

$actions = array(
    'edit'=>'Edit',
    'delete'=>'Delete'
);

/* javascript to ask before (bulk) deleting entries */
reset($headers); // jump to the first header
$cb_arrayname = key($headers) . '[]'; // fetch the checkbox array name
echo <<<EOJS
<script type="text/javascript">
<!--
function askEditDelete() {
    var checkCount = countCheckboxes('{$cb_arrayname}');
    var actionBox = document.getElementById('action');
    var action = actionBox.value;

    if (checkCount == 0) {
        alert('Please select at least one item.');
        return false;
    }

    switch (action) {
    case 'edit':
        if (checkCount > 1) {
            alert('Please only select one location to be edited at a time.');
            return false;
        } else
            return true;
    case 'delete':
        var confirmDelete = confirm('Do you really want to delete the '+checkCount+' selected item(s)?');
        return confirmDelete;
    default:
        return true; break;
    }

    return true;
}
// -->
</script>
EOJS;

form_start('form', null, 'post', null, 'onSubmit="return askEditDelete();"');
show_list($locations,$headers,'checkbox',$actions);
form_end();

echo '<h2>Add a Location</h2>';
form_start();
include_once(INC.'/forms/location.php');
form_submit('add-submit','','button1','Add Location');
form_end();

require_once(FOOTER);
?>
