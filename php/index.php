<?php
/**
 *  Main handler.
 *  @package mirror
 *	@subpackage pub
 */
require_once('./cfg/config.php');  // config file that defines constants

/**
 * Echo proper headers for ensuring no caching of redirects.
 */
function show_no_cache_headers() {
    header('Cache-Control: no-store, no-cache, must-revalidate, post-check=0, pre-check=0, private');
    header('Pragma: no-cache');
}

/**
 * Get a random element from an array based on weighted array values.
 * @param array $array array of val => weight pairings
 * @param int $sum total of added weightings
 * @return bool value of randomly selected element
 */
function getRandElement( $array, $sum ) {
    $tot_prob = $sum;
    foreach ( $array as $element => $element_prob ) {
        if ( mt_rand( 1, $tot_prob ) <= $element_prob ) {
            return $element;
        } else {
            $tot_prob -= $element_prob;
        }
    }
    return 0;
}

// if we don't have an os, make it windows, playing the odds
if (empty($_GET['os'])) {
    $_GET['os'] = 'win';
}

// do we even have a product?
if (!empty($_GET['product'])) {

    // clean in os and product strings
    $os_name = trim(strtolower($_GET['os']));
    $product_name = trim(strtolower($_GET['product']));

    require_once(LIB.'/sdo.php');

    $sdo = new SDO();

    // get os and product IDs
    $os_id = $sdo->name_to_id('mirror_os','os_id','os_name',$os_name);
    $product_id = $sdo->name_to_id('mirror_products','product_id','product_name',$product_name);

    // do we have a valid os and product?
    if (!empty($os_id)&&!empty($product_id)) {
        $location = $sdo->get_one("
            SELECT
                location_id,
                location_path
            FROM
                mirror_locations
            WHERE
                product_id = %d AND 
                os_id = %d",array($product_id,$os_id));

        // did we get a valid location?
        if (!empty($location)) {
            $mirrors = $sdo->get("
                SELECT
                    mirror_mirrors.mirror_id,
                    mirror_baseurl,
                    mirror_rating
                FROM 
                    mirror_mirrors,
                    mirror_location_mirror_map
                WHERE
                    mirror_mirrors.mirror_id = mirror_location_mirror_map.mirror_id AND
                    mirror_location_mirror_map.location_id = %d AND
                    mirror_active='1' AND 
                    location_active ='1' 
                ORDER BY mirror_rating",array($location['location_id']),MYSQL_ASSOC,'mirror_id');

            $mirrors_rand = array();
            $sum = 0;
            foreach ($mirrors as $buf) {
                $mirrors_rand[$buf['mirror_id']] = $buf['mirror_rating'];
                $sum += $buf['mirror_rating'];
            }

            $mirror_rand_id = getRandElement($mirrors_rand, $sum);

            $mirror = $mirrors[$mirror_rand_id];

            // did we get a valid mirror?
            if (!empty($mirror)) {

                // if logging is enabled, insert log
                if (LOGGING) {
                    $sdo->query("UPDATE mirror_mirrors SET mirror_count=mirror_count+1 WHERE mirror_id = %d",array($mirror['mirror_id']));
                    $sdo->query("UPDATE mirror_products SET product_count=product_count+1 WHERE product_id = %d",array($product_id));
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

/**
 * If there are non-empty parameters, it is an unsuccessful request and the user
 * should get a 404 header response code.
 *
 * If they are all empty, we should redirect them to www.mozilla.org because
 * they are likely a user trying to access download.mozilla.org directly.
 */
if (!empty($_GET['product']) || !empty($_GET['lang'])) {
    header('HTTP/1.0 404 Not Found');
    show_no_cache_headers();
    require_once('./error.php');
    exit;
} else {
    show_no_cache_headers();
    header('Location: http://www.mozilla.com/');
    exit;
}
?>
