/**
 *
 * @param event
 */
window.document.onkeydown = function(event){
    if(! check_shortcut(event)) {
        return;
    }

    let rowCodes = getBigQueryTokens();

    for(let i = 0; i < rowCodes.length; i++) {
        console_log(i + " : " + rowCodes[i]);
    }

    // parse
    let parsedTokens = parse(rowCodes);

    for(let i = 0; i < parsedTokens.length; i++) {
        console.log(i + " : " + parsedTokens[i]);
    }
};

function check_shortcut(event) {
    if (event.ctrlKey && event.shiftKey && event.key == 'F') {
        return true;
    }

    return false;
}
