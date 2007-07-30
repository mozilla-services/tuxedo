<?php
/**
 *  Product form.
 *  @package mirror
 *  @subpackage forms
 */
echo '<div>';
form_label('Product Name', 'pname','label-small');
form_text('product_name', 'pname', '', $posts['product_name'], 30, 100);
echo '</div><br />';

echo '<div>';
form_label('Priority', 'pty','label-small');
form_text('product_priority', 'pty', '', $posts['product_priority'], 30, 100);
echo '</div><br />';
?>
