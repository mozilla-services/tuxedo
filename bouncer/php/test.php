<?php
/**
 *  Memcache server status.
 *  @package mirror
 *  @subpackage admin
 */
require_once('./cfg/init.php');

/* ***** BEGIN LICENSE BLOCK *****
 * Version: MPL 1.1/GPL 2.0/LGPL 2.1
 *
 * The contents of this file are subject to the Mozilla Public License Version
 * 1.1 (the "License"); you may not use this file except in compliance with
 * the License. You may obtain a copy of the License at
 * http://www.mozilla.org/MPL/
 *
 * Software distributed under the License is distributed on an "AS IS" basis,
 * WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
 * for the specific language governing rights and limitations under the
 * License.
 *
 * The Original Code is addons.mozilla.org site.
 *
 * The Initial Developer of the Original Code is
 * The Mozilla Foundation.
 * Portions created by the Initial Developer are Copyright (C) 2006
 * the Initial Developer. All Rights Reserved.
 *
 * Contributor(s):
 *   Wil Clouser <clouserw@mozilla.com>
 *   Mike Morgan <morgamic@mozilla.com>
 *
 * Alternatively, the contents of this file may be used under the terms of
 * either the GNU General Public License Version 2 or later (the "GPL"), or
 * the GNU Lesser General Public License Version 2.1 or later (the "LGPL"),
 * in which case the provisions of the GPL or the LGPL are applicable instead
 * of those above. If you wish to allow use of your version of this file only
 * under the terms of either the GPL or the LGPL, and not to allow others to
 * use your version of this file under the terms of the MPL, indicate your
 * decision by deleting the provisions above and replace them with the notice
 * and other provisions required by the GPL or the LGPL. If you do not delete
 * the provisions above, a recipient may use your version of this file under
 * the terms of any one of the MPL, the GPL or the LGPL.
 *
 * ***** END LICENSE BLOCK ***** */

/**
 * This is a lightweight page designed to be monitored with a program like nagios. I
 * don't want to duplicate the test suite, but I do want something that we can hit
 * pretty often.  If there is a problem, this will throw a 500 error.
 *
 */

// Never cache this page
header('Cache-Control: no-store, no-cache, must-revalidate, post-check=0, pre-check=0, private');
header('Pragma: no-cache');

global $results;

// Check Main Database
    $dbh = @mysql_connect(DBHOST.':'.DBPORT,DBUSER,DBPASS);
    testo('Connect to MAIN database ('.DBHOST.')', is_resource($dbh));
    testo('Select MAIN database ('.DBNAME.')', @mysql_select_db(DBNAME, $dbh));
    unset ($dbh);

// Check Memcache
    testo('Memcache is installed', class_exists('Memcache'));
    testo('Memcache is configured', (is_array($memcache_config) && !empty($memcache_config)));

    if (class_exists('Memcache')) {
        $_memcache = new Memcache();

        $total = 0;
        foreach ($memcache_config as $host=>$options) {
            testo("Memcache server ({$host}) is responding", $_memcache->addServer($host, $options['port'], $options['persistent'], $options['weight'], $options['timeout'], $options['retry_interval']));
            $total++;
        }

        $_memcache->close();

        testo("At least 1 memcache server? ({$total})", ($total>=1));
    }

// Print out all our results
    foreach ($results as $result) {

        if ($result['result'] === 'FAILED') {
            echo "<b style=\"color:red;\">{$result['message']}: {$result['result']}</b><br />\n";
        } else {
            echo "{$result['message']}: {$result['result']}<br />\n";
        }

    }

    echo '<hr />';
    echo '<p>What are we actually testing? <a href="https://svn.mozilla.org/projects/bouncer/1.0/trunk/php/status.php">Check the source</a>';

// Functions
    /**
     * To use as a general message function, pass two strings
     * To use to trigger errors, pass a message and a boolean
     */
    function testo($message, $result) {
        global $results;

        // If they passed in a boolean, we convert it to a string
        if (is_bool($result)) {
            $result = ($result ? 'success' : 'FAILED');
        }

        $results[] = array( 'message' => $message, 'result'  => $result );

        if ($result === 'FAILED') {
            header("HTTP/1.0 500 Internal Server Error");
        }
    }
?>
