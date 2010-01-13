/* Bouncer js */

/**
 * select all checkboxes in an array
 * @param string name (e.g. "langs[]")
 * @param int select (1) or unselect (0) all
 * @return bool success
 */
function selectAll(name, all_on) {
    var boxes = document.getElementsByName(name);
    if (!boxes) return false;
    if (arguments.length < 2) all_on = 1;

    for (var i = 0; i < boxes.length; i++) {
        boxes[i].checked = all_on;
    }
    return true;
}

/**
 * unselect all checkboxes in an array
 * @param string name (e.g. "langs[]")
 */
function selectNone(name) {
    return selectAll(name, 0);
}

/**
 * invert the selection of a group of checkboxes
 * @param string name of checkbox array
 * @return bool success
 */
function selectInvert(name) {
    var boxes = document.getElementsByName(name);
    if (!boxes) return false;

    for (var i = 0; i < boxes.length; i++) {
        boxes[i].checked = (!boxes[i].checked);
    }
    return true;
}

/**
 * count how many checkboxes of an array are checked
 * @param string name of checkbox array
 * @return number of checked boxes, or false if failed
 */
function countCheckboxes(name) {
    var boxes = document.getElementsByName(name);
    if (!boxes) return false;

    var counter = 0;
    for (var i = 0; i < boxes.length; i++) {
        if (boxes[i].checked) counter++;
    }
    return counter;
}

/**
 * Replace selection in a text field or similar
 * @param id of textbox
 * @param replacement/insert text
 * @return bool success
 */
function insertAtCursor(textboxID, replacement) {
    var textbox = document.getElementById(textboxID);
    if (!textbox) return false;
    
    if (textbox.selectionStart || textbox.selectionStart == '0') {
        var startPos = textbox.selectionStart;
        var endPos = textbox.selectionEnd;
        textbox.value = textbox.value.substring(0, startPos)
            + replacement
            + textbox.value.substring(endPos, textbox.value.length);
    } else {
        textbox.value += replacement;
    }
    return true;
}
