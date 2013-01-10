<?php
/**
 * To run this test from this directory:
 *  [morgamic@khan-vm tests]$ php -q sdo.php
 *  sdotest
 *  OK
 *  Test cases run: 1/1, Passes: 29, Failures: 0, Exceptions: 0
 */

if (! defined('SIMPLE_TEST')) {
    define('SIMPLE_TEST', 'simpletest/');
}
require_once(SIMPLE_TEST . 'unit_tester.php');
require_once(SIMPLE_TEST . 'reporter.php');
require_once('../php/cfg/config.php');
require_once('../php/lib/memcaching.php');
require_once('../php/lib/sdo.php');

class SDOTest extends UnitTestCase {

    function setUp() {
        $this->q = "SELECT location_id, location_path FROM mirror_locations WHERE product_id = %d AND os_id = %d";
        $this->args = array(1,2);

        $this->sdo = new SDO();
        $this->assertIsA($this->sdo,'SDO','SDO object is the correct type.');
        $this->assertIsA($this->sdo->mc,'Memcaching','SDO has a Memcaching instance.');
        $this->assertTrue($this->sdo->mc->memcacheConnected,'Memcaching object connected to memcache server.');
    }

    function testNoDatabaseonnection() {
        $q = $this->sdo->flatten_query($this->q,$this->args);
        $this->assertIsA($q,'string','Flattened query is a string.');

        $key = md5($q.MYSQL_BOTH.null);
        $this->assertTrue($this->sdo->mc->flush(),'Existing cache entries flushed.');
        $this->assertTrue($this->sdo->mc->set($key,'foobar'));

        $buf = $this->sdo->get($this->q, $this->args);
        $this->assertEqual($buf,'foobar','Get retrieved from cache only.');
        $this->assertNull($this->sdo->db,'No database connection was made when getting a memcache server hit.');

        $this->sdo->mc->flush();
    }

    function testConnect() {
        $this->assertTrue(is_resource($this->sdo->connect()),'SDO connected to the default database successfully.');
        $this->assertTrue(is_resource($this->sdo->connect('db_write')),'SDO connected to the write database successfully.');
        $this->assertTrue(is_resource($this->sdo->connect('db_read')),'SDO connected to the read-only database successfully.');
    }

    function doGet() {
        $buf = $this->sdo->get($this->q,$this->args);
        $this->assertIsA($buf,'array','Result set is an array.');
        $this->assertTrue(count($buf)>0,'Result contained data.');
    }

    function doGetOne() {
        $buf = $this->sdo->get_one($this->q,$this->args);
        $this->assertIsA($buf,'array','Result set is an array.');
        $this->assertEqual(count($buf),2,'Array contained two items.');
    }

    function doNameToId() {
        $buf = $this->sdo->name_to_id('mirror_os','os_id','os_name','win');
        $this->assertTrue(is_numeric($buf),'Result is an integer.');
    }

    function doUpdateCount() {
        $res = $this->sdo->query('SELECT MIN(mirror_id) FROM mirror_mirrors'); 
        $row = mysql_fetch_row($res);
        $id = $row[0];

        $res = $this->sdo->query('SELECT mirror_count FROM mirror_mirrors WHERE mirror_id = ' . $id); 
        $row = mysql_fetch_row($res);
        $initial_count = $row[0];

        $res = $this->sdo->query('UPDATE mirror_mirrors SET mirror_count=mirror_count+1 WHERE mirror_id = ' . $id,false);

        $res = $this->sdo->query('SELECT mirror_count FROM mirror_mirrors WHERE mirror_id = ' . $id); 
        $row = mysql_fetch_row($res);
        $update_count = $row[0];

        $res = $this->sdo->query('UPDATE mirror_mirrors SET mirror_count=mirror_count-1 WHERE mirror_id = ' . $id,false);

        $this->assertEqual($initial_count + 1,$update_count,'SDO updated a mirror count.');
    }

    function testCacheEntries() {

        $before = $this->sdo->mc->getExtendedStats();

        // First try, hits the db.
        $this->doGet();
        $this->doGetOne();
        $this->doNameToId();

        // Try to update
        $this->doUpdateCount();

        // Second try, hits the cache.
        $this->doGet();
        $this->doGetOne();
        $this->doNameToId();

        $after = $this->sdo->mc->getExtendedStats();

        // Only do it once (assume we only have 1 memcache server).
        // This verifies that we get 3 cache hits for three queries that are
        // done twice.
        foreach ($after as $host=>$stats) {
            $this->assertEqual(intval($before[$host]['cmd_set']),intval($stats['cmd_set'])-3,"Memcache server {$host} received 3 new records.");
            $this->assertEqual(intval($before[$host]['cmd_get']),intval($stats['cmd_get'])-6,"Memcache server {$host} recorded 6 get attempts.");
            $this->assertEqual(intval($before[$host]['get_misses']),intval($stats['get_misses'])-3,"Memcache server {$host} recorded 3 misses.");
            $this->assertEqual(intval($before[$host]['get_hits']),intval($stats['get_hits'])-3,"Memcache server {$host} recorded 3 cache hits.");
            break;
        }

        $this->sdo->mc->flush();
    }
}

$test = new SDOTest();
$test->run(new TextReporter());
?>
