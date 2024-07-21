import $ from 'jquery';
import 'jstree';
import 'jstree/dist/themes/default/style.min';

import {SystemException} from "../../exception";

import './scss/hierarchical-checkbox';

const className = 'HierarchicalCheckbox';

class HierarchicalCheckbox {
    constructor(field, hierarchy) {
        this.field = field;
        this.hierarchy = hierarchy;
        this.container = null;
        this.treeContainer = null;
        this.tree = null;

        this.init();
    }

    renderTree() {
        let _this = this;

        this.tree = $(this.treeContainer).jstree({
            'core': {
                data: this.hierarchy
            },
            'checkbox': {
                three_state: false,
                cascade: ''
            },
            'plugins': ["checkbox"]
        }).bind("loaded.jstree", function (event, data) {
            $(this).jstree("open_all");
            _this.initData();
        }).on('changed.jstree', function (e, data) {
            _this.field.value = JSON.stringify(_this.tree.jstree("get_checked", null, true));
        });
    }

    render() {
        this.field.style.display = 'none';
        this.treeContainer = jsUtils.Utils.domElement('div', null, 'hierarchical-checkbox-tree-container');
        this.container.appendChild(this.treeContainer);
        this.renderTree();
    }

    initData() {
        if(this.field.value) {
            this.tree.jstree(true).select_node(JSON.parse(this.field.value));
        }
    }

    init() {
        if (typeof this.field !== 'object') {
            throw new SystemException(`[${className}][init]: Control container has to be valid DOM text input object.`);
        }
        this.container = this.field.parentElement;
        this.render();
    }
}

export default HierarchicalCheckbox;

