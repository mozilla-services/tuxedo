<?php
/**
 *  Main handler.
 *  @package mirror
 *	@subpackage pub
 */
error_reporting(0);  // hide all errors
require_once('./cfg/config.php');  // config file that defines constants

function show_no_cache_headers() {
    header('Cache-Control: no-store, no-cache, must-revalidate, post-check=0, pre-check=0, private');
    header('Pragma: no-cache');
}

// if we don't have an os, make it windows, playing the odds
if (empty($_GET['os'])) {
    $_GET['os'] = 'win';
}

// do we even have a product?
if (!empty($_GET['product'])) {
    require_once(LIB.'/db.php');  // core mysql wrappers
    $conn = db_connect(DBHOST,DBUSER,DBPASS);  // open persistent connection to db

    // if we don't have a db connection, show them the gonefishing page
    if ($conn == false) { 
        require_once('./gonefishing.php'); 
        exit;
    } else {
        db_select(DBNAME);  // select db
    }

    // clean in os and product strings
    $os_name = mysql_real_escape_string(trim(strtolower($_GET['os'])));
    $product_name = mysql_real_escape_string(trim(strtolower($_GET['product'])));

    // get os and product IDs
    $os_id = db_name_to_id('mirror_os','os_id','os_name',$os_name);
    $product_id = db_name_to_id('mirror_products','product_id','product_name',$product_name);

    // do we have a valid os and product?
    if (!empty($os_id)&&!empty($product_id)) {
        $location = db_get_one("SELECT location_id,location_path FROM mirror_locations WHERE product_id={$product_id} AND os_id={$os_id}");

        // did we get a valid location?
        if (!empty($location)) {
            $mirror = db_get_one("SELECT mirror_mirrors.mirror_id,mirror_baseurl FROM mirror_mirrors, mirror_location_mirror_map WHERE mirror_mirrors.mirror_id = mirror_location_mirror_map.mirror_id AND mirror_location_mirror_map.location_id = {$location['location_id']} AND mirror_active='1' AND location_active ='1' ORDER BY rand()*(1/mirror_rating)");

            // did we get a valid mirror?
            if (!empty($mirror)) {

                // if logging is enabled, insert log
                if (LOGGING) {
                    db_query("UPDATE mirror_mirrors SET mirror_count=mirror_count+1 WHERE mirror_id={$mirror['mirror_id']}");
                    db_query("UPDATE mirror_products SET product_count=product_count+1 WHERE product_id={$product_id}");
                }
                
                // LANGUAGE HACK
                if (!empty($_GET['lang'])) {
                    $location['location_path'] = str_replace('en-US',$_GET['lang'],$location['location_path']);
                }

                // if we are just testing, then just print and exit.
                if (!empty($_GET['print'])) {
                    show_no_cache_headers();
                    print(htmlentities('Location: '.$mirror['mirror_baseurl'].$location['location_path']));
                    exit;
                }

                // otherwise, by default, redirect them and exit
                show_no_cache_headers();
                header('Location: '.$mirror['mirror_baseurl'].$location['location_path']);
                exit;
            }
        }
    }
}

// if we get here, the request was invalid; redirect to mozilla home
show_no_cache_headers();
header('Location: http://www.mozilla.org/');
exit;
?>
