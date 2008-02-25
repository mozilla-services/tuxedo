<?php
/**
 *  File location form.
 *  @package mirror
 *  @subpackage forms
 */
echo '<div>';
form_label('Product', 'product','label-small');
form_select('product_id','product','',mirror_get_products_select(),$posts['product_id']);
echo ' [<a href="./products.php">edit products</a>]';
echo '</div><br />';

echo '<div>';
form_label('OS', 'os','label-small');
form_select('os_id','os','',mirror_get_oss_select(),$posts['os_id']);
echo ' [<a href="./os.php">edit operating systems</a>]';
echo '</div><br />';

echo '<div>';
form_label('File Location', 'floc','label-small');
form_text('location_path', 'floc', '', $posts['location_path'], 30, 255);
echo '</div><br />';
?>
