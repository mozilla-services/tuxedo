<?php
/**
 *  Mirror Statistics.
 *  @package mirror
 *  @subpackage admin
 */
$protect=1;  // protect this page
require_once('../cfg/init.php');

$title = 'Mirror Statistics';
$nav = INC.'/admin_nav.php';
require_once(HEADER);
echo '<h2>Mirror Statistics</h2>';

$stats = mirror_get_mirror_stats();

$_GET['sort']=(!empty($_GET['sort']))?$_GET['sort']:'count';
$_GET['order']=(!empty($_GET['order']))?$_GET['order']:'DESC';
$stats=array_order_by($stats,$_GET['sort'],$_GET['order']);

$headers = array(
    'count'=>'Hits',
    'mirror_rating'=>'Rating',
    'mirror_name'=>'Host Name',
    'mirror_baseurl'=>'Address',
    'region_name'=>'Region'
);

show_list($stats,$headers,'simple');

require_once(FOOTER);
?>
