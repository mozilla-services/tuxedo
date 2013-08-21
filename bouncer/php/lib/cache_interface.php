<?php

interface Cache_Interface {
    
    /**
     * Get an item from the cache, if it exists
     * @return mixed item if found, else false
     */
    public function get($key);
    
    /**
     * Store an item in the cache. Replaces an existing item.
     * @return bool success
     */
    public function set($key, $var, $flag = null, $expire);
    
    /**
     * Store an item in the cache. Returns false if the key is
     * already present in the cache.
     * @return bool success
     */
    public function add($key, $var, $flag = null, $expire);

    /**
     * Store an item in the cache. Returns false if the key did
     * NOT exist in the cache before.
     * @return bool success
     */
    public function replace($key, $var, $flag = null, $expire);

    /**
     * Close the connection to _ALL_ cache servers
     * @return bool success
     */
    public function close();

    /**
     * Delete something off the cache
     * @return bool success
     */
    public function delete($key, $timeout = null);

    /**
     * Returns key in the appropriate namespace.
     * @param string $key memcache key 
     * @return string Namespaced key
     */
     public function namespaceKey($key);

    /**
     * Flush the cache
     * @return bool success
     */
    public function flush();
    
}
