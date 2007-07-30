<?php
/**
 * RSS 2.0 feed for download counts.
 * @package mirror
 * @subpackage rss
 */

require_once('../cfg/config.php');  // config file
require_once(LIB.'/db.php');  // core mysql wrappers

db_connect(DBHOST,DBUSER,DBPASS);  // open persistent connection to db
db_select(DBNAME);  // select db

// get download counts per product
$data = db_get("SELECT * FROM mirror_products ORDER BY product_name");

// time to go at the end of each item
$now = date('G',time());

// content headers, replace Content-type if already set
header('Content-type: text/xml', true);
echo '<?xml version="1.0"?>'."\n\n";

// doctype
echo '<rdf:RDF'."\n"; 
echo '    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"'."\n";
echo '    xmlns="http://purl.org/rss/1.0/">'."\n\n";

// channel details
echo '<channel rdf:about="http://download.mozilla.org/rss/download-counts.php">'."\n";
echo '    <title>Mozilla Download Counts</title>'."\n";  
echo '    <link>http://mozilla.org/</link>'."\n";  
echo '    <description>Mozilla product download counts pulled from Bouncer database.</description> '."\n";

// item listing
echo '    <items>'."\n";
echo '        <rdf:Seq>'."\n";
foreach ($data as $product) {
    echo '            <rdf:li rdf:resource="http://download.mozilla.org/?product='.$product['product_name'].'&amp;lastmod='.$now.'"/>'."\n";
}
echo '        </rdf:Seq>'."\n";
echo '    </items>'."\n";
echo '</channel>'."\n\n";

// item details
foreach ($data as $product) {
    echo '<item rdf:about="http://download.mozilla.org/?product='.$product['product_name'].'&amp;lastmod='.$now.'">'."\n";
    echo '    <title>'.$product['product_name'].'</title>'."\n";
    echo '    <description>'.$product['product_count'].'</description>'."\n";
    echo '    <link>http://download.mozilla.org/?product='.$product['product_name'].'&amp;lastmod='.$now.'</link>'."\n";
    echo '</item>'."\n";
}

echo "\n".'</rdf:RDF>';
?>
