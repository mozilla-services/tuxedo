<?php
/**
 *  Admin navigation.
 *  @package mirror
 *  @subpackage inc
 */
?>
<div id="side">
<ul id="nav">
<li><a href="<?=WEBPATH?>/admin/logout.php" class="logout" title="Logout to end your session.">&laquo; Logout <?=$_SESSION['user']['username']?></a></li>
<li>
    <a href="<?=WEBPATH?>/admin/" title="Manage current mirrors.">Mirrors</a>
    <ul>
        <li><a href="<?=WEBPATH?>/admin/regions.php" title="A region is an area that has a set of mirrors.">Regions</a></li>
    </ul>
</li>
<li>
    <a href="<?=WEBPATH?>/admin/products.php" title="Products (firefox, thunderbird, etc.)">Products</a>
    <ul>
        <li><a href="<?=WEBPATH?>/admin/locations.php" title="Product file locations based on OS.">File Locations</a></li>
        <li><a href="<?=WEBPATH?>/admin/os.php" title="Operating systems.">Operating Systems</a></li>
        <li><a href="<?=WEBPATH?>/admin/lstats.php" title="View location statuses.">Location Statuses</a></li>
        <li><a href="<?=WEBPATH?>/admin/monitor.php" title="View product uptake.">Product Uptake</a></li>
    </ul>
</li>
<li><a href="<?=WEBPATH?>/admin/users.php" title="Manage administrator accounts.">Users</a></li>
</ul>
</div>
