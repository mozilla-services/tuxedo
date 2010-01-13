<?php
/**
 *  OS form.
 *  @package mirror
 *  @subpackage forms
 */
echo '<div>';
form_label('OS Name', 'oname','label-small');
form_text('os_name', 'oname', '', $posts['os_name'], 30, 100);
echo '</div><br />';

echo '<div>';
form_label('Priority', 'p','label-small');
form_text('os_priority', 'p', '', $posts['os_priority'], 30, 100);
echo '</div><br />';
?>
