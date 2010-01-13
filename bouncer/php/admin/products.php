<?php
/**
 *  Products.
 *  @package mirror
 *  @subpackage admin
 */
$protect=1;  // protect this page
require_once('../cfg/init.php');

// add product
if (!empty($_POST['add-submit'])&&!empty($_POST['product_name'])) {
    if (mirror_insert_product($_POST['product_name'],$_POST['product_priority'])) {
        set_msg('Product added successfully.');
        header('Location: '.PROTOCOL.'://'.$_SERVER['HTTP_HOST'].WEBPATH.'/admin/products.php');
        exit;
    } else {
        set_error('Product could not be added because of an unknown error.');
    }
}

// process actions
if (!empty($_POST['submit'])) {
    if (!empty($_POST['product_id'])) {
        switch($_POST['action']) {
            case 'edit':
                if (!empty($_POST['doit'])) {
                    if (mirror_update_product($_POST['product_id'],$_POST['product_name'],$_POST['product_priority'])) {
                        set_msg('Product updated successfully.');
                        header('Location: '.PROTOCOL.'://'.$_SERVER['HTTP_HOST'].WEBPATH.'/admin/products.php');
                        exit;
                    } else {
                        set_error('Product update failed.');
                    }
                } else {
                    $title = 'Edit Product';
                    $nav = INC.'/admin_nav.php';
                    require_once(HEADER);
                    echo '<h2>Edit Product</h2>';
                    $posts = mirror_get_one_product($_POST['product_id']);
                    form_start();
                    include_once(INC.'/forms/product.php');
                    form_hidden('doit','1');
                    form_hidden('action','edit');
                    form_hidden('product_id',$_POST['product_id']);
                    form_submit('submit','','button1','Update');
                    form_end();
                    require_once(FOOTER);
                    exit;
                }
                break;
            case 'delete':
                if (!record_exists('mirror_locations','product_id',$_POST['product_id'])&&mirror_delete_product($_POST['product_id'])) {
                    set_msg('Product deleted successfully.');
                } else {
                    set_error('Product cannot be deleted because it is being used by a file location.');
                }
                break;
            case 'check':
                if (product_toggle($_POST['product_id'])) {
                    set_msg('Product flagged for immediate checking..');
                } else {
                    set_error('Product could not be flagged for immediate checking.');
                }
                break;
        }
    } else {
        set_error('You must select a product to continue.');
    }
}

$title = 'Products';
$nav = INC.'/admin_nav.php';
require_once(HEADER);
echo '<h2>Products</h1>';

show_error();
show_msg();

$products = mirror_get_products();

$_GET['sort']=(!empty($_GET['sort']))?$_GET['sort']:'product_name';
$_GET['order']=(!empty($_GET['order']))?$_GET['order']:'ASC';
$products=array_order_by($products,$_GET['sort'],$_GET['order']);

$headers = array(
    'product_id'=>'',
    'product_name'=>'Product Name',
    'product_count'=>'Downloads',
    'product_checknow'=>'Check Now?'
);

$actions = array(
    'check'=>'Check Now!',
    'edit'=>'Edit',
    'delete'=>'Delete'
);

form_start();
show_list($products,$headers,'radio',$actions);
form_end();

echo '<h2>Add a Product</h2>';
form_start();
include_once(INC.'/forms/product.php');
form_submit('add-submit','','button1','Add Product');
form_end();

require_once(FOOTER);
?>
