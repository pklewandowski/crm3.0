import {HierarchyUtils} from "./hierarachy-utils";

class HierarchyDrag {
    constructor() {
        this.dragStart = null;
        this.dragEnd = null;
        this.nodeStructure = null;
    }

    _checkDroppableConditions(node, dragged) {
        if (node.type === 'POS') {
            return false;
        }

        if (node.id == dragged.id) {
            return false;
        }
        if (node.id == dragged.parent.id) {
            return false;
        }


        if(HierarchyUtils.findNode(dragged, node.id)) {
            return false;
        }

        if (dragged.type === 'HDQ' && node.type !== 'CMP') {
            return false;
        }

        if (dragged.type === 'POS' && ['CMP', 'HDQ'].includes(node.type)) {
            return false;
        }

        return true;
    }

    getDroppable(nodes, dragged, droppableList) {
        for (let i of nodes) {
            if (this._checkDroppableConditions(i, dragged)) {
                droppableList.push(i.id);
            }
            if (i.children) {
                this.getDroppable(i.children, dragged, droppableList);
            }
        }
    }

    setNodes(nodes) {
        this.nodeStructure = nodes;
    }

    handleDragStart(e) {
        let droppableList = [];
        this.dragStart = e.target.parentElement.dataset['id'];
        let dragged = HierarchyUtils.findNode(this.nodeStructure, this.dragStart);

        this.getDroppable(this.nodeStructure.children, dragged, droppableList);

        // remove node parent from droppable because it's just attached to
        // if (dragged.parent) {
        //     droppableList.splice(droppableList.indexOf(dragged.parent.id), 1);
        // }

        for (let i of droppableList) {
            document.querySelector(`[data-id="${i}"] .node-dropable`).style.display = 'inherit';
        }

        e.dataTransfer.setData("text/html", '<div><<i class="fa-edit"></i>/div>');
        e.effectAllowed = 'move';
    }

    handleDragOver(e) {
        e.preventDefault();
    }

    handleDragEnd(e) {
        let items = document.querySelectorAll('.node-dropable');
        items.forEach(function (item) {
            item.style.display = 'none';
        });
        console.log('dragEnd', e.target.parentElement.dataset['id']);
    }

    handleDrop(e) {
        if (e.target.parentElement.dataset['id'] === this.dragStart) {
            return;
        }

        Alert.questionWarning('Czy na pewno przenieść element?', '', () => {
            ajaxCall({
                    method: 'put',
                    url: _g.hierarchy.urls.moveUrl,
                    data: {
                        nodeId: this.dragStart,
                        nodeTo: e.target.parentElement.dataset['id']
                    }
                },
                () => {
                    document.dispatchEvent(new Event('hierarchy:refresh'));
                },
                (resp) => {
                    Alert.error('Błąd!', resp.responseJSON);
                })
        });
    }

    setDrag() {
        let items = document.querySelectorAll('.node-draggable');
        items.forEach((item) => {
            item.addEventListener('dragstart', (e) => {
                this.handleDragStart(e)
            });
            item.addEventListener('dragend', (e) => {
                this.handleDragEnd(e)
            });
        });

        items = document.querySelectorAll('.node-dropable');
        items.forEach((item) => {
            // item.addEventListener('dragenter', handleDragEnter);
            item.addEventListener('drop', (e) => {
                this.handleDrop(e)
            });
            item.addEventListener('dragover', (e) => {
                this.handleDragOver(e)
            });
        });
    }
}

export {HierarchyDrag};