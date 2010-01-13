<?php
/**
 *  Region form.
 *  @package mirror
 *  @subpackage forms
 */
echo '<div>';
form_label('Mirror Name', 'mname','label-small');
form_text('mirror_name', 'mname', '', $posts['mirror_name'], 30, 100);
echo '</div><br />';

echo '<div>';
form_label('Region', 'mregion','label-small');
form_select('region_id','mregion','',mirror_get_regions_select(),$posts['region_id']);
echo ' [<a href="./regions.php">edit regions</a>]';
echo '</div><br />';

echo '<div>';
form_label('Base URL', 'murl','label-small');
form_text('mirror_baseurl', 'murl', '', $posts['mirror_baseurl'], 30, 100);
echo '</div><br />';

echo '<div>';
form_label('Rating', 'mrating','label-small');
form_text('mirror_rating', 'mrating', '', $posts['mirror_rating'], 30, 100);
echo '</div><br />';
?>
