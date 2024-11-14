import Tabulator from "tabulator-tables";
import {Format} from "../../../../_core/format/format";

class TabulatorTableUtils {
    static headerMenu = function () {
        let menu = [{label: "Widoczność kolumn", menu: []}];
        let columns = this.getColumns();
        let prevParent = null;

        for (let column of columns) {
            if (!column.getParentColumn() || (column.getParentColumn() === prevParent)) {
                continue;
            }

            column = column.getParentColumn();
            prevParent = column;

            //create checkbox element using font awesome icons
            let icon = document.createElement("i");
            icon.classList.add("fas");
            icon.classList.add(column.isVisible() ? "fa-check-square" : "fa-square");

            //build label
            let label = document.createElement("span");
            let title = document.createElement("span");

            title.textContent = " " + column.getDefinition().title;

            label.appendChild(icon);
            label.appendChild(title);

            //create menu item
            menu[0].menu.push({
                label: label,
                action: function (e) {
                    //prevent menu closing
                    e.stopPropagation();

                    //toggle current column visibility
                    column.toggle();

                    //change menu item icon
                    if (column.isVisible()) {
                        icon.classList.remove("fa-square");
                        icon.classList.add("fa-check-square");
                    } else {
                        icon.classList.remove("fa-check-square");
                        icon.classList.add("fa-square");
                    }
                }
            });
        }
        return menu;
    };

    static setFormatters() {
        Tabulator.prototype.extendModule("format", "formatters", {
            moneyCss: function (cell, formatterParams) {
                if (formatterParams.hasOwnProperty("css")) {
                    for (let key in formatterParams.css) {
                        if (formatterParams.css.hasOwnProperty(key)) {
                            cell.getElement().style[key] = formatterParams.css[key];
                        }
                    }
                }

                if (formatterParams.hasOwnProperty("className")) {
                    cell.getElement().classList.add(formatterParams.className);
                }

                return Format.formatNumber(cell.getValue(), formatterParams, true);
            },
            css: function (cell, formatterParams) {
                if (formatterParams.hasOwnProperty("className")) {
                    cell.getElement().classList.add(formatterParams.className);
                    return cell.getValue();
                }
            }
        });
    }

    static setTabulatorTable(id, columns, data = [], rowFormatter) {
        return new Tabulator(id, {
            height: "100%", // set height of table (in CSS or here), this enables the Virtual DOM and improves render speed dramatically (can be any valid css height value)
            data: data, //assign data to table
            columnHeaderVertAlign: "bottom",
            layout: "fitDataStretch",
            movableColumns: true,
            columns: columns,
            tooltipsHeader: true,
            rowFormatter: rowFormatter,
            rowClick: function (e, row) { //trigger an alert message when the row is clicked
                // let data = row.getData(); //get data object for row
                let table = document.createElement('table');
                table.classList.add(...['table', 'table-bordered', 'table-hover', 'table-striped']);
                let tbody = document.createElement('tbody');
                table.appendChild(tbody);

                let data = row.getCells();
                if (data.length) {
                    table.dataset['calc_date'] = data[0].getValue();
                }
                let prevParent = null;
                for (let i in data) {
                    let column = data[i].getColumn();
                    let parent = column.getParentColumn();

                    if (parent && (!prevParent || prevParent !== parent)) {
                        let row = document.createElement('tr');

                        let td = document.createElement('td');
                        td.colSpan = 2;
                        row.appendChild(td);

                        row.classList.add(...['calc-table-modal-group-row']);
                        td.textContent = parent.getDefinition().title;

                        tbody.appendChild(row);
                        prevParent = parent;
                    }

                    let row = document.createElement('tr');
                    tbody.appendChild(row);

                    let label = document.createElement('td');
                    row.appendChild(label);
                    label.textContent = data[i].getColumn().getDefinition().title;
                    label.classList = data[i].getElement().classList;

                    let value = document.createElement('td');
                    row.appendChild(value);
                    if (column.getDefinition().dataType === "currency") {
                        value.textContent = Format.formatNumber(data[i].getValue(), {"decimal": ",", "thousand": " ", "precision": 2});
                    } else {
                        value.textContent = data[i].getValue();
                    }
                    value.classList = data[i].getElement().classList;
                }

                let modal = document.getElementById('calcTableRowDetails');
                let modalBody = modal.querySelector('.modal-body');
                modalBody.innerHTML = null;
                modalBody.appendChild(table);
                $("#calcTableRowDetails").modal();
            },
        });
    }
}

export {TabulatorTableUtils};