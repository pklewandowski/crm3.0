$(document).ready(function () {


    let productRetail = new ProductRetail(
        {
            urls: {
                productCategoryTreeUrl: globals.urls.productCategoryTreeUrl,
                addCategoryUrl: globals.urls.addCategoryUrl,
                deleteCategoryUrl: globals.urls.deleteCategoryUrl
            },
            category: {
                change: function (e, data) {
                    $("#id_category").val(data.node.id);
                    $("#id_category_name").val(data.node.text);
                }
            },
            loaded: function (e, data) {
                if (globals.config.mode === 'E') {
                    selectNode($("#id_category").val());
                }
            }
        }
    );

    function selectNode(node) {
        productRetail.selectNode(node);
    }

    productRetail.getCategoryTree();

});