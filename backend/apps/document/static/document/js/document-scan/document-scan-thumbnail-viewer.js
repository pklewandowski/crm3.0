import DocumentScanThumbnail from "./document-scan-thumbnail.js"

const DocumentScanThumbnailViewer = function (documentScanThumbnailContainer) {
    this.init = function () {
        "use strict";
        this.container = document.getElementById(documentScanThumbnailContainer);
    };

    this.add = function (url) {
        "use strict";
        let thumbnail = new DocumentScanThumbnail(url);
        this.container.appendChild(thumbnail.get());
        return thumbnail;
    };

    this.setPreviewContainer = function (previewContainer) {
        this.previewContainer = previewContainer;
    };

    this.enumerateItems = function () {
        let cnt = parseInt($("#id_scan-INITIAL_FORMS").val());
        $(`#${documentScanThumbnailContainer}`).find('.document-scan-thumbnail').each(function (i, e) {
            if ($(e).data('status') && $(e).data('status') === "NEW") {

                $(e).find("input").each(function (i1, e1) {
                    $(e1).prop('name', $(e1).prop('name').replace('__prefix__', cnt));
                    if ($(e1).prop('name').indexOf('sq') !== -1) {
                        $(e1).val(cnt);
                    }
                    console.log($(e1).prop('name'));
                });
                cnt++;
            }
        });
        $("#id_scan-TOTAL_FORMS").val(cnt);
    };

    this.init();
};

export default DocumentScanThumbnailViewer