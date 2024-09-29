const FileField = function (element) {
    let containerClassname = 'file-upload-field-container';
    "use strict";
    this.field = null;
    this.init = function (e) {
        this.field = this.getField(e);
        this.fileList = this.field.closest(`.${containerClassname}`).find(".file-upload-field-list")

    };

    this.getField = function (e) {
        return e.closest(`.${containerClassname}`).find(".file-upload-field");
    };

    this._serializeFileList = function () {
        let t = [];
        this.fileList.find('li').each(function (i, e) {
            let _e = $(e);
            t.push(
                {
                    file_name: _e.data('file_name'),
                    file_original_name: _e.data('file_original_name'),
                    file_mime_type: _e.data('file_mime_type'),
                    file_path: _e.data('file_path').replace(/\\/g, '/')
                })
        });
        this.field.val(JSON.stringify(t));
        console.log(this.field);
    };

    this.handleUploadedFile = function (file) {
        console.log(file);

        let file_path = file.file_path.replace(/\\/g, '/');

        this.fileList.append(`<li data-type="${file.file_mime_type}" 
                                  data-file_original_name="${file.file_original_name}" 
                                  data-file_name="${file.file_name}"
                                  data-file_path="${file_path}"
                                  data-file_mime_type="${file.file_mime_type}">
                                  <a href="#"><img src="/static/attachment/img/file_types${file.mime.icon_sm}"/>${file.file_original_name}</li>`);
        this._serializeFileList();
    };

    this.init(element);
};

export default FileField;
