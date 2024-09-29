// check if field label text was truncated
/*
use example
let l = document.getElementById('3310').nextElementSibling // get label of a field
if($(l).is(":truncated")) {console.log('label truncated')}
 */
$.expr[':'].truncated = function (obj) {
    let e = $(obj);
    let c = e.clone().css({display: 'inline', width: 'auto', visibility: 'hidden'}).appendTo('body');
    let c_width = c.width();
    c.remove();

    return (c_width > e.width());
};