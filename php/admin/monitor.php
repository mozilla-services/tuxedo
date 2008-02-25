<?php
/**
 *  Monitor product status.
 *  @package mirror
 *  @subpackage admin
 */
$protect=1;  // protect this page
require_once('../cfg/init.php');
require_once('../lib/csv.php');

$product = isset($_GET['q']) ? mysql_real_escape_string($_GET['q']) : null;

if (!empty($product)) {
    $stats = db_get("
    SELECT 
    SUM( m.mirror_rating ) as available,
    (
        SELECT SUM( mirror_rating )
        FROM mirror_mirrors
        WHERE mirror_active = '1' 
    ) as total,
    (   100 * SUM( m.mirror_rating )/
        (
            SELECT SUM( mirror_rating )
            FROM mirror_mirrors
            WHERE mirror_active = '1' 
        )
    ) as percentage,
    p.product_name as product_name,
    o.os_name as os_name
    FROM mirror_mirrors m
    JOIN mirror_location_mirror_map lmm ON lmm.mirror_id = m.mirror_id
    JOIN mirror_locations l ON l.location_id = lmm.location_id
    JOIN mirror_products p ON p.product_id = l.product_id
    JOIN mirror_os o ON o.os_id = l.os_id
    WHERE lmm.location_active = '1'
    AND p.product_name LIKE '%{$product}%'
    GROUP BY lmm.location_id
    ",MYSQL_ASSOC);

    $_GET['sort']=(!empty($_GET['sort']))?$_GET['sort']:'product_name';
    $_GET['order']=(!empty($_GET['order']))?$_GET['order']:'ASC';
    $stats=array_order_by($stats,$_GET['sort'],$_GET['order']);

    $headers = array(
        'product_name'=>'Product',
        'os_name'=>'OS',
        'available'=>'Available',
        'total'=>'Total',
        'percentage'=>'Percentage'
    );

    // should we export to csv?
    if (!empty($_GET['csv'])) {
        $csv = array();
        $csv[] = $headers;
        foreach ($stats as $row) {
            $csv[] = $row;
        }
        send_csv($csv);
        exit;
    }
}

$title = 'Product Uptake';
$nav = INC.'/admin_nav.php';
require_once(HEADER);
echo '<h2>Product Uptake</h2>';

echo '<p>Type in a product to see its status on the network.</p>';
echo '<form method="get" action="./monitor.php">';
echo '<input type="text" name="q" size="20"/>';
echo '<input type="submit" value="Go"/>';
echo '</form>';

if (!empty($stats)) {
    echo '<h2>Results</h2>';
    show_list($stats,$headers,'simple');
    echo '<p><a href="./monitor.php?csv=1&amp;sort='.$_GET['sort'].'&amp;order='.$_GET['order'].'&amp;q='.$product.'">Save this page as CSV &raquo;</a></p>';
}

require_once(FOOTER);
?>
