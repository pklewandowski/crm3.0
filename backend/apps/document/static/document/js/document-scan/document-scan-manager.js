import DocumentScanViewer from "./document-scan-viewer.js"
import DocumentScanThumbnailViewer from "./document-scan-thumbnail-viewer.js"

var docScan = new DocumentScanViewer("documentScanContainer");
var docThumbViewer = new DocumentScanThumbnailViewer("documentScanThumbnailContainer");

$(document).ready(function () {

    // docScan.loadImage('/media/document/scan/fk.jpg');

    let scanDropzone = new MyDropzone({
        uploadUrl: upload_scan_url,
        container: '#addScanForm #dropzone_atm',
        previewTemplate: '#attachmentUploadTemplate',
        previewContainer: '#addScanForm #attachmentBeforeUpload tbody',
        dropzoneForm: '#addScanForm',

        onSavedFiles: function (i, e, file) {
            docThumbViewer.add('/media/' + e.file_path + e.file_name);
        }
    });

    $("#add_scan_btn").click(function () {
        $("#addScanForm").modal();
    });

    $(document).on("click", ".document-scan-thumbnail", function () {
        docScan.loadImage($(this).find('img').prop('src'));
    });

    $(document).on('submit', function (e) {
        // e.preventDefault();
        docThumbViewer.enumerateItems();
    });
});
