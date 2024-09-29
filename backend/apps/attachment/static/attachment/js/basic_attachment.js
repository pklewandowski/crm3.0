import AttachmentDirectoryTree from './attachment-directory-tree.js';

//TODO: DRUT!!! docelowo zmienić
var mediaUrl = '/media/';
var draggedItem;
var atmTree;

function fillTemplate(data) {

    let attachment_total_forms = $('#id_attachment-TOTAL_FORMS');
    let tmpl = $("#file_thumbnail_template").html();
    let icSize = '';
    let iSize = '';
    if ($("#atmSizeToggle").hasClass('thumbnail-size-small')) {
        icSize = 'thumbnail-image-container-small';
        iSize = 'thumbnail-image-small';
    }
    tmpl = tmpl.replace(/__THUMBNAIL_SIZE__/g, icSize);
    tmpl = tmpl.replace(/__THUMBNAIL_IMAGE_SIZE__/g, iSize);
    tmpl = tmpl.replace(/__FILE_ORIGINAL_NAME__/g, data.file_original_name);
    tmpl = tmpl.replace(/__FILE_NAME__/g, data.file_name);
    tmpl = tmpl.replace(/__FILE_PATH__/g, data.file_path);
    tmpl = tmpl.replace(/__FILE_EXT__/g, data.file_ext);
    tmpl = tmpl.replace(/__FILE_MIME_TYPE__/g, data.mime.type);
    tmpl = tmpl.replace(/__ATTACHMENT_TYPE__/g, data.attachment_type ? data.attachment_type : 'file');
    tmpl = tmpl.replace(/__ATTACHMENT_ID__/g, data.attachment_id);

    if (data.attachment_type && data.attachment_type.indexOf('folder') !== -1) {
        tmpl = tmpl.replace(/__FILE_ICON__/g, '/static/attachment/img/folder.png')
    } else {
        if (data.mime.type.indexOf('image') !== -1) {
            tmpl = tmpl.replace(/__FILE_ICON__/g, mediaUrl + data.file_path + data.file_name);
        } else {
            if (data.mime.icon_lg) {
                tmpl = tmpl.replace(/__FILE_ICON__/g, '/static/attachment/img/file_types/' + data.mime.icon_lg)
            }
        }
    }

    tmpl = tmpl.replace(/__prefix__/g, attachment_total_forms.val());
    attachment_total_forms.val(parseInt(attachment_total_forms.val()) + 1);

    $("#file_thumbnail_film").append(tmpl);
}

function setAttachmentVisibility(node) {

    let _node;

    function toggleAttachments(node) {
        $(".thumbnail-image-container").hide();
        $(node.children).each(function (i, e) {
            $(`.thumbnail-image-container[data-id="${e}"]`).show();
        });
    }

    if (!node) {
        return;
    }

    if (['directory', 'root'].indexOf(node.data.type) > -1) {
        _node = node;
    } else if (node.data.type === 'file') {
        console.log('file');
        _node = this.getNodeById(node.parent);

    }

    toggleAttachments(_node)
}

