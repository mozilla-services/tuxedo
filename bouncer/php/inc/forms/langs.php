<?php
/**
 *  Language form.
 *  @package mirror
 *  @subpackage forms
 */
echo '<div>';
form_label('Language', 'lang','label-small');
form_text('lang', 'lang', '', $posts['lang'], 20, 6);
echo '</div><br />';

?>
