<?php
/**
 *  Languages.
 *  @package mirror
 *  @subpackage admin
 */
$protect=1;  // protect this page
require_once('../cfg/init.php');

// add language
if (!empty($_POST['add-submit']) && !empty($_POST['language'])) {
    if (mirror_insert_lang($_POST['language'])) {
        set_msg('Language added successfully.');
        header('Location: http://'.$_SERVER['HTTP_HOST'].WEBPATH.'/admin/langs.php');
        exit;
    } else {
        set_error('Language could not be added because of an unknown error.');
    }
}

// process actions
if (!empty($_POST['submit'])) {
    if (!empty($_POST['lang_id'])) {
        switch($_POST['action']) {
            case 'edit':
                if (!empty($_POST['doit'])) {
                    if (mirror_update_lang($_POST['lang_id'], $_POST['lang'])) {
                        set_msg('Language updated successfully.');
                        header('Location: http://'.$_SERVER['HTTP_HOST'].WEBPATH.'/admin/langs.php');
                        exit;
                    } else {
                        set_error('Language update failed.');
                    }
                } else {
                    $title = 'Edit Language';
                    $nav = INC.'/admin_nav.php';
                    require_once(HEADER);
                    echo '<h2>Edit Language</h2>';
                    $posts = mirror_get_one_lang($_POST['lang_id']);
                    form_start();
                    include_once(INC.'/forms/langs.php');
                    form_hidden('doit','1');
                    form_hidden('action','edit');
                    form_hidden('lang_id', $_POST['lang_id']);
                    form_submit('submit','','button1','Update');
                    form_end();
                    require_once(FOOTER);
                    exit;
                }
                break;
            case 'delete':
                if (mirror_delete_lang($_POST['lang_id'])) {
                    set_msg('Language deleted successfully.');
                } else {
                    set_error('Language could not be deleted.');
                }
                break;
        }
    } else {
        set_error('You must select a language to continue.');
    }
}

$title = 'Languages';
$nav = INC.'/admin_nav.php';
require_once(HEADER);
echo '<h2>Languages</h2>';

show_error();
show_msg();

$langs = mirror_get_langs();

$_GET['sort'] = (!empty($_GET['sort'])) ? $_GET['sort'] : 'lang';
$_GET['order'] = (!empty($_GET['order'])) ? $_GET['order'] : 'ASC';
$langs = array_order_by($langs, $_GET['sort'], $_GET['order']);

$headers = array(
    'lang_id' => '',
    'lang' => 'Language',
);

$actions = array(
    'edit' => 'Edit',
    'delete' => 'Delete'
);

form_start();
show_list($langs, $headers, 'radio', $actions);
form_end();

echo '<h2>Add a Language</h2>';
form_start();
include_once(INC.'/forms/langs.php');
form_submit('add-submit','','button1','Add Language');
form_end();

require_once(FOOTER);
?>
