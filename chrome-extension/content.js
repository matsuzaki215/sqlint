/**
 *
 * @param event
 */
window.document.onkeydown = function(event){
    if (event.key !== 'Enter')
        return;

    let rowCodes = getBigQueryTokens();

    for(let i = 0; i < rowCodes.length; i++) {
        console.log(i + " : " + rowCodes[i]);
    }

    // parse
    let parsedTokens = parse(rowCodes);

    for(let i = 0; i < parsedTokens.length; i++) {
        console.log(i + " : " + parsedTokens[i]);
    }
};
