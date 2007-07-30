<?php
/**
 *  Footer document.
 *  @package mirror
 *  @subpackage inc
 */
?>
<hr class="hide">
</div>
<?php
if (!empty($nav)) {
    echo '</div>';
}
?>
<div id="footer">
<ul>
<li><a href="http://mozilla.org/sitemap.html">Site Map</a></li>
<li><a href="http://mozilla.org/contact/">Contact Us</a></li>
<li><a href="http://mozilla.org/foundation/donate.html">Donate</a></li>
</ul>
<p class="copyright">Copyright &copy; 1998-<?php echo date('Y'); ?> The Mozilla Organization</p>
</div>
</div>
</body>
</html>
<?php
ob_end_flush();
?>
