<?php
/**
 *  Header document.
 *  @package mirror
 *  @subpackage inc
 */
ob_start();
?>
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=ISO-8859-1">
<link rel="home" title="Home" href="http://www.mozilla.org/">
<link rel="stylesheet" type="text/css" href="http://mozilla.org/css/print.css"  media="print">
<link rel="stylesheet" type="text/css" href="http://mozilla.org/css/base/content.css"  media="all">
<link rel="stylesheet" type="text/css" href="http://mozilla.org/css/cavendish/content.css" title="Cavendish" media="screen">
<link rel="stylesheet" type="text/css" href="http://mozilla.org/css/base/template.css"  media="screen">
<link rel="stylesheet" type="text/css" href="http://mozilla.org/css/cavendish/template.css" title="Cavendish" media="screen">
<link rel="stylesheet" type="text/css" href="<?=WEBPATH?>/css/screen.css" media="screen">
<link rel="icon" href="http://mozilla.org/images/mozilla-16.png" type="image/png">
<title><?=$title?></title>
<meta name="robots" content="all">
<meta name="keywords" content="web browser mozilla firefox firebird camino thunderbird bugzilla user agent web links cool sites">
<meta name="author" content="Tristan Nitot http://standblog.com/, design by Dave Shea http://www.mezzoblue.com/">
<?=(!empty($extra_headers))?$extra_headers:null?>
</head>
<body id="www-mozilla-org" class="secondLevel"<?=(!empty($body_tags))?' '.$body_tags.' ':null;?>>
<div id="container">
<p class="skipLink"><a href="#mBody" accesskey="2">Skip to main content</a></p>
<div id="header">
<h1><a href="/" title="Return to home page" accesskey="1">Mozilla</a></h1>
<ul>
<li id="menu_aboutus"><a href="http://mozilla.org/about/" title="Getting the most out of your online experience">About</a></li>
<li id="menu_developers"><a href="http://mozilla.org/developer/" title="Using Mozilla's products for your own applications">Developers</a></li>
<li id="menu_store"><a href="http://www.mozillastore.com/?r=mozorg1" title="Shop for Mozilla products on CD and other merchandise">Store</a></li>
<li id="menu_support"><a href="http://mozilla.org/support/" title="Installation, trouble-shooting, and the knowledge base">Support</a></li>
<li id="menu_products"><a href="http://mozilla.org/products/" title="All software Mozilla currently offers">Products</a></li>
</ul>
<form id="search" method="get" action="http://www.google.com/custom" title="Mozilla.org Search">
<div>
<label for="q" title="Search mozilla.org">search mozilla:</label>
<input type="hidden" name="cof" value="LW:174;LH:60;L:http://www.mozilla.org/images/mlogosm.gif;GIMP:#cc0000;T:black;ALC:#0000ff;GFNT:grey;LC:#990000;BGC:white;AH:center;VLC:purple;GL:0;GALT:#666633;AWFID:9262c37cefe23a86;">
<input type="hidden" name="domains" value="mozilla.org">
<input type="hidden" name="sitesearch" value="mozilla.org">
<input type="text" id="q" name="q" accesskey="s" size="30">
<input type="submit" id="submit" value="Go">
</div>
</form>
</div>
<hr class="hide">
<div id="mBody">
<?php
if (!empty($nav)) {
    require_once($nav);
    echo '<hr class="hide">';
    echo '<div id="mainContent">';
}
?>
