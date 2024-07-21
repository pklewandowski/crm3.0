const AttachmentDirectoryTree = function (treeContainer, id, rootName, options) {
    let _this = this;

    let forbidenDirectoryChars = new RegExp("[!@#$%^&*()+=;,/{}.|:<>?]", "g");

    this.draggedItem = null;

    this.id = id;
    this.rootDirName = this.id;
    this.rootName = rootName.replace(forbidenDirectoryChars, '_');

    this.tree = $(`#${treeContainer}`); //$("#attachmentDirectoryTree");
    this.treeUrl = '/attachment/get-tree/';
    this.upload_attachment_url = '/attachment/upload/';
    this.attachment_details_url = '/attachment/details/';
    this.move_attachment_url = '/attachment/move/';
    this.remove_attachment_url = '/attachment/remove/';
    this.download_attachment_url = '';
    this.add_directory_url = '/attachment/add-directory/';
    this.delete_directory_url = '/attachment/delete-directory/';

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

        console.log(_this.getPath(node, true));

        let filePathItem = _this.draggedItem;
        _this.draggedItem = null;

        if (!filePathItem) {
            return;
        }

        let atmId = $(filePathItem).closest('.thumbnail-image').data('id');
        _this.moveAttachment(atmId, _this.getPath(node, true));
    };

    this.moveAttachment = function (id, path) {

        $.ajax(this.move_attachment_url, {
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


    this._update = function (id, root_name, root_dir_name) {

        $.ajax(this.treeUrl, {
            dataType: 'json',
            method: 'POST',
            data: {'id': id, 'csrfmiddlewaretoken': window.csrf_token, 'root_name': root_name, 'root_dir_name': root_dir_name},
            success: function (res) {
                _this.tree.jstree(true).settings.core.data = $.parseJSON(res.tree);
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
            },
            error: function (res) {
                let resp = res.responseJSON;
                Alert.error("Błąd!",resp.errmsg);
                return false;
            }
        });
    };

    this.addDirectory = function (node) {
        let dir = {
            path: (_this.getPath(node, true)),
            root_dir_name: _this.rootDirName,
            original_name: node.original.text
        };
        $.ajax(this.add_directory_url, {
            dataType: 'json',
            method: 'POST',
            data: {
                'directory': dir,
                'csrfmiddlewaretoken': window.csrf_token
            },
            success: function (res) {
                _this._update(_this.id, _this.rootName, _this.id);
                // swal('Katalog został dodany!', '', 'success');
                return true;
            },
            error: function (res) {
                _this.tree.jstree("refresh");
                let resp = res.responseJSON;
                Alert.error("Błąd!",resp.errmsg);
                return false;
            }
        });
    };

    this.deleteDirectory = function (node) {
        let dir = {
            path: (_this.getPath(node, true)),
            root_dir_name: _this.rootDirName,
        };
        $.ajax(this.delete_directory_url, {
            dataType: 'json',
            method: 'POST',
            data: {'directory': dir, 'csrfmiddlewaretoken': window.csrf_token},
            success: function (res) {
                _this._update(_this.id, _this.rootName, _this.id);
                return true;
            },
            error: function (res) {
                _this.tree.jstree("refresh");
                let resp = res.responseJSON;
                Alert.error("Błąd!",resp.errmsg);
                return false;
            }
        });
    };

    this.update = function () {
        this._update(this.id, this.rootName, id)
    };

    this.init = function () {

        this.tree.on("loaded.jstree", function (event, data) {
            _this.tree.jstree("open_all");
        });

        this.tree.on("refresh.jstree", function (e, data) {
            $(this).jstree("open_all");
        });

        this.tree.on('select_node.jstree', function (e, data) {
            let node = data.instance.get_node(data.selected[0]);
            if (typeof _this.onSelect === 'function') {
                _this.onSelect(node);
            }
        });

        this.tree.on('rename_node.jstree', function (e, data) {
            console.log(data.node);
            _this.addDirectory(data.node);
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
                        console.log(_tree);
                        let _node = _tree.create_node(node,
                            {
                                text: 'Nowy folder',
                                data: {
                                    filename: '',
                                    type: 'directory'
                                }
                            });
                        _tree.edit(_node);
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
                        // _this.tree.trigger('productRetail.event.category.delete', [node]);
                        if (node.children.length) {
                            Alert.error("Błąd!", "Folder nie może być usunięty, bo nie jest pusty!");
                            return false;
                        }
                        _tree.delete_node(node);
                        _this.deleteDirectory(node)
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
            this.update()
        }
    };

    this.init();
};

export default AttachmentDirectoryTree;