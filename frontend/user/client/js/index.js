import {FileUploadControl} from "../../../_core/controls/file-upload-control/js/file-upload-control";

window.onload = () => {
    let fileUpload = new FileUploadControl(
        document.getElementById('csvFileUploadContainer'),
        document.getElementById('csvDataTable'),
        'file',
        '/client/csv/',
        'client',
        ['text/csv', 'application/vnd.ms-excel'],
        4
    );

    $("#csvUploadModal").on('hide.bs.modal, show.bs.modal', () => {
        fileUpload.reset();
    });

    document.getElementById('csvUploadMenuBtn').addEventListener('click', () => {
        $('#csvUploadModal').modal();
    });
    document.getElementById('csvTemplateBtn').addEventListener('click', () => {
        window.location = '/client/api/csv-import-template/';
    });
};
