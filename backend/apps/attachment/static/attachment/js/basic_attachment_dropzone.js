MyDropzone = function (opt) {

    var _this = this;

    this.uploadUrl = opt.uploadUrl;
    this.container = opt.container;
    this.previewContainer = opt.previewContainer;
    this.previewTemplate = opt.previewTemplate;
    this.dropzoneForm = opt.dropzoneForm;
    this.path = null;
    this.getPath = opt.getPath ? opt.getPath : null;
    this.onSavedFiles = opt.onSavedFiles;
    this.onComplete = opt.onComplete ? opt.onComplete : null;
    this.documentId = opt.documentId ? opt.documentId : null;
    this.createAttachment = opt.createAttachment ? opt.createAttachment : null;

    this.getParent = opt.getParent ? opt.getParent : null;

    this._getPath = function () {
        return this.path;
    };

    this.init = function createDropzone() {

        let dz = new Dropzone(this.container, {
            timeout: 300000,
            createElement: 'tr',
            url: _this.uploadUrl,
            uploadMultiple: true,
            parallelUploads: 1,
            // maxFilesize: 1,
            paramName: 'attachments',
            autoProcessQueue: false,
            previewsContainer: _this.previewContainer,
            previewTemplate: $(_this.previewTemplate).html(),
            clickable: true, //".add-attachment-btn",
            error: function (file, err) {
                console.log(err);
                swal({
                    title: "Błąd!?!",
                    text: err.errmsg,
                    type: 'error',
                    confirmButtonText: "ok"
                });
                dz.removeFile(file);
            },
            // addedfile: function (file) {
            //     console.log(this);
            //
            //     file.previewElement = Dropzone.createElement(this.options.previewTemplate, this.options.createElement);
            //     // Now attach this new element some where in your page
            //     console.log(file.previewElement);
            //     $(this.options.previewsContainer).append(file.previewElement);
            // },
            // uploadprogress: function (file, progress, bytesSent) {
            //     console.log(progress)
            // }
        });

        // dz.on('uploadprogress', function (file, progress, bytesSent) {
        //     console.log(progress)
        // });

        dz.on('sending', function (file, xhr, formData) {

            let path=_this._getPath();

            if (!path && typeof _this.getPath === 'function') {
                path = _this.getPath();
            }

            if (path) {
                formData.append("path", path);
            }
            if (_this.documentId) {
                formData.append('documentId', _this.documentId)
            }

            if(_this.createAttachment) {
                formData.append('createAttachment', _this.createAttachment)
            }
        });


        //  dz.on('addedfile', function (file) {
        //     file.previewElement = dz.createElement(dz.options.previewTemplate, dz.options.createElement);
        //     // if ($(_this.previewContainer).find('tr').length > 0) {
        //     //     $(`${_this.dropzoneForm} #addAttachmentFiles`).show();
        //     // }
        //     alert('added');
        // });

        dz.on('removedfile', function (file) {
            if ($(_this.container).find('#attachmentBeforeUpload').find('div#scan_preview_container').length > 0) {
                $(`${_this.dropzoneForm} #addAttachmentFiles`).hide();
            }
        });

        dz.on('success', function (file, response) {
            let _file = file;
            dz.removeFile(file);
            if (response.status === "ERROR") {
                swal({
                    title: "Błąd!",
                    text: response.errMSG,
                    type: 'error',
                    confirmButtonText: "ok"
                });
                dz.removeAllFiles(true);
                return;
            }

            $.each(response.saved_files, function (i, e) {
                _this.onSavedFiles(i, e, _file);
            });

            if (dz.getQueuedFiles().length > 0) {
                dz.processQueue();
            }
        });

        dz.on('queuecomplete', function () {
            if (typeof _this.onComplete === 'function') {
                _this.onComplete();
            }
            $(_this.dropzoneForm).modal('hide');
        });

        $(`${_this.dropzoneForm} #addAttachmentFiles`).click(function () {
            // $(this).hide();
            dz.processQueue();
        });

        return dz;
    };
    this.dz =this.init();

};