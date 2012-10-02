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
            geoip_country_to_region AS cty
        INNER JOIN
            geoip_ip_to_country AS ip
            ON 
            ip.country_code = cty.country_code AND
            ip_end = ( SELECT MIN(ip_end) FROM geoip_ip_to_country WHERE ip_end >=  INET_ATON('%s') LIMIT 1 ) AND
            ip_start <= INET_ATON('%s')
        ",array($ip, $ip));
    
    if ($region)
        return $region['region_id'];
    else
        return false;
}

/**
 * GeoIP: For a given region id do any throttling for the region
 * @param int $region_id a region id
 * @return boolean should this request come from the clients region? false = yes true = no
 */
function throttleGeoIPRegion($region_id) {
    global $sdo;

    $region_throttle = $sdo->get_one("
        SELECT
            throttle
        FROM
            geoip_regions
        WHERE
            id = %d
        ",array($region_id));
    
    $region_throttle = $region_throttle['throttle'];

    // Don't throttle the user if the throttle is invalid.
    if ( $region_throttle == 100 || $region_throttle > 100 || $region_throttle < 0 ) {
        return false;
    } else {
        /* Ex: Thottle is at 25% GeoIP
          A random number from 1 to 100 will be less than or equal to 25 25% or the time.
          100 will always be greater than or equal to a random number between 1 and 100
          0 will never be greater than or equal to a random number between 1 and 100
        */
        if ( $region_throttle >= mt_rand(1,100) ) {
            return false;
        } else {
            return true;
        }
        
    }

}

function getFallbackRegion($region_id) {
    global $sdo;
    
    $fallback = $sdo->get_one("
        SELECT
            fallback_id
        FROM
            geoip_regions
        WHERE
            id = %d
        ",array($region_id));
        
    if($fallback) {
        return $fallback['fallback_id'];
    } else {
        return false;
    }
}

function getGlobalFallbackProhibited($region_id) {
    global $sdo;
    
    $fallback = $sdo->get_one("
        SELECT
            prevent_global_fallback
        FROM
            geoip_regions
        WHERE
            id = %d
        ",array($region_id));
        
    if($fallback) {
        return $fallback['prevent_global_fallback'];
    } else {
        return false;
    }
}

function setHttpType($ssl_only) {
    if ($ssl_only) {
        $http_type = "https://";
    } else {
        $http_type = "http://";
    }
    return $http_type;
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

    // if we got a language, query for it, otherwise get US English
    if (!empty($_GET['lang']))
        $where_lang = $_GET['lang'];
    else
        $where_lang = 'en-US';

    // Special case for bug 398366
    if ($product_name == 'firefox-latest') {
        $string = file_get_contents(INC . '/product-details/json/firefox_versions.json');
        $firefox_versions = json_decode($string);
        $latest = $firefox_versions->{'LATEST_FIREFOX_VERSION'};

        $redirect_url = WEBPATH . '?product=firefox-' . $latest .
                        '&os=' . $os_name . '&lang=' . $where_lang;
        // if we are just testing, then just print and exit.
        if (!empty($_GET['print'])) {
            show_no_cache_headers();
            print(htmlentities('Location: ' . $redirect_url . '&print=1'));
            exit;
        }

        // otherwise, by default, redirect them and exit
        show_no_cache_headers();
        header('Location: ' . $redirect_url);
        exit;
    }

    require_once(LIB.'/sdo.php');

    $sdo = new SDO();

    // get OS ID
    $os_id = $sdo->name_to_id('mirror_os','id','name',$os_name);

    // get product for this language (if applicable)
    $buf = $sdo->get_one("
        SELECT prod.id, prod.ssl_only FROM mirror_products AS prod
        LEFT JOIN mirror_product_langs AS langs ON (prod.id = langs.product_id)
        WHERE prod.name LIKE '%s'
        AND (langs.language LIKE '%s' OR langs.language IS NULL)",
        array($product_name, $where_lang), MYSQL_ASSOC);
    if (!empty($buf['id'])) {
         $product_id = $buf['id'];
         $ssl_only = $buf['ssl_only'];
    } else {
        $product_id = null;
        $ssl_only = 0;
    }
    // do we have a valid os and product?
    if (!empty($os_id) && !empty($product_id)) {
        $location = $sdo->get_one("
            SELECT
                id,
                path
            FROM
                mirror_locations
            WHERE
                product_id = %d AND 
                os_id = %d", array($product_id, $os_id));

        $client_ip = null;

        // did we get a valid location?
        if (!empty($location)) {
            $mirrors = false;
            if (GEOIP) { 
                // determine the querying user's geographical region
                if (defined('ALLOW_TEST_IP') && ALLOW_TEST_IP && isset($_GET['ip']))
                    $client_ip = $_GET['ip'];
                elseif (!empty($_SERVER['HTTP_X_FORWARDED_FOR'])) {
                    $client_ip = null;
                    $_forward_ips = explode(',', $_SERVER['HTTP_X_FORWARDED_FOR']);

                    if (defined('TRUSTED_PROXIES'))
                        $proxies = explode(' ', TRUSTED_PROXIES);
                    else
                        $proxies = array();

                    while ($_ip = trim(array_pop($_forward_ips))) {
                        if (in_array($_ip, $proxies)) continue;
                        $client_ip = $_ip;
                        break;
                    }
                }

                if (!$client_ip) $client_ip = $_SERVER['REMOTE_ADDR'];
                $client_region = getRegionFromIP($client_ip);
                $fallback_region = getFallbackRegion($client_region);
                $use_this_region = throttleGeoIPRegion($client_region);
                $region_id = false;
                if($use_this_region && $client_region) {
                    $region_id = $client_region;
                } else if (!$use_this_region && $fallback_region) {
                    $region_id = $fallback_region;
                }
                
                if ($region_id) {
                    $http_type = setHttpType($ssl_only);
                    $mirrors = $sdo->get("
                        SELECT
                            mirror_mirrors.id,
                            baseurl,
                            rating
                        FROM 
                            mirror_mirrors
                        JOIN
                            mirror_location_mirror_map ON mirror_mirrors.id = mirror_location_mirror_map.mirror_id
                        LEFT JOIN
                            mirror_lmm_lang_exceptions AS lang_exc ON (mirror_location_mirror_map.id = lang_exc.location_mirror_map_id AND NOT lang_exc.language = '%s')
                        INNER JOIN
                            geoip_mirror_region_map ON (geoip_mirror_region_map.mirror_id = mirror_mirrors.id)
                        WHERE
                            mirror_location_mirror_map.location_id = %d AND
                            geoip_mirror_region_map.region_id = %d AND
                            mirror_mirrors.active='1' AND 
                            mirror_location_mirror_map.active ='1' AND
                            mirror_mirrors.baseurl LIKE '$http_type%%'
                        ORDER BY rating",
                        array($where_lang, $location['id'], $client_region), MYSQL_ASSOC, 'id');
                }
            }
            
            // If we're here we've fallen back to global
            $fallback_global = getGlobalFallbackProhibited($client_region);
            if (empty($mirrors) && !$fallback_global) {
                // either no region chosen or no mirror found in the given region
                $http_type = setHttpType($ssl_only);
                $mirrors = $sdo->get("
                    SELECT
                        mirror_mirrors.id,
                        baseurl,
                        rating
                    FROM 
                        mirror_mirrors,
                        mirror_location_mirror_map
                    LEFT JOIN
                        mirror_lmm_lang_exceptions AS lang_exc ON (mirror_location_mirror_map.id = lang_exc.location_mirror_map_id AND NOT lang_exc.language = '%s')
                    WHERE
                        mirror_mirrors.id = mirror_location_mirror_map.mirror_id AND
                        mirror_location_mirror_map.location_id = %d AND
                        mirror_mirrors.active='1' AND 
                        mirror_location_mirror_map.active ='1' AND
                        mirror_mirrors.baseurl LIKE '$http_type%%'
                    ORDER BY rating",
                    array($where_lang, $location['id']), MYSQL_ASSOC, 'id');
            }

            $mirrors_rand = array();
            $sum = 0;
            foreach ($mirrors as $buf) {
                $mirrors_rand[$buf['id']] = $buf['rating'];
                $sum += $buf['rating'];
            }

            $mirror_rand_id = getRandElement($mirrors_rand, $sum);

            $mirror = $mirrors[$mirror_rand_id];

            // did we get a valid mirror?
            if (!empty($mirror)) {

                // if logging is enabled, insert log
                if (LOGGING) {
                    $sdo->query("UPDATE mirror_mirrors SET count=count+1 WHERE id = %d",array($mirror['id']),false);
                    $sdo->query("UPDATE mirror_products SET count=count+1 WHERE id = %d",array($product_id),false);
                }

                // replace :lang placeholder with requested language
                $target_loc = str_replace(':lang', $where_lang, $location['path']);

                // if we are just testing, then just print and exit.
                if (!empty($_GET['print'])) {
                    show_no_cache_headers();
                    print(htmlentities('Location: '.$mirror['baseurl'].$target_loc));
                    exit;
                }

                // otherwise, by default, redirect them and exit
                show_no_cache_headers();
                header('Location: '.$mirror['baseurl'].$target_loc);
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
