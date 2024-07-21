import FileField from "./document-file-field.js"
// import { fillTemplate, atmTree} from "/static/attachment/js/basic_attachment.js";

$(document).ready(function () {

    let currentFileField = null;

    var cndAtm = new MyDropzone({
        uploadUrl: upload_attachment_url,
        container: '#addFileFieldForm #dropzone_atm',
        previewTemplate: '#attachmentUploadTemplate',
        previewContainer: '#addFileFieldForm #attachmentBeforeUpload tbody',
        dropzoneForm: '#addFileFieldForm',
        documentId: documentId,
        createAttachment: true,

        onSavedFiles: function (i, e, file) {
            currentFileField.handleUploadedFile(e);
        }
    });

    $(".file-upload-field").click(function () {
        //TODO: Po dodaniu załącznika zapisuje się on automatycznie. Jednakże aby był widoczny w rekordzie formsetu, trzeba zapisać cały dokument. Trzeba to tak zmienić, żeby było spójne

        let re = new RegExp('[\\!@#$%^&*()/:?{}+";.,]', 'g'); // TODO: DRUT!!!!!! wziąć docelowo ze zmiennej globalnej niedozwolponych znaków w nazwie katalogu
        let dirName = $(this).closest(".panel").find('.panel-heading').text().replace(re, '_');

        cndAtm.path = `Warunki/${dirName}/`;
        currentFileField = new FileField($(this));

        $("#addFileFieldForm").modal();
    });
});