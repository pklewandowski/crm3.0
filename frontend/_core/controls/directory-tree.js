import ajaxCall from "../ajax";
import Alert from "../alert";

const DirectoryTree = function (treeContainer, id, rootName, options) {
    let _this = this;

    let forbidenDirectoryChars = new RegExp("[!@#$%^&*()+=;,/{}.|:<>?]", "g");

    // this.contentContainer = options.contentContainer ? document.getElementById(options.contentContainer): null;

    this.draggedItem = null;

    this.id = id;
    this.rootDirName = this.id;
    this.rootName = rootName; //rootName.replace(forbidenDirectoryChars, '_');
    this.newFolderName = 'Nowy folder';

    this.tree = $(`#${treeContainer}`); //$("#attachmentDirectoryTree");
    this.treeUrl = '/attachment/api/tree/';
    this.upload_attachment_url = '/attachment/upload/';
    this.attachment_details_url = '/attachment/details/';
    this.move_attachment_url = '/attachment/move/';
    this.remove_attachment_url = '/attachment/remove/';
    this.download_attachment_url = '';
    this.add_directory_url = '/attachment/add-directory/';
    this.delete_directory_url = '/attachment/delete-directory/';
    this.attachment = options.attachment ? options.attachment : null;

    this.onSelect = options ? (options.onSelect ? options.onSelect : null) : null;


    this.setDraggedItem = function (item) {
        this.draggedItem = item;
    };

    this.getNodeById = function (id) {
        return _this.tree.jstree(true).get_node(id)
    };

    this.getSelected = function () {
        return this.tree.jstree("get_node", _this.tree.jstree(true).get_node(_this.tree.jstree(true).get_selected()));
    };

    this.getPath = function (node, noRoot) {

        let path = '';
        if (node) {
            path = _this.tree.jstree(true).get_path(node, '/');
            if (noRoot) {
                if (node.data.type === 'root') {
                    return '';
                }
                path = path.substring(path.indexOf('/') + 1);
            }
        }
        return path;
    };

    this._handleDroppedItem = function (evt) {
        evt.preventDefault();
        evt.target.style.background = "";

        let node = _this.getNodeById($(evt.target).closest('li').prop('id'));

        let filePathItem = _this.draggedItem;
        _this.draggedItem = null;

        if (!filePathItem) {
            return;
        }

        let atmId = $(filePathItem).closest('.thumbnail-image').data('id');
        _this.moveAttachment(atmId, _this.getPath(node, true));
    };

    this.moveAttachment = function (id, path) {

        $.ajax(_this.move_attachment_url, {
            method: 'POST',
            data: {id: id, doc_id: _this.id, path: path},
            success: function (res) {
                _this._update(_this.id, _this.rootName, _this.id)
            },
            error: function (res) {
                let resp = res.responseJSON;
                Alert.error("Błąd!", resp.errmsg);
            }
        });
    };


    this._update = function (id, root_name, callback = null, params = null) {

        return ajaxCall({
                url: _this.treeUrl,
                dataType: 'json',
                method: 'get',
                data: {id: id, root_name: root_name, documentTypeId: _g.document.type.id}
            },
            (res) => {
                _this.tree.jstree(true).settings.core.data = res.tree; //$.parseJSON(res.tree);
                _this.tree.jstree(true).refresh();


                $(".jstree-anchor")
                    .bind("dragenter", function (evt) {
                        evt.target.style.background = "#9fccee";
                    })
                    .bind("dragleave", function (evt) {
                        evt.target.style.background = "";
                    })
                    .bind("dragover", function (evt) {
                        evt.preventDefault();
                    })
                    .bind("drop", function (evt) {
                        console.log(evt);
                        _this._handleDroppedItem(evt);
                    });

                if (typeof callback === 'function') {
                    console.log('_update callback');
                    callback(_this.tree.jstree(true), params);
                }

            },
            (res) => {
                let resp = res.responseJSON;
                Alert.error("Błąd!", resp.errmsg);
                return false;
            }
        );
    };

    this.addDirectory = function (node) {
        return ajaxCall(
            {
                url: _this.treeUrl,
                method: 'post',
                dataType: 'json',
                data: {
                    documentId: _g.document.id,
                    documentTypeId: _g.document.type.id,
                    parentId: node.parent,
                    name: node.text
                }
            },
            (res) => {
                let _node = _this.tree.jstree(true).create_node(
                    _this.tree.jstree(true).get_node(node.parent),
                    {
                        id: res.node.id,
                        text: res.node.name,
                        data: {
                            filename: '',
                            type: 'directory'
                        }
                    }
                );
                _this.tree.jstree(true).edit(_node);

                // _this._update(_this.id, _this.rootName, (tree, id) => {
                //     console.log('_update callback');
                //     tree.edit(tree.get_node(id));
                // }, res.id);
            },
            (res) => {
                // _this.tree.jstree("refresh");
                let resp = res.responseJSON;
                Alert.error("Błąd!", resp.errmsg);
            })
    };

    this.renameDirectory = function (node) {
        ajaxCall(
            {
                url: _this.treeUrl,
                method: 'put',
                dataType: 'json',
                data: {
                    id: node.id,
                    name: node.text,
                    documentTypeId: _g.document.type.id
                }
            },
            (res) => {
                _this._update(_this.id, _this.rootName, _this.id);
            },
            (res) => {
                _this.tree.jstree("refresh");
                let resp = res.responseJSON;
                jsUtils.Alert.error("Błąd!", resp.errmsg);
            })
    };

    this.deleteDirectory = function (node) {
        ajaxCall(
            {
                url: _this.treeUrl,
                dataType: 'json',
                method: 'delete',
                data: {id: node.id, documentTypeId: _g.document.type.id}
            },
            (res) => {
                _this._update(_this.id, _this.rootName, _this.id);
                return true;
            },
            (res) => {
                _this.tree.jstree("refresh");
                let resp = res.responseJSON;

                Alert.error("Błąd!",resp.errmsg);
                return false;
            }
        )
    };

    this.update = function () {
        this._update(this.id, this.rootName, id)
    };

    this.init = function () {

        this.tree.on("loaded.jstree", function (event, data) {
            _this.tree.jstree("open_all");
        });

        this.tree.on("refresh.jstree", function (e, data) {
            _this.tree.jstree("open_all");
            //todo: drut. Root node nie musi mieć id __root__. Zrobć fn do znajdowania roota
            // _this.tree.jstree(true).select_node('__root__');
        });

        this.tree.on('select_node.jstree', function (e, data) {
            let node = data.instance.get_node(data.selected[0]);
            if (typeof _this.onSelect === 'function') {
                _this.onSelect(node);
            }

            this.dispatchEvent(new CustomEvent(
                'directoryTree.selectedNode',
                {
                    bubbles: true,
                    detail: {node: node}
                }
            ));
        });

        this.tree.on('rename_node.jstree', function (e, data) {
            _this.renameDirectory(data.node);
        });

        this._customMenu = function (node) {
            if (node.data.type === 'file') {
                return null;
            }
            let _tree = _this.tree.jstree(true);
            let items = {
                "create": {
                    "separator_before": false,
                    "separator_after": false,
                    "label": "Nowy folder",
                    "action": function (obj) {
                        _this.addDirectory({text: _this.newFolderName, parent: node.id})
                    }
                },
                "rename": {
                    "separator_before": false,
                    "separator_after": false,
                    "label": "Zmień nazwę",
                    "action": function (obj) {
                        _tree.edit(node);
                    }
                },
                "remove": {
                    "separator_before": false,
                    "separator_after": false,
                    "label": "Usuń",
                    "action": function (obj) {
                        if (_this.attachment && _this.attachment.attachments[node.id].length) {  //todo: zmienić, bo już nie ma node jako plików. Sa tylko directory
                            Alert.questionWarning(
                                'Katalog zawiera dane. Czy na pewno usunąć?',
                                'Wszystkie dane (podkatalogi i pliki) zostaną usunięte wraz z katalogiem.',
                                _this.deleteDirectory, node
                            );


                        } else {
                            Alert.question('Czy na pewno usunąć katalog?', '', _this.deleteDirectory, node);
                        }
                    }
                }
            };

            if (node.data.type === 'root') {
                delete items.remove;
                delete items.rename;
            }
            return items;
        };

        _this.tree.jstree({
            'core': {
                'multiple': false,
                "check_callback": true
            },
            plugins: ["contextmenu"],
            "contextmenu": {
                'items': _this._customMenu
            }
        });

        if (this.id && this.rootName) {
            this.update();
        }
    };

    this.init();
};

export default DirectoryTree;