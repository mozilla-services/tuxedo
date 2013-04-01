<?php
/**
 *  Scalable Data Object 2
 *  
 *  Replacement to use modern OO standards for PHP 5.x.
 *
 *  @package mirror
 *  @subpackage lib
 */

require_once(LIB . '/memcaching.php');

class SDO2 {
    
    // We should abstract PDO away from the functions in our app that use this class.
    // So we redefine the constants as a passthrough to PDO.
    const FETCH_ASSOC = PDO::FETCH_ASSOC;
    const FETCH_BOTH = PDO::FETCH_BOTH;
    const FETCH_NAMED = PDO::FETCH_NAMED;
    const FETCH_NUM = PDO::FETCH_NUM;
    
    /**
     * Database resource.
     */
    protected $db;

    /**
     * Memcache object.
     * Requires use of Memcaching object. 
     */
    protected $mc;
    
    protected $db_write;
    protected $db_read;
    protected $db_details;

    public function __construct(Cache_Interface $mc, array $dbwrite = array(), array $dbread = array()) {
        $this->mc = $mc;
        if(empty($dbwrite) && empty($dbread)) {
            throw new Exception('No credentials supplied for database connection');
        }
        
        if(empty($dbwrite)) {
            throw new Exception('Write database credentials are required');
        }
        
        $this->db_details = array (
                                'db_write' => array ( 
                                    'host' => $dbwrite['host'],
                                    'name' => $dbwrite['name'],
                                    'user' => $dbwrite['user'],
                                    'pass' => $dbwrite['pass'],
                                ),
                                'db_read'  => array (
                                    'host' => isset($dbread['host']) ? $dbread['host'] : $dbwrite['host'],
                                    'name' => isset($dbread['name']) ? $dbread['name'] : $dbwrite['name'],
                                    'user' => isset($dbread['user']) ? $dbread['user'] : $dbwrite['user'],
                                    'pass' => isset($dbread['pass']) ? $dbread['pass'] : $dbwrite['pass'],
                                ),
                            );
    }

    /**
     *  Connect to a MySQL database server.
     *  @param string $dbtype db selector (db_write,db_read)
     *  @return resource|boolean
     */
    public function connect($dbtype='db_write')
    {
        if(isset($this->$dbtype) && $this->$dbtype instanceof PDO) {
            return $this->$dbtype;
        }

        $details = $this->db_details[$dbtype];
        $dsn = 'mysql:host=' . $details['host'] . ';dbname=' . $details['name'];

        try {
            $this->$dbtype = new PDO($dsn, $details['user'], $details['pass'], array(PDO::ATTR_PERSISTENT => true));
            $this->$dbtype->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
        
            return $this->$dbtype;
        } catch (Exception $e) {
            /**
             * If we can't connect at all then we have to show a fallback page w/
             * the correct error code.
             */
            error_log($e->getMessage());
            header('HTTP/1.0 500 Internal Server Error');
            require_once(FILEPATH.'/gonefishing.php');
            exit;
        }
    }

    /**
     *  Execute a MySQL query.
     *  @param string $q MySQL query
     *  @param array $args arguments
     *  @param boolean $readonly query from read only database?
     */
    public function query($q, array $args=array(), $readonly=true)
    {        
        $stmt = $this->build_query($q, $readonly);
        $stmt->execute($args);
        return $stmt;
    }

    /**
     *  Fetch a row as an array from a mysql result.
     *  @param string $result
     *  @return array
     */
    public function fetch_array(PDOStatement $result, $type = self::FETCH_BOTH)
    {
        return $result->fetchAll($type);
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
    public function get($query,$args, $type = self::FETCH_NAMED, $col_id = null)
    {

        // trim our query
        $query = trim($query);

        // set cachekey
        $cachekey = md5($this->flatten_query($query, $args).$type.$col_id);

        // only return cached results if we have a valid cache object and the
        // current query is a select query 
        if ($this->mc && 0 === strpos(strtolower($query), 'select')) {
            if ($list = $this->mc->get($cachekey)) {
                return $list;
            }
        }
        
        $res = $this->query($query, $args);
        
        $list = array();
        
        
        if( $res instanceof PDOStatement &&
            !is_null($col_id) &&
            $type == self::FETCH_NAMED &&
            $res->rowCount() > 0
          ) {
        
            $rows = $this->fetch_array($res, $type);
            
            foreach($rows as $row) {
                $list[$row[$col_id]] = $row;
            }
            
            return $list;
        }
        
        $list = $this->fetch_array($res, $type);

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
    public function get_one($query, $args, $type = self::FETCH_ASSOC) {
        $buf = $this->query($query.' LIMIT 1',$args);
        return $buf->fetch($type);
    }

    /**
     * Parse pre-query and add passed args.
     * @param string $base base query with ? marking variables
     * @param array $args array containing args for substitution
     */
    public function build_query($base, $readonly) {
        if($readonly) {
            $dbh = $this->connect('db_read');
        } else {
            $dbh = $this->connect();
        }
        
        return $dbh->prepare($base);
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