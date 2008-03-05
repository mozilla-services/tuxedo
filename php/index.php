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

/**
 * GeoIP: For a given IP address, get the associated region ID it is in.
 * @param string $ip IP address in dotted quad format
 * @return mixed region ID (int) or false if no region assigned or error
 */
function getRegionFromIP($ip) {
    global $sdo;

    $region = $sdo->get_one("
        SELECT
            cty.region_id
        FROM
            mirror_country_to_region AS cty
        INNER JOIN
            mirror_ip_to_country AS ip
            ON 
            ip.country_code = cty.country_code AND
            ip_end = ( SELECT MIN(ip_end) FROM mirror_ip_to_country WHERE ip_end >=  INET_ATON('%s') LIMIT 1 ) AND
            ip_start <= INET_ATON('%s')
        ",array($ip, $ip));
    
    if ($region)
        return $region['region_id'];
    else
        return false;
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
        // if we got a language, query for it, otherwise get US English
        if (!empty($_GET['lang']))
            $where_lang = $_GET['lang'];
        else
            $where_lang = 'en-US';

        $location = $sdo->get_one("
            SELECT
                location_id,
                location_path
            FROM
                mirror_locations
            LEFT JOIN
                mirror_langs ON (mirror_locations.lang_id = mirror_langs.lang_id)
            WHERE
                product_id = %d AND 
                os_id = %d AND
                mirror_langs.lang = '%s'",array($product_id, $os_id, $where_lang));

        // did we get a valid location?
        if (!empty($location)) {
            
            // determine the querying user's geographical region
            if (defined('ALLOW_TEST_IP') && ALLOW_TEST_IP && isset($_GET['ip']))
                $client_ip = $_GET['ip'];
            elseif (!empty($_SERVER['HTTP_X_FORWARDED_FOR']))
                $client_ip = $_SERVER['HTTP_X_FORWARDED_FOR'];
            else
                $client_ip = $_SERVER['REMOTE_ADDR'];
            $client_region = getRegionFromIP($client_ip);
            
            if ($client_region) {
                $mirrors = $sdo->get("
                    SELECT
                        mirror_mirrors.mirror_id,
                        mirror_baseurl,
                        mirror_rating
                    FROM 
                        mirror_mirrors,
                        mirror_location_mirror_map
                    INNER JOIN
                        mirror_mirror_region_map ON (mirror_mirror_region_map.mirror_id = mirror_mirrors.mirror_id)
                    WHERE
                        mirror_mirrors.mirror_id = mirror_location_mirror_map.mirror_id AND
                        mirror_location_mirror_map.location_id = %d AND
                        mirror_mirror_region_map.region_id = %d AND
                        mirror_active='1' AND 
                        location_active ='1' 
                    ORDER BY mirror_rating",array($location['location_id'], $client_region),MYSQL_ASSOC,'mirror_id');
            } else {
                $mirrors = false;
            }

            if (empty($mirrors)) {
                // either no region chosen or no mirror found in the given region
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
            }

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
                    $sdo->query("UPDATE mirror_mirrors SET mirror_count=mirror_count+1 WHERE mirror_id = %d",array($mirror['mirror_id']),false);
                    $sdo->query("UPDATE mirror_products SET product_count=product_count+1 WHERE product_id = %d",array($product_id),false);
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
