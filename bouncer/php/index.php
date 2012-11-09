<?php
/**
 *  Main handler.
 *  @package mirror
 *	@subpackage pub
 */
require_once('./cfg/config.php');  // config file that defines constants
require_once('./functions.php'); // The functions

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
        $fallback_global = FALSE; // False means we WILL fall back.
        
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
                $client_region = getRegionFromIP($sdo, $client_ip);
                $fallback_region = getFallbackRegion($sdo, $client_region);
                $use_this_region = throttleGeoIPRegion($sdo, $client_region);
                $region_id = false;
                if($use_this_region && $client_region) {
                    $region_id = $client_region;
                } else if (!$use_this_region && $fallback_region) {
                    $region_id = $fallback_region;
                }
                
                if ($region_id) {
                    $http_type = setHttpType($ssl_only);
                    $mirrors = queryForMirrors($sdo, $http_type, $where_lang, $location['id'], $client_region);
                }
            }
            
            // If we're here we've fallen back to global
            if (empty($mirrors) && !$fallback_global) {
                if (GEOIP) {
                    $fallback_global = getGlobalFallbackProhibited($sdo, $client_region);
                }
                // either no region chosen or no mirror found in the given region
                $http_type = setHttpType($ssl_only);
                $mirrors = queryForMirrors($sdo, $http_type, $where_lang, $location['id']);
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
