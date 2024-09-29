import {SystemException} from "../exception";
import "./scss/toolbar-utils.scss";

const TOOLBAR_BTN = {sm: 'toolbar-sm-btn'};
const className = 'ToolbarUtils';

class ToolbarUtils {

    static toolbarBtn(classList = null, icon = null, size = null, callback = null, inline = false) {
        let btn = document.createElement('div');
        btn.classList.add(inline ? 'toolbar-btn-inline' : 'toolbar-btn');

        if (classList) {
            if (typeof classList !== 'object') {
                throw SystemException(`[${className}][_toolbarBtn]: classList parameter must be an array`);
            }
            btn.classList.add(...classList);
        }

        if (icon) {
            let btnIcon = document.createElement('i');
            for (let i of icon.split(' ')) {
                btnIcon.classList.add(i);
            }
            btn.appendChild(btnIcon);
        }
        if (size) {
            btn.classList.add(size);
        }
        return btn;
    }


    static handleBtn(size = null, inline = false) {
        let btn = ToolbarUtils.toolbarBtn(['toolbar-handle-btn'], 'fa fa-arrows', size, null, inline);
        btn.tabIndex = 0;
        return btn;
    }

    static addBtn(size = null, inline = false) {
        return ToolbarUtils.toolbarBtn(['toolbar-add-btn'], 'fa fa-plus-circle', size, null, inline);
    }

    static editBtn(size = null, inline = false) {
        return ToolbarUtils.toolbarBtn(['toolbar-edit-btn'], 'fas fa-pen', size, null, inline);
    }

    static saveBtn(size = null, inline = false) {
        return ToolbarUtils.toolbarBtn(['toolbar-save-btn'], 'fas fa-save', size, null, inline);
    }

    static deleteBtn(size = null, inline = false) {
        return ToolbarUtils.toolbarBtn(inline ? ['toolbar-delete-btn-inline'] : ['toolbar-delete-btn'], 'fa fa-times', size, null, inline);
    }

    static deleteXBtn(size = null, inline = false) {
        return ToolbarUtils.toolbarBtn(['toolbar-delete-btn'], 'fa fa-times', size, null, inline);
    }

    static closeBtn(size = null, inline = false) {
        return ToolbarUtils.toolbarBtn(['toolbar-close-btn'], 'fa fa-times', size, null, inline);
    }

    static undoBtn(size = null, inline = false) {
        return ToolbarUtils.toolbarBtn(['toolbar-undo-btn'], 'fa fa-undo', size, null, inline);
    }

    static redoBtn(size = null, inline = false) {
        return ToolbarUtils.toolbarBtn(['toolbar-redo-btn'], 'fa fa-redo', size, null, inline);
    }

    static container() {
        let c = jsUtils.Utils.domElement('div', null, ['toolbar-container']);
        return c;
    }
}

export {ToolbarUtils, TOOLBAR_BTN};