<?php

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
function getRegionFromIP($sdo, $ip) {

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
function throttleGeoIPRegion($sdo, $region_id) {
    
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

function getFallbackRegion($sdo, $region_id) {

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

function getGlobalFallbackProhibited($sdo, $region_id) {
    
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

function queryForMirrors($sdo, $http_type, $where_lang, $location_id, $client_region = null, $recurse = false) {
    $arguments = array($where_lang, $location_id);
    
    // If we are using GEOIP, we need to customize the SQL accordingly.
    if($client_region) {
        $cr_sql = ' geoip_mirror_region_map.region_id = %d AND ';
        $arguments[] = $client_region;
    } else {
        $cr_sql = null;
    }
    
    // If we have recursed into this function, we have failed over to unhealthy
    // mirrors.
    if($recurse) {
        $healthy = 0;
    } else {
        $healthy = 1;
    }
    
    $arguments[] = $healthy;

    // Let's fetch the mirrors.
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
            $cr_sql
            mirror_mirrors.active='1' AND 
            mirror_location_mirror_map.active ='1' AND
            mirror_location_mirror_map.healthy = '%d' AND
            mirror_mirrors.baseurl LIKE '$http_type%%'
        ORDER BY rating",
        $arguments, MYSQL_ASSOC, 'id');

    // If we found no mirrors and we are not in the second execution of this
    // function, let's try finding some unhealthy mirrors.
    if(!$mirrors && !$recurse) {
        return queryForMirrors($sdo, $http_type, $where_lang, $location_id, $client_region, true);
    }
    
    return $mirrors;
}