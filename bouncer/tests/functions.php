<?php
/**
 * To run this test from this directory:
 *  $ php -q functions.php
 *  sdotest
 *  OK
 *  Test cases run: 1/1, Passes: 4, Failures: 0, Exceptions: 0
 */

if (! defined('SIMPLE_TEST')) {
    define('SIMPLE_TEST', 'simpletest/');
}
require_once(SIMPLE_TEST . 'unit_tester.php');
require_once(SIMPLE_TEST . 'reporter.php');
require_once('../php/cfg/config.php');
require_once('../php/lib/memcaching.php');
require_once('../php/lib/sdo.php');
require_once('../php/functions.php');

# Include the mocks
require_once('./mocks/sdo.php');

class FunctionsTest extends UnitTestCase {
    
    
    function testQueryForMirrorsStandalone() {
        $sdo_mock = new SDO_Mock();
        $mirrors = queryForMirrors($sdo_mock, 'http', 1, 1);
        
        
        $this->assertTrue(empty($mirrors), 'Mirrors not empty.');
        $this->assertEqual($sdo_mock->requestCount, 2, 'Incorrect number of requests made to database');
        
        $sdo_mock->resetCount();
        $sdo_mock->returnJunk = true;
        $mirrors = queryForMirrors($sdo_mock, 'http', 1, 1);
        
        $this->assertFalse(empty($mirrors), 'Mirrors are empty');
        $this->assertEqual($sdo_mock->requestCount, 1, 'Incorrect number of requests made to database');
    }
}

$test = new FunctionsTest();
$test->run(new TextReporter());
