<?php
/**
 *  Regions.
 *  @package mirror
 *  @subpackage admin
 */
$protect=1;  // protect this page
require_once('../cfg/init.php');

if (!empty($_GET['os_id'])&&!empty($_GET['product_id'])) {

    $os_id = intval($_GET['os_id']);
    $product_id = intval($_GET['product_id']);

    $mirrors = db_get("
        SELECT DISTINCT
            mirror_baseurl 
        FROM 
            mirror_mirrors 
        INNER JOIN
            mirror_location_mirror_map
        ON
            mirror_location_mirror_map.mirror_id = mirror_mirrors.mirror_id
        INNER JOIN
            mirror_locations
        ON
            mirror_location_mirror_map.location_id = mirror_locations.location_id
        WHERE
            mirror_locations.os_id = {$os_id} AND
            mirror_locations.product_id = {$product_id} AND
            mirror_location_mirror_map.location_active = '1' AND
            mirror_mirrors.mirror_active = '1'
        ");

    header("Content-type: text/plain;");
    foreach ($mirrors as $mirror) {
        echo $mirror['mirror_baseurl']."\n";
    }
    exit;

} else {

    $title = 'Mirror Listing';
    require_once(HEADER);
    echo '<h1>Mirror List</h1>';
    echo '<p>Use this form to get a list of all mirrors serving up active files
    for the selected Product/OS.</p>';
    form_start('list','list','get','./mirror-list.php');
    echo '<div>';
    form_label('Product', 'product','label-small');
    form_select('product_id','product','',mirror_get_products_select(),$posts['product_id']);
    echo ' [<a href="./products.php">edit products</a>]';
    echo '</div><br />';

    echo '<div>';
    form_label('OS', 'os','label-small');
    form_select('os_id','os','',mirror_get_oss_select(),$posts['os_id']);
    echo ' [<a href="./os.php">edit operating systems</a>]';
    echo '</div><br />';
    form_submit('submit','','button1','Update');
    form_end();
    require_once(FOOTER);
}
?>
