

import "treantjs/Treant";
import "treantjs/Treant.css";
import "../scss/styles.scss";

import {HierarchyDrag} from "./hierarchy-drag";
import {HierarchyForm} from "./hierarchy-form";
import {HierarchyTile} from "./hierarchy-tile";
import {HierarchyUtils} from "./hierarachy-utils";

class Hierarchy {
    constructor(container, formDialogId, rootNodeId = null) {
        this.containerSelector = `#${container}`;
        this.container = jsUtils.Utils.setContainer(container);
        this.rootNodeId = rootNodeId;
        this.form = new HierarchyForm(formDialogId);

        this.tree = null;
        this.blockDiagramConfig = {
            chart: {
                container: this.containerSelector,
                connectors: {
                    type: 'step'
                },
                node: {
                    HTMLclass: 'nodeExample1'
                },
            },
            nodeStructure: {}
        };

        this.hierarchyDrag = new HierarchyDrag(this.blockDiagramConfig.nodeStructure);
    }

    prepareNodes() {
        function _prepareNodes(nodes, parent) {
            if (nodes.length) {
                for (let node of nodes) {
                    node.parent = parent;
                    node.innerHTML = HierarchyTile.nodeInnerHTML(node);
                    node.connectors = {
                        style: {
                            "stroke": "#a8a8a8",
                            "stroke-width": 2,
                        }
                    };
                    _prepareNodes(node.children, node);
                }
            }
        }

        if (!this.blockDiagramConfig.nodeStructure) {
            return null;
        }

        this.blockDiagramConfig.nodeStructure.innerHTML = HierarchyTile.rootInnerHTML(this.blockDiagramConfig.nodeStructure);
        this.blockDiagramConfig.nodeStructure.connectors = {
            style: {
                "stroke": "#a8a8a8",
                "stroke-width": 2,
            }
        };

        _prepareNodes(this.blockDiagramConfig.nodeStructure.children, this.blockDiagramConfig.nodeStructure);
    }

    _addHierarchy(nodeId) {
        this.form.show(null, HierarchyUtils.findNode(this.blockDiagramConfig.nodeStructure, nodeId));
    }

    _editHierarchy(nodeId) {
        this.form.show(nodeId);
    }

    _deleteHierarchy(nodeId) {
        Alert.questionWarning(
            'Czy na pewno usunąć strukturę - operacja jest nieodwracalna?',
            'Usunięcie spowoduje odłączenie wszystich przypisanych pracowników',
            () => {
                ajaxCall({
                        method: 'delete',
                        url: _g.hierarchy.urls.apiUrl,
                        data: {id: nodeId}
                    },
                    () => {
                        this.render();
                    },
                    (resp) => {
                        jsUtils.LogUtils.log(resp.responseJSON);
                    }
                )
            }
        )
    }

    _setActions() {
        this.container.addEventListener('click', (e) => {
            console.log('target', e.target);
            let el = e.target;
            let id = parseInt(el.dataset['id']);
            if (el.classList.contains('add-hierarchy')) {
                this._addHierarchy(id);
            }
            if (el.classList.contains('edit-hierarchy')) {
                this._editHierarchy(id);
            }

            if (el.classList.contains('delete-hierarchy')) {
                this._deleteHierarchy(id);
            }

            if (el.classList.contains('node-editable-as-root')) {
                this.rootNodeId = id;
                this.render()
            }
        });

        this.hierarchyDrag.setDrag();
        document.addEventListener('hierarchy:refresh', () => {
            this.render();
        });

        this.form.submitButton.addEventListener('click', () => {
            Alert.questionWarning('Czy na pewno zapisać zmiany?', '', () => {
                this.add();
            });
        })
    }

    _getNodes() {
        return new Promise((resolve, reject) => {
            ajaxCall({
                    method: 'get',
                    url: _g.hierarchy.urls.apiUrl,
                    data: {rootNodeId: this.rootNodeId}
                },
                (nodes) => {
                    this.blockDiagramConfig.nodeStructure = nodes;
                    resolve(nodes);
                },
                (resp) => {
                    jsUtils.LogUtils.log(resp.responseJSON);
                }
            );
        });
    }

    buildTree() {
        if (this.tree) {
            this.tree.destroy();
        }
        this.tree = new Treant(this.blockDiagramConfig);
    }

    render(nodes = null) {
        let _this = this;
        function _render() {
            _this.prepareNodes();
            _this.hierarchyDrag.setNodes(_this.blockDiagramConfig.nodeStructure);
            _this.buildTree();
            _this._setActions();
        }

        if (nodes) {
            this.blockDiagramConfig.nodeStructure = nodes;
            _render();
        } else {
            this._getNodes().then(() => {
                _render();
            });
        }
    };

    add() {
        let hierarchy = this.form.getFormData();

        ajaxCall({
                method: hierarchy?.id ? 'put' : 'post',
                url: _g.hierarchy.urls.apiUrl,
                data: {form: JSON.stringify(hierarchy)}
            },
            () => {
                this.form.hide();
                this.render();
            }
        )
    }

    update(hierarchy) {

    }

    delete(id) {

    }
}

export {Hierarchy};