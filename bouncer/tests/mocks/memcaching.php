<?php

require LIB . '/memcaching.php';

/**
 * This model is an interface to Memcache.
 * It's called Memcaching to not interfere with the actual Memcache class.
 */
class Memcaching_Mock implements Cache_Interface {

    function get($key) {
        return false;
    }

    /**
     * Store an item in the cache. Replaces an existing item.
     * @return bool success
     */
    function set($key, $var, $flag = null, $expire = CACHE_EXPIRE) {
        return true;
    }
    
    /**
     * Store an item in the cache. Returns false if the key is
     * already present in the cache.
     * @return bool success
     */
    function add($key, $var, $flag = null, $expire = CACHE_EXPIRE) {
        return true;
    }

    /**
     * Store an item in the cache. Returns false if the key did
     * NOT exist in the cache before.
     * @return bool success
     */
    function replace($key, $var, $flag = null, $expire = CACHE_EXPIRE) {
        return true;
    }

    /**
     * Close the connection to _ALL_ cache servers
     * @return bool success
     */
    function close() {
        return true;
    }

    /**
     * Delete something off the cache
     * @return bool success
     */
    function delete($key, $timeout = null) {
        return true;
    }

    /**
     * Returns key in the appropriate namespace.
     * @param string $key memcache key 
     * @return string Namespaced key
     */
     function namespaceKey($key) {
        $this->namespace = 'ns';
        return $this->namespace . $key;
     }

    /**
     * Flush the cache
     * @return bool success
     */
    function flush() {
        return true;
    }

    /**
     * Get server statistics.
     * return array
     */
    function getExtendedStats() {
        return array();
    }
}
?>
