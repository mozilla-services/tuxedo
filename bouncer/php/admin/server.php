<?php
/**
 *  Memcache server status.
 *  @package mirror
 *  @subpackage admin
 */
$protect=1;  // protect this page
require_once('../cfg/init.php');
require_once('../lib/memcaching.php');

$memcache = new Memcaching();

if (!empty($_POST['flush'])) {
    $memcache->flush();
    header('Location: ./server.php');
    exit;
}

$title = 'Memcache Server Status';
$nav = INC.'/admin_nav.php';
require_once(HEADER);
echo '<h2>Memcache Server Status</h2>';

$data['memcache'] = $memcache->getExtendedStats();

if (defined('CACHE') && CACHE) {
    foreach ($data['memcache'] as $server=>$stats) {
        echo '<div class="corner-box">';
        echo "<h3>{$server}</h3>";    
        if (!empty($stats) && is_array($stats)) {
            echo '<ul>';
            echo '<li>Gets: '.$stats['get_hits'].'</li>';
            echo '<li>Misses: '.$stats['get_misses'].'</li>';
            echo '<li>Total Gets: '.($stats['get_hits']+$stats['get_misses']).'</li>';
            echo '<li>Hit %: '.$stats['get_hits']*100/($stats['get_hits']+$stats['get_misses']).'</li>';
            echo '<li>Quota %: '.$stats['bytes']*100/$stats['limit_maxbytes'].'</li>';
            echo '</ul>';
            echo '<ul>';
            foreach ($stats as $key=>$val) {
                echo "<li>{$key}: {$val}</li>";
            }
            echo '</ul>';
        } else {
            echo "<ul><li>Failed to connect to {$server}</li></ul>";
        }
        echo '</div>';
    }
} else {
    echo '<p>Memcache is not enabled (CACHE is false).</p>';
}

?>
<h3>Memcache Flush</h3>
<form method="post" action="./server.php">
<div>
<p>You can use this to expire all existing records.  Use it smartly.</p>
<input type="submit" name="flush" value="Flush Cache">
</div>
</form>
<?php
require_once(FOOTER);
?>
