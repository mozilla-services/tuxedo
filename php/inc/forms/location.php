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
echo '<br/><span class="form-indent">Use '
    .'<span class="jslink" onClick="insertAtCursor(\'floc\',\'%LANG%\');"><code>%LANG%</code></span>'
    .' as a place holder for the language code.</span>';
echo '</div><br />';

$all_langs = mirror_get_langs_select();
echo '<div>';
form_label('Languages', 'languagelist','label-small');
echo '<div class="form-indent">';
foreach ($all_langs as $lid => $lname) {
    form_checkbox('langs[]', "lang{$lid}", '', $lid, (!empty($posts['langs']) && in_array($lid,$posts['langs'])?'1':'0'));
    form_label($lname, "lang{$lid}");
    echo '<br/>';
}
echo 'Select: ';
echo '<span class="jslink" onClick="selectAll(\'langs[]\');">all</span> | ';
echo '<span class="jslink" onClick="selectNone(\'langs[]\');">none</span> | ';
echo '<span class="jslink" onClick="selectInvert(\'langs[]\');">invert</span>';
echo '</div>';
echo '</div><br />';
?>