$(document).ready(function () {
    // let upload_attachment_url = '/attachment/basic/file-upload/';
    // let upload_prtscn_url = '/attachment/basic/prtscn-upload/';


    if (!_g.document.id) {
        return;
    }

    let documentId = _g.document.id;

    atmTree = new AttachmentDirectoryTree(
        "atmDirectoryTree",
        documentId,
        _g.document.attachment.root_name,
        {
            onSelect: setAttachmentVisibility
        });


    //let CLIPBOARD = new CLIPBOARD_CLASS("paste_canvas", true);


    $(document).on("contextmenu", ".thumbnail-image-container", function (e) {
        e.preventDefault();
        console.log('thumbail context menu');
    });

    $(document).on("dragstart", ".thumbnail-image-container .thumbnail-image img", function (evt) {
        console.log("dragstart");

        if (!evt) {
            return false;
        }
        atmTree.setDraggedItem(evt.target);
        evt.target.style.opacity = .3;
    });

    $(document).on("dragend", ".thumbnail-image-container", function (evt) {
        evt.target.style.opacity = "";
    });


    $("#add_file_btn").click(function () {
        $("#addAttachmentForm").modal();
    });

    $("#paste_screen_btn").click(function () {

        let canvas = $("#paste_canvas")[0];
        let ctx = canvas.getContext("2d");
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        canvas.width = 300;
        canvas.height = 300;
        $("#paste_screen_modal").modal();
        $("#paste_screen_modal #prtscn_description").val(null);
    });

    $('#add_printscreen_btn').click(function () {
        console.log(documentId);

        $.ajax({
            type: 'post',
            url: upload_prtscn_url,
            data: {
                'documentId': documentId,
                'createAttachment': true,
                'image_data': document.getElementById('paste_canvas').toDataURL('image/jpeg'),

            }
        }).done(function (res) {
            fillTemplate(res);
            $("#file_thumbnail_film .thumbnail-image-container").last().focus();

        }).fail(function (res) {
            swal(res.msg, '', 'error');
        }).always(function () {
            $('#paste_screen_modal').modal('hide');
        });

    });

    $(function () {
        Dropzone.createElement = function (string) {
            var el = $(string);
            return el[0];
        };
    });

    let atmDropzone = new MyDropzone({
        uploadUrl: upload_attachment_url,
        container: '#addAttachmentForm #dropzone_atm',
        previewTemplate: '#attachmentUploadTemplate',
        previewContainer: '#addAttachmentForm #attachmentBeforeUpload tbody',
        dropzoneForm: '#addAttachmentForm',
        documentId: documentId,
        createAttachment: true,

        getPath: function () {
            let node = atmTree.getSelected();
            if (node) {
                let path = atmTree.getPath(node, true);
                return path ? path : '';
            } else {
                return '';
            }
        },

        onSavedFiles: function (i, e, file) {
            fillTemplate(e);
            $("#file_thumbnail_film .thumbnail-image-container").last().focus();
        },

        onComplete: function () {
            atmTree.update();
        }

    });

    $('#addAttachmentForm').on('hidden.bs.modal', function () {
        atmDropzone.removeAllFiles();
    });


    function _thumbnailToggle(e, remove) {

        let formset_row_delete = e.closest('.thumbnail-image-container').find('.formset-row-delete');
        console.log(formset_row_delete);
        let file = e.closest('.thumbnail').find('img').attr('src').split('/');
        let filename = file[file.length - 1];
        if (remove) {
            e.closest('.thumbnail').addClass('thumbnail-removed');
            formset_row_delete.val(1)
        } else {
            e.closest('.thumbnail').removeClass('thumbnail-removed');
            formset_row_delete.val(null)
        }
        e.closest('.thumbnail').find('.thumbnail-btn').toggle();
        return filename;
    }

    $(document).on('click', ".thumbnail-close-btn", function (e) {
        e.stopPropagation();
        let _this = $(this);

        Alert.questionWarning(
            'Jesteś pewien?',
            'Czy na pewno usunąć załącznik?',
            () => {
                let filename = _thumbnailToggle(_this, true);
                $('form input.thumbnail-value[value="' + filename + '"]').attr('disabled', true);
            });
    });

    $(document).on('click', ".thumbnail-restore-btn", function (e) {
        e.stopPropagation();
        let _this = $(this);

        Alert.questionWarning(
            'Jesteś pewien?',
            'Czy na pewno przywrócić załącznik?',
            () => {
                let filename = _thumbnailToggle(_this);
                $('form input.thumbnail-value[value="' + filename + '"]').removeAttr('disabled');
            });
    });

    $(document).on('click', '.thumbnail-image', function () {
        let mimeType = $(this).data('mime_type');
        let id = $(this).data('id');
        let fileName = $(this).data('file_name');
        if (mimeType.indexOf('image') === -1) {
            if (id) {
                window.location = '/attachment/download/' + id + '/';
                return;
            } else {
                swal('Plik będzie dostępny do podglądu po zapisaniu danych', '', 'info');
                return;
            }
        }

        var src = $(this).find('img').attr('src');
        $('#image_preview').attr('src', src);
        $('#image_preview_modal').modal();
    });


    $(document).on('click', '.file-upload-field-list li', function () {
        let id = $(this).data('id');
        let mimeType = $(this).data('file_mime_type');
        let fileName = $(this).data('file_name');
        let filePath = $(this).data('file_path').replace(/\\/g, '/');

        if (mimeType.indexOf('image') === -1) {
            window.location = `/attachment/download/`;
            return;
        }

        $('#image_preview').attr('src', `/media/${filePath}${fileName}`);
        $('#image_preview_modal').modal();
    });


    $(document).on('click', '.prtscn-thumbnail', function () {
        var src = $(this).find('img').attr('src');
        $('#image_preview').attr('src', src);
        $('#image_preview_modal').modal();
    });

    $(document).on('click', '.scroll-text', function () {
        $(this).closest('.thumbnail-image-container').find('img').toggleClass('blur-grayscale');
        $(this).closest('.thumbnail-image-container').find('.attachment-description').toggle('slow');
    });

    $("#atmSizeToggle").click(function () {
        $(this).toggleClass("thumbnail-size-small");

        $("#file_thumbnail_film").find(".thumbnail-image").toggleClass("thumbnail-image-small");
        $("#file_thumbnail_film").find(".thumbnail-image-container").toggleClass("thumbnail-image-container-small");
    });

    $("#atmFolderAddBtn").click(function () {
        console.log('add folder');
        data = {
            file_original_name: $("#atmFolderName").val(),
            file_name: $("#atmFolderName").val(),
            file_path: '/static/attachment/img/file_types/',
            file_ext: '',
            attachment_type: 'folder',
            mime: {
                type: 'folder',
            }
        };
        fillTemplate(data);
    });

    $(".atm-play-music").click(function (e) {
        e.stopPropagation();
        let speakerIcon = $(this).find("i");
        let audio = $(this).closest('.thumbnail-image-container').find(".audio")[0];
        audio.crossOrigin = "anonymous";
        if (speakerIcon.hasClass('fa-play-circle')) {
            audio.play();
        } else {
            audio.pause();
        }
        speakerIcon.toggleClass('fa-stop-circle fa-play-circle');
    });
});

export {fillTemplate, atmTree}
