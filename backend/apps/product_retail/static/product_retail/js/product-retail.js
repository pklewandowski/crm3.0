function ProductRetail(options) {
    let _this = this;

    if (!options) {
        options = {category: {}}
    }

    if (!options.urls) {
        throw 'No urls defined'
    }

    this.userPermissions = null;

    this.urls = options.urls;

    if (!this.urls.productCategoryTreeUrl) {
        throw 'productCategoryTreeUrl not defined';
    }

    // if (!this.urls.productsForCategoryUrl) {
    //     throw 'productsForCategoryUrl not defined';
    // }


    this.defaults = {
        productListRowTemplate: '<tr data-id="__ID_PRODUCT__">' +
        '<td class="product-name">__PRODUCT_NAME__</td>' +
        '<td class="unit-price">__UNIT_PRICE__</td>' +
        '<td>' +
        '<div class="btn-group">' +
        '<button class="btn btn-default btn-sm add-product-to-list-btn">' +
        '<i class="fa fa-plus"></i>' +
        '</button>' +
        '</div>' +
        '</td></td>' +
        '</tr>',
        categoryTreeContainer: $('#productCategoryTree'),
        productListContainer: $('#productList').find('table tbody'),
        category: {
            addCategoryBtn: $("#id_add_category_btn"),
            addCategoryNameContainer: $("#id_add_category_name"),
            change: function () {

            },

            rename: function () {

            },
            delete: function (node) {
                if (!_this.urls.deleteCategoryUrl) {
                    throw 'Brak zdefioniowanego Url dla usunięcia kategorii';
                }

                let children = _this.categoryTreeContainer.jstree().get_node(node).children;
                if (children.length) {
                    return swal('Kategoria posiada podkategorie!', '', 'error');
                }

                swal({
                    title: 'Jesteś pewien?',
                    type: 'warning',
                    showCancelButton: true,
                    confirmButtonText: "Tak, usuń!",
                    cancelButtonText: "Nie",
                    closeOnConfirm: false,
                }, function () {

                    $.ajax({
                        url: _this.urls.deleteCategoryUrl,
                        method: 'post',
                        data: {
                            id: node.id
                        },
                        success: function (resp) {
                            _this.categoryTreeContainer.jstree(true).delete_node(node);
                            swal('Kategoria została usunięta', '', 'info');
                        },
                        error: function (resp, errmsg) {
                            let res = resp.responseJSON;
                            if (resp.statusText === 'abort') {
                                return;
                            }
                            return swal('Błąd', res.errmsg, 'error');
                        }
                    });
                });
            }
        },

        page: {
            currentPageContainer: $("#id_filter-form-page"),
            searchContainer:
                $("#id_filter-form-search"),
            sortFieldContainer:
                $("#id_filter-form-p3_sort_field"),
            sortDirContainer:
                $("#id_filter-form-p3_sort_dir"),
        },
    };

    this.selectedNode = null;
    this.categoryTreeContainer = options.categoryTreeContainer ? options.categoryTreeContainer : this.defaults.categoryTreeContainer;
    this.productListContainer = options.productListContainer ? options.productListContainer : this.defaults.productListContainer;
    this.productListRowTemplate = options.productListRowTemplate ? options.productListRowTemplate.html() : this.defaults.productListRowTemplate;
    this.addCategoryBtn = options.addCategoryBtn ? options.addCategoryBtn : this.defaults.addCategoryBtn;
    this.category = {};
    if (options.category) {
        this.category.addCategoryNameContainer = options.category.addCategoryNameContainer ? options.category.addCategoryNameContainer : this.defaults.category.addCategoryNameContainer;
        this.category.addCategoryBtn = options.category.addCategoryBtn ? options.category.addCategoryBtn : this.defaults.category.addCategoryBtn;
    }
    else {
        this.category.addCategoryNameContainer = this.defaults.category.addCategoryNameContainer;
        this.category.addCategoryBtn = this.defaults.category.addCategoryBtn;
    }

    if (options.filterForm) {
        let f = options.filterForm;
        this.currentPageContainer = $(f.currentPageContainer);
        this.searchContainer = $(f.searchContainer);
        this.sortFieldContainer = $(f.sortFieldContainer);
        this.sortDirContainer = $(f.sortDirContainer);
    }
    else {
        this.currentPageContainer = this.defaults.page.currentPageContainer;
        this.searchContainer = this.defaults.page.searchContainer;
        this.sortFieldContainer = this.defaults.page.sortFieldContainer;
        this.sortDirContainer = this.defaults.page.sortDirContainer;
    }

    this.fillProductList = function (e, data) {
        _this.productListContainer.html(null);
        _this.getProductsForCategory(data.selected[0]);
    }

    this.getCategoryTree = function () {
        if (this.ajxGetCategoryTree) {
            this.ajxGetCategoryTree.abort();
        }
        this.ajxGetCategoryTree = $.ajax({
            url: _this.urls.productCategoryTreeUrl,
            method: 'post',
            success: function (res) {
                // let res = $.parseJSON(resp);
                let tree = _this.categoryTreeContainer;
                tree.jstree(
                    {
                        core: {
                            data: res.data,
                            multiple: false,
                            check_callback: true,
                        },
                        plugins: ["contextmenu"],
                        "contextmenu": {
                            "items": function (node) {
                                let tree = _this.categoryTreeContainer.jstree(true);
                                return {
                                    // "Create": {
                                    //     "separator_before": false,
                                    //     "separator_after": false,
                                    //     "label": "Utwórz",
                                    //     "action": function (obj) {
                                    //         node = tree.create_node(node);
                                    //         this.edit(node);
                                    //     }
                                    // },
                                    // "Rename": {
                                    //     "separator_before": false,
                                    //     "separator_after": false,
                                    //     "label": "Zmień nazwę",
                                    //     "action": function (obj) {
                                    //         tree.edit(node);
                                    //     }
                                    // },
                                    "Remove": {
                                        "separator_before": false,
                                        "separator_after": false,
                                        "label": "Usuń",
                                        "action": function (obj) {
                                            _this.categoryTreeContainer.trigger('productRetail.event.category.delete', [node]);
                                            // _this.deleteNode(node);
                                        }
                                    }
                                };
                            }
                        }
                    })
                    .bind("loaded.jstree", function (e, data) {
                        if(options.loaded && typeof options.loaded === 'function') {
                            options.loaded(e, data);
                        }
                        // _this.categoryTreeContainer.jstree("select_node", '2', true);
                    });
                return tree;
            },
            error: function (resp) {
                swal('Błąd', resp.errmsg, 'error');
            }
        });
    };

    this.categoryTreeContainer.on('changed.jstree', function (e, data) {
        _this.selectedNode = data.node;
        if (_this.urls.productsForCategoryUrl) {
            _this.fillProductList(e, data)
        }
        if (options.category) {
            if (typeof options.category.change === 'function') {
                options.category.change(e, data)
            }
        }
    });

    this.categoryTreeContainer.on('productRetail.event.category.delete', function (e, node) {
        _this.defaults.category.delete(node);
    });

    this._fillProductList = function (el, data) {
        let tmpl = this.productListRowTemplate;
        let html = '';
        $.each(data, function (i, e) {
            let _e = e.fields;
            html += tmpl
                .replace(/__ID_PRODUCT__/g, e.pk)
                .replace(/__PRODUCT_NAME__/g, _e.name)
                .replace(/__UNIT_PRICE__/g, _e.unit_price)
                .replace(/__CATEGORY__/g, _e.unit_price)
        });
        _this.productListContainer.html(html)
    };

    this.getProductsForCategory = function () {

        if (!_this.urls.productsForCategoryUrl) {
            return;
        }

        let selectedNode = _this.categoryTreeContainer.jstree('get_selected')[0];
        if (!selectedNode) {
            return;
        }

        if (this.ajxGetProducstForCategory) {
            this.ajxGetProducstForCategory.abort();
        }
        this.ajxGetProducstForCategory = $.ajax({
            url: _this.urls.productsForCategoryUrl,
            method: 'post',
            data: {
                id: selectedNode,
                search: _this.searchContainer ? _this.searchContainer.val() : '',
                page: _this.currentPageContainer ? _this.currentPageContainer.val() : 1,
                sort_dir: _this.sortDirContainer ? _this.sortDirContainer.val() : '',
                sort_field: _this.sortFieldContainer ? _this.sortFieldContainer.val() : ''
            },
            success: function (resp) {
                let res = $.parseJSON(resp);
                _this._fillProductList(_this.productListContainer, $.parseJSON(res.page.data))
            },
            error: function (resp, errmsg) {
                if (resp.statusText === 'abort') {
                    return;
                }
                return swal('Błąd', errmsg, 'error');
            }
        });
    };

    this.addCategory = function () {
        if (!this.urls.addCategoryUrl) {
            throw 'addCategoryUrl not defined';
        }
        let selectedNode = this.categoryTreeContainer.jstree('get_selected')[0];
        if (!selectedNode) {
            swal('Proszę zaznaczyć kategorię nadrzędną', '', 'warning');
            return;
        }
        if (!this.category.addCategoryNameContainer.val()) {
            swal('Proszę wprowadzić nazwę katregorii', '', 'warning');
            return;
        }
        $.ajax({
            url: _this.urls.addCategoryUrl,
            method: 'post',
            data: {
                parentId: selectedNode,
                name: _this.category.addCategoryNameContainer.val()
            },
            success: function (res) {
                _this.category.addCategoryNameContainer.val(null);

                let position = 'last';
                let parentId = _this.categoryTreeContainer.jstree('get_selected')[0];
                let newNode = {
                    text: res.name,
                    id: res.id,
                    state: {
                        opened: true,
                        selected: false
                    }
                };

                _this.categoryTreeContainer.jstree().create_node(
                    parentId,
                    newNode,
                    position,
                    function () {
                    }
                );

                _this.categoryTreeContainer.jstree().select_node(res.id);
                swal('Pomyślnie dodano kategorię', '', 'info');
            },
            error: function (resp) {
                let res = resp.responseJSON;
                return swal('Błąd', res.errmsg, 'error');
            }
        });
    };

    this.selectNode = function (node, triggerChangeEvent) {
        this.categoryTreeContainer.jstree().deselect_all(true);
        this.categoryTreeContainer.jstree().select_node(node);
        if (triggerChangeEvent) {
            this.categoryTreeContainer.trigger('changed.jstree')
        }
    };

    this.findProduct = function () {
    };

    this.addProductToSelection = function () {
    };
    this.getUserPermissions = function () {
        this.userPermissions = null;
    };

    this.init = function () {
        this.category.addCategoryBtn.click(function () {
            _this.addCategory();
        });
        this.getUserPermissions();
    };
    this.init();
}

