<?php
/**
 *  Location Statistics.
 *  @package mirror
 *  @subpackage admin
 */
$protect=1;  // protect this page
require_once('../cfg/init.php');

$stats = db_get("
    SELECT
        IF(mirror_location_mirror_map.location_active='0','DISABLED','ok') as location_active,
        mirror_name,
        mirror_baseurl,
        location_path
    FROM
        mirror_mirrors,
        mirror_location_mirror_map,
        mirror_locations
    WHERE
        mirror_mirrors.mirror_id = mirror_location_mirror_map.mirror_id AND
        mirror_locations.location_id = mirror_location_mirror_map.location_id
",MYSQL_ASSOC);

$_GET['sort']=(!empty($_GET['sort']))?$_GET['sort']:'location_active';
$_GET['order']=(!empty($_GET['order']))?$_GET['order']:'ASC';
$stats=array_order_by($stats,$_GET['sort'],$_GET['order']);

$headers = array(
    'location_active'=>'Status',
    'mirror_name'=>'Host Name',
    'mirror_baseurl'=>'Address',
    'location_path'=>'Path'
);

// should we export to csv?
if (!empty($_GET['csv'])) {
    $csv = array();
    $csv[] = $headers;
    foreach ($stats as $row) {
    	$csv[] = $row;
    }
    csv_send_csv($csv);
    exit;
}

$title = 'Location Statistics';
$nav = INC.'/admin_nav.php';
require_once(HEADER);
echo '<h2>Location Statistics</h2>';

echo '<p>This shows whether or not a server is serving up Firefox.</p>';

show_list($stats,$headers,'simple');

echo '<p><a href="./lstats.php?csv=1&amp;sort='.$_GET['sort'].'&amp;order='.$_GET['order'].'">Save this page as CSV &raquo;</a></p>';

require_once(FOOTER);
?>
