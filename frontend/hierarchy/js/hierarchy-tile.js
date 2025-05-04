class HierarchyTile {
    static _isDraggable(node) {
        if (node.type !== 'CMP') {
            return `<div class="node-draggable" draggable="true"><i class="fas fa-arrows-alt"></i></div>`;
        } else return '';
    };

    static _isEditableAsRoot(node) {
        if (node.type !== 'POS') {
            return `<div data-id="${node.id}" class="node-editable-as-root" draggable="true"><i class="fas fa-edit"></i></div>`;
        } else return '';
    }

    static _addHierarchyBtn(node) {
        if (node.type === 'CMP' || node.type === 'HDQ' || node.type === 'DEP') {
            return `<a data-id="${node.id}" class="add-hierarchy"><i class="fa fa-plus"></i></a>`;
        } else return '';
    };

    static _editHierarchyBtn(node) {
        return `<a data-id="${node.id}" data-type="${node.type}" data-parent="${node.parent.id}" data-name="${node.name}"
                   data-description="${node.description}" class="edit-hierarchy"><i class="fas fa-pencil-alt"></i></a>`;
    };

    static _deleteHierarchyBtn(node) {
        return `<a data-id="${node.id}" class="delete-hierarchy"><i class="fa fa-times"></i></a>`;
    };

    static _userHierarchyBtn(node) {
        if (node.type === 'POS') {
            return `<a data-id="${node.id}" class="user-hierarchy"><i class="fa fa-user"></i></a>`;
        } else return '';
    };


    static rootInnerHTML(node) {
        return `<div class="node-inner-content node-root"><p class="node-name">${node.name}</p>
            <a data-id="${node.id}" class="add-hierarchy btn btn-default btn-sm" >
            <i class="fa fa-plus" style="pointer-events: none;"></i></a>
            </div>`;
    };

    static nodeInnerHTML(node) {
        return `<div data-id="${node.id}" data-type="${node.type}" class="node-inner-content node-descendant">
         ${HierarchyTile._isDraggable(node)}
         ${HierarchyTile._isEditableAsRoot(node)}
        <div class="node-dropable"><i class="fas fa-shopping-basket"></i></div>
        
        <p style="margin-bottom:0" class="node-name">${node.name}</p>
        <p style="font-size:11px">&nbsp;${node.description ? node.description : ''}</p>
        <div class="hierarchy-action-buttons">
            <div style="float: left">
                ${HierarchyTile._userHierarchyBtn(node)}
                ${HierarchyTile._addHierarchyBtn(node)}
                ${HierarchyTile._editHierarchyBtn(node)}
                ${HierarchyTile._deleteHierarchyBtn(node)}
            </div>
        </div>
    </div>`;
    };
}

export {HierarchyTile};