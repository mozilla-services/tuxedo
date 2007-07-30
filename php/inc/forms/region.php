<?php
/**
 *  Region form.
 *  @package mirror
 *  @subpackage forms
 */
echo '<div>';
form_label('Region Name', 'rname','label-small');
form_text('region_name', 'rname', '', $posts['region_name'], 30, 100);
echo '</div><br />';

echo '<div>';
form_label('Priority', 'rp','label-small');
form_text('region_priority', 'rp', '', $posts['region_priority'], 30, 100);
echo '</div><br />';
?>
