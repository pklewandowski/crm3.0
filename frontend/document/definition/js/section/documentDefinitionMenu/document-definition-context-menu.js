import Sortable from "sortablejs";

class DocumentDefinitionContextMenu {

    constructor(menuSelector) {

        this.menuSelector = menuSelector;
        this.menuDialog = ``;

    }

    addField() {
        //todo: Only for tests. Finally render field from standarized DocumentFieldRenderer class
        let formGroup = document.createElement('div');
        formGroup.classList.add('form-group');
        let field = document.createElement('input');
        field.classList.add(...['form-control', 'input-md']);
        formGroup.appendChild(field);
        return formGroup;
    }

    addColumnContainer(id) {
        console.log(id);
        let columnContainer = document.createElement('div');
        columnContainer.classList.add(...['column-container', 'col-lg-12']);
        columnContainer.setAttribute('tabindex', '0');

        //todo: move to separate file to reuse in document-definition and this file
        new Sortable(columnContainer, {
            handle: '.handle-icon', // handle's class
            group: 'column-container',
            ghostClass: 'sortable-label-swap',
            animation: 150,
            onStart: evt => {
            },
            onEnd: evt => {
                var itemEl = evt.item;  // dragged HTMLElement
                console.log(evt.item,
                    evt.to,    // target list
                    evt.from,  // previous list
                    // evt.oldIndex,  // element's old index within old parent
                    evt.newIndex,  // element's new index within new parent
                    //evt.oldDraggableIndex, // element's old index within old parent, only counting draggable elements
                    // evt.newDraggableIndex, // element's new index within new parent, only counting draggable elements
                    // evt.clone, // the clone element
                    //evt.pullMode
                );  // when item is in another sortable: `"clone"` if cloning, `true` if moving
            }
        });

        return columnContainer;
    }

    show(e) {
        let _this = this;
        console.log(e.target);
        let menu = $(_this.menuSelector)
            .data("invokedOn", e.target)
            .show()
            .css({
                position: "absolute",
                left: _this.getMenuPosition(e.clientX, 'width', 'scrollLeft'),
                top: _this.getMenuPosition(e.clientY, 'height', 'scrollTop')
            })
            .off('click')
            .on('click', 'a', function (e) {
                menu.hide();

                let invokedOn = menu.data("invokedOn");
                let selectedMenu = $(e.target);

                if (invokedOn.classList.contains('column-container')) {
                    menu.data('invokedOn').appendChild(_this.addField());

                } else if (invokedOn.classList.contains('subsection-container')) {
                    menu.data('invokedOn').appendChild(_this.addColumnContainer(invokedOn.id));
                }

                // _this.menuSelected.call(this, $invokedOn, $selectedMenu);
            });
    }

    getMenuPosition(mouse, direction, scrollDir) {
        let win = $(window)[direction](),
            scroll = $(window)[scrollDir](),
            menu = $(this.menuSelector)[direction](),
            position = mouse + scroll;

        // opening menu would pass the side of the page
        if (mouse + menu > win && menu < mouse)
            position -= menu;

        return position;
    }
}

export default DocumentDefinitionContextMenu;