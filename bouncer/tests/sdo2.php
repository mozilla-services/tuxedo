<?php
/**
 * To run this test from this directory:
 *  [morgamic@khan-vm tests]$ php -q sdo2.php
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
require_once('./mocks/memcaching.php');
require_once('../php/lib/sdo2.php');

class SDOTest extends UnitTestCase {

    function setUp() {
        $this->q = "SELECT `id`, `path` FROM mirror_locations WHERE product_id = ? AND os_id = ?";
        $this->args = array(1,2);

        $mc = new Memcaching_Mock();
        $this->mc = $mc;
        
        $dbwrite = array(
            'host' => DBHOST,
            'name' => DBNAME,
            'user' => DBUSER,
            'pass' => DBPASS,
        );
        $this->sdo = new SDO2($mc, $dbwrite);
        $this->assertIsA($this->sdo,'SDO2','SDO object is the correct type.');
    }

    function testNoDatabaseonnection() {
        $this->assertIsA($this->q,'string','Flattened query is a string.');
    }

    function testConnect() {
        $this->assertTrue(($this->sdo->connect() instanceof PDO),'SDO connected to the default database successfully.');
        $this->assertTrue(($this->sdo->connect('db_write') instanceof PDO),'SDO connected to the write database successfully.');
        $this->assertTrue(($this->sdo->connect('db_read') instanceof PDO),'SDO connected to the read-only database successfully.');
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

    function doUpdateCount() {
        $res = $this->sdo->query('SELECT MIN(id) FROM mirror_mirrors'); 
        $row = $res->fetch();
        $id = $row[0];

        $res = $this->sdo->query('SELECT count FROM mirror_mirrors WHERE id = ' . $id); 
        $row = $res->fetch();
        $initial_count = $row[0];

        $res = $this->sdo->query('UPDATE mirror_mirrors SET count=count+1 WHERE id = ' . $id);

        $res = $this->sdo->query('SELECT count FROM mirror_mirrors WHERE id = ' . $id); 
        $row = $res->fetch();
        $update_count = $row[0];

        $res = $this->sdo->query('UPDATE mirror_mirrors SET count=count-1 WHERE id = ' . $id);

        $this->assertEqual($initial_count + 1,$update_count,'SDO updated a mirror count.');
    }

    function testCacheEntries() {
        print "FIXME testCacheEntries() disabled, needs test DB\n";
        /*
        // First try, hits the db.
        $this->doGet();
        $this->doGetOne();

        // Try to update
        $this->doUpdateCount();

        // Second try, hits the cache.
        $this->doGet();
        $this->doGetOne();
        */
    }
}

$test = new SDOTest();
$test->run(new TextReporter());
?>
