<?php
/**
 *  Functions for netgeo lookups.
 *  @package mirror
 *  @subpackage lib
 */

/**
 *  Calculate the distance between two geo points.
 *  @param int $lat1 latitude of first point
 *  @param int $lon1 longitude of first point
 *  @param int $lat2 latitude of second point
 *  @param int $lon2 longitude of second point
 *  @return int $distance rounded distance in _km_ between these points
 */
function geo_get_distance($lat1,$lon1,$lat2,$lon2)
{
    return null; 
}

/**
 *  Query NetGeo based on API and parse results.
 *  @param string $ip an IP address 
 *  @param string $method lookup method, based on NetGeo API.
 *  @return array|false array containing results or false on failure
 */
function geo_query($ip,$method='getRecord')
{
    $raw = strip_tags(file_get_contents(GEO_URL.'?target='.$ip.'&method='.$method));
    $lines = array_slice(explode("\n",$raw),5);
    array_pop($lines);
    foreach ($lines as $row)
    {
        $buf = preg_split('/:\s*/',$row);
        $data[$buf[0]] = $buf[1];
    }
    return $data;
}

/**
 *  Get longitude and latitude of an IP.
 *  @param string $ip an IP address
 *  @return array|false array containing results or false on failure
 */
function geo_get_coordinates($ip)
{
    return ($data = geo_query($ip,'getLatLong'))?array('lat'=>$data['LAT'],'long'=>$data['LONG']):false;
}

/**
 *  Get complete record based on IP.
 *  @param string $ip an IP address
 *  @return array|false array containing results or false on failure
 */
function geo_get_record($ip)
{
    return ($data = geo_query($ip,'getRecord'))?$data:false;
}

/**
 *  Get country of an IP.
 *  @param string $ip an IP address
 *  @return string|false array containing results or false on failure
 */
function geo_get_country($ip)
{
    return ($data = geo_query($ip,'getCountry'))?$data['COUNTRY']:false;
}
?>
