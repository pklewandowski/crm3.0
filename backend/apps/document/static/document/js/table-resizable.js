// //var tables = document.getElementsByClassName('flexiCol');
// var tables = document.getElementsByTagName('table');
// for (var i = 0; i < tables.length; i++) {
//     resizableGrid(tables[i]);
// }

function resizableGrid(table) {
    var row = table.getElementsByTagName('tr')[0],
        cols = row ? row.children : undefined;
    if (!cols) return;

    // trzeba zaremować, bo inaczej zasłania bootstrapowe dropdown
    // table.style.overflow = 'hidden';

    var tableHeight = table.offsetHeight;

    for (var i = 0; i < cols.length; i++) {
        var div = createDiv(tableHeight);
        cols[i].appendChild(div);
        cols[i].style.position = 'relative';
        setListeners(div);
    }

    function setListeners(div) {
        var pageX, curCol, nxtCol, curColWidth, nxtColWidth;

        div.addEventListener('mousedown', function (e) {
            curCol = e.target.parentElement;
            nxtCol = curCol.nextElementSibling;
            pageX = e.pageX;

            var padding = paddingDiff(curCol);

            curColWidth = curCol.offsetWidth - padding;
            if (nxtCol)
                nxtColWidth = nxtCol.offsetWidth - padding;
        });

        // div.addEventListener('mouseover', function (e) {
        //     e.target.style.borderRight = '2px solid #0000ff';
        // });
        //
        // div.addEventListener('mouseout', function (e) {
        //     e.target.style.borderRight = '';
        // });

        document.addEventListener('mousemove', function (e) {
            if (curCol) {
                var diffX = e.pageX - pageX;

                if (nxtCol)
                    nxtCol.style.width = (nxtColWidth - (diffX)) + 'px';

                curCol.style.width = (curColWidth + diffX) + 'px';
            }
        });

        document.addEventListener('mouseup', function (e) {
            curCol = undefined;
            nxtCol = undefined;
            pageX = undefined;
            nxtColWidth = undefined;
            curColWidth = undefined
        });
    }

    function createDiv(height) {
        var div = document.createElement('div');
        div.style.top = 0;
        div.style.right = 0;
        div.style.width = '8px';
        div.style.position = 'absolute';
        div.style.cursor = 'col-resize';
        div.style.userSelect = 'none';
        div.style.height = '100%'; //height + 'px';
        div.className = 'columnSelector';
        return div;
    }

    function paddingDiff(col) {

        if (getStyleVal(col, 'box-sizing') == 'border-box') {
            return 0;
        }

        var padLeft = getStyleVal(col, 'padding-left');
        var padRight = getStyleVal(col, 'padding-right');
        return (parseInt(padLeft) + parseInt(padRight));

    }

    function getStyleVal(elm, css) {
        return (window.getComputedStyle(elm, null).getPropertyValue(css))
    }
}




/*


$(function () {
            var startX,
                startWidth,
                $handle,
                $table,
                pressed = false;

            $(document)
                .on({
                    mousemove: function (event) {
                        if (pressed) {
                            $handle.width(startWidth + (event.pageX - startX));
                        }
                    },
                    mouseup: function () {
                        if (pressed) {
                            $table.removeClass("resizing");
                            pressed = false;
                        }
                    }
                })
                .on("mousedown", ".table-resizable th", function (event) {
                    $handle = $(this);
                    pressed = true;
                    startX = event.pageX;
                    startWidth = $handle.width();

                    $table = $handle.closest(".table-resizable").addClass("resizing");
                })
                .on("dblclick", ".table-resizable thead", function () {
                    // Reset column sizes on double click
                    $(this)
                        .find("th[style]")
                        .css("width", "");
                });
        });
* */