<?php
/**
 *  Scalable Data Object
 *  
 *  Schoolhouse paste holding together a simple set of db wrappers and the memcache API.
 *  NOTE: For PHP4 OO but should work in PHP5.  Just test it first.  Seriously.
 *
 *  @package mirror
 *  @subpackage lib
 */
require_once(LIB.'/memcaching.php');
class SDO {

    /**
     * Database resource.
     */
    var $db;

    /**
     * Memcache object.
     * Requires use of Memcaching object. 
     */
    var $mc;

    function SDO() {
        $this->db_write = null;
        $this->db_read = null;
        $this->mc = new Memcaching();
        $this->db_details = array (
                                'db_write' => array ( 
                                    'host' => DBHOST,
                                    'name' => DBNAME,
                                    'user' => DBUSER,
                                    'pass' => DBPASS,
                                ),
                                'db_read'  => array (
                                    'host' => defined('SHADOWDBHOST') ? SHADOWDBHOST : DBHOST,
                                    'name' => defined('SHADOWDBNAME') ? SHADOWDBNAME : DBNAME,
                                    'user' => defined('SHADOWDBUSER') ? SHADOWDBUSER : DBUSER,
                                    'pass' => defined('SHADOWDBPASS') ? SHADOWDBPASS : DBPASS,
                                ),
                            );
    }

    /**
     *  Connect to a MySQL database server.
     *  @param string $dbtype db selector (db_write,db_read)
     *  @return resource|boolean
     */
    function connect($dbtype='db_write')
    {
        if (is_resource($this->$dbtype) && @mysql_db_name($this->$dbtype)) {
            return $this->$dbtype;
        }

        $details = $this->db_details[$dbtype];

        $db = @mysql_connect($details['host'],$details['user'],$details['pass']);
        if (is_resource($db) && !@mysql_db_name($db)) { 
            @mysql_select_db($details['name'],$db);
            $this->$dbtype = $db;
            return $this->$dbtype;
        }

        /**
         * If we can't connect at all then we have to show a fallback page w/
         * the correct error code.
         */
        header('HTTP/1.0 500 Internal Server Error');
        require_once(FILEPATH.'/gonefishing.php');
        exit;
    }

    /**
     *  Execute a MySQL query.
     *  @param string $q MySQL query
     *  @param array $args arguments
     *  @param boolean $readonly query from read only database?
     */
    function query($q,$args=null,$readonly=true)
    {
        $dbh = $readonly ? $this->connect('db_read') : $this->connect('db_write');
        return @mysql_query($this->build_query($q,$args),$dbh);
    }

    /**
     *  Fetch a row as an array from a mysql result.
     *  @param string $result
     *  @return array
     */
    function fetch_array($result=null,$type=MYSQL_BOTH)
    {
        return @mysql_fetch_array($result,$type);
    }

    /**
     *  Fetch an array based on a query. 
     *  @param string $query database query
     *  @param array $args query arguments
     *  @param int $type result type
     *  @param string $col_id if passed it, the values of this column in the result set will be used as the array keys in the returned array
     *  @return array $list array of database rows
     *
     *  Example of returned array:
     *  <code>
     *  $this->get("SELECT * FROM table WHERE foo=?",array('bar'),MYSQL_ASSOC);
     *  returns...
     *  Array
     *  (
     *      [0] => Array
     *          (
     *              [id] => 1
     *              [field1] => data1 
     *              [field2] => data2
     *          )
     *
     *  )
     *  </code>
     */
    function get($query,$args,$type=MYSQL_BOTH,$col_id=null)
    {

        // trim our query
        $query = trim($query);

        // set cachekey
        $cachekey = md5($this->flatten_query($query,$args).$type.$col_id);

        // only return cached results if we have a valid cache object and the
        // current query is a select query 
        if ($this->mc && 0 === strpos(strtolower($query), 'select')) {
            if ($list = $this->mc->get($cachekey)) {
                return $list;
            }
        }

        $res = $this->query($query,$args);
        $list = array();
        if (is_resource($res) && !is_null($col_id) && ($type == MYSQL_BOTH || $type == MYSQL_ASSOC) && @mysql_num_rows($res) !== 0) {
            $col_test = $this->fetch_array($res,$type);
            @mysql_data_seek($res, 0);
            if (array_key_exists($col_id,$col_test)) {
                while ( $buf = $this->fetch_array($res,$type) ) {
                    $list[$buf[$col_id]] = $buf;
                }

                if ($this->mc && 0 === strpos(strtolower($query), 'select')) {
                    $this->mc->set($cachekey, $list);
                }

                return $list;
            }
        }

        while ( $buf = $this->fetch_array($res,$type) ) {
            $list[] = $buf;
        }

        if ($this->mc && 0 === strpos(strtolower($query), 'select')) {
            $this->mc->set($cachekey, $list);
        }

        return $list;
    }

    /**
     *  Get one record.
     *  @param string $query query
     *  @param int $type result type
     */
    function get_one($query,$args,$type=MYSQL_ASSOC) {
        $buf = $this->get($query.' LIMIT 1',$args,$type,null);
        return !empty($buf[0]) ? $buf[0] : null;
    }

    /**
     *  Get an ID based on name.
     *  @param string $table
     *  @param string $id_col
     *  @param string $name_col
     *  @param string $name
     */
    function name_to_id($table,$id_col,$name_col,$name)
    {
        $buf = $this->get_one("SELECT {$id_col} FROM {$table} WHERE {$name_col} = '%s'", array($name), MYSQL_NUM);
        return $buf[0];
    }

    /**
     * Parse pre-query and add passed args.
     * @param string $base base query with ? marking variables
     * @param array $args array containing args for substitution
     */
    function build_query($base, $args=array()) {
        if ( empty($args) ) {
            return $base;
        }

        array_walk($args, array($this, 'escape_string'));
        // array_merge now requires a type-cast to handle strings (changed in PHP5)
        return call_user_func_array('sprintf', array_merge((array)$base, $args));
    }

    /**
     * Escapes query strings.
     */
    function escape_string(&$s) {
        $s = @mysql_real_escape_string($s);
    }

    /**
     * Generate a flat string for a cache id.
     * @param string $base base query
     * @param array $args array containing args
     * @return string
     */
    function flatten_query($base, $args) {
        return $base.serialize($args);
    }

}
?>
