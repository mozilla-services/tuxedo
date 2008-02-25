<?php
/**
 *  User form.
 *  @package mirror
 *  @subpackage forms
 */
echo '<div>';
form_label('Username', 'uname','label-small');
form_text('username', 'uname', '', $posts['username'], 30, 100);
echo '</div><br />';

echo '<div>';
form_label('Password', 'password','label-small');
form_password('password', 'password', '', 30, 100);
echo '</div><br />';

echo '<div>';
form_label('Re-enter Password', 'rpassword','label-small');
form_password('rpassword', 'rpassword', '', 30, 100);
echo '</div><br />';

echo '<div>';
form_label('First Name', 'fname','label-small');
form_text('user_firstname', 'fname', '', $posts['user_firstname'], 30, 100);
echo '</div><br />';

echo '<div>';
form_label('Last Name', 'lname','label-small');
form_text('user_lastname', 'lname', '', $posts['user_lastname'], 30, 100);
echo '</div><br />';

echo '<div>';
form_label('Email', 'email','label-small');
form_text('user_email', 'email', '', $posts['user_email'], 30, 100);
echo '</div><br />';

?>
