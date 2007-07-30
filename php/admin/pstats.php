<?php
/**
 *  Product Statistics.
 *  @package mirror
 *  @subpackage admin
 */
$protect=1;  // protect this page
require_once('../cfg/init.php');

$title = 'Product Statistics';
$nav = INC.'/admin_nav.php';
require_once(HEADER);
echo '<h2>Product Statistics</h2>';

$stats = mirror_get_product_stats();

$_GET['sort']=(!empty($_GET['sort']))?$_GET['sort']:'count';
$_GET['order']=(!empty($_GET['order']))?$_GET['order']:'DESC';
$stats=array_order_by($stats,$_GET['sort'],$_GET['order']);

$headers = array(
    'count'=>'Hits',
    'product_name'=>'Product'
);

show_list($stats,$headers,'simple');

require_once(FOOTER);
?>
