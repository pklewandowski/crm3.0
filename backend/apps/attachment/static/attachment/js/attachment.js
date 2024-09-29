var tree = $("#tree");
var treeUrl = '/attachment/get-tree/';
var upload_attachment_url = '/attachment/upload/';
var attachment_details_url = '/attachment/details/';
var remove_attachment_url = '/attachment/remove/';
var download_attachment_url = '';
var add_directory_url = '/attachment/add-directory/';

function getTreePath(tree, node, noRoot) {

    let path = '';
    if (node) {
        path = tree.jstree(true).get_path(node, '/');
        if (noRoot) {
            if (node.data.type == 'root') {
                return '';
            }
            path = path.substring(path.indexOf('/') + 1);
        }
    }
    return path;
}

function getTreeNodeSelected(tree) {
    return tree.jstree("get_node", tree.jstree(true).get_node(tree.jstree(true).get_selected()));
}

function updateTreeData(tree, url, id, root_name, root_dir_name) {

    $.ajax(url, {
        dataType: 'json',
        method: 'POST',
        data: {'id': id, 'csrfmiddlewaretoken': window.csrf_token, 'root_name': root_name, 'root_dir_name': root_dir_name},
        success: function (res) {
            if (res.status != "OK") {
                swal({
                    title: "Błąd!",
                    text: res.errMSG,
                    type: 'error',
                    confirmButtonText: "ok"
                });
                return false;
            } else {
                tree.jstree(true).settings.core.data = $.parseJSON(res.tree);
                tree.jstree(true).refresh();
            }
        }
    });
}


function getAttachmentDetails(id) {

    $.ajax(attachment_details_url, {
        dataType: 'json',
        method: 'POST',
        data: {'id': id, 'csrfmiddlewaretoken': window.csrf_token},
        success: function (res) {
            if (res.status != "OK") {
                swal({
                    title: "Błąd!",
                    text: res.errMSG,
                    type: 'error',
                    confirmButtonText: "ok"
                });
                return false;
            } else {
                var details = $('#attachmentDetailsTemplate').clone().html();
                var atm = $.parseJSON(res.data)[0].fields;
                details = details.replace(/__NAME__/, atm.name);
                details = details.replace(/__DATE_ADD__/, moment(atm.creation_date).format('YYYY-MM-DD HH:mm:ss'));
                details = details.replace(/__DESCRIPTION__/, atm.description);
                details = $(details);

                $('.attachment_details tbody').html(details);

            }
        }
    });
}

function clearAttachmentDetails(id) {
    $('.attachment_details tbody').html(null);
}


/*----------------------------------------------------------------*/

$(document).ready(function () {

    var atm_owner_id = atm.id;
    var root_dir_name = atm.root_dir_name;

    tree.on("loaded.jstree", function (event, data) {
        tree.jstree("open_all");
    });

    tree.on("refresh.jstree", function (e, data) {
        $(this).jstree("open_all");
    });

    tree.on('select_node.jstree', function (e, data) {
        var node = data.instance.get_node(data.selected[0]);

        if (node.data.type == 'file') {
            $(".dz-hidden-input").attr("disabled", true);
            $(".add-attachment-btn").attr("disabled", true);
            $(".open-attachment-btn").attr("disabled", false);


            getAttachmentDetails(node.id);

        } else {
            $(".dz-hidden-input").attr("disabled", false);
            $(".add-attachment-btn").attr("disabled", false);
            $(".open-attachment-btn").attr("disabled", true);

            clearAttachmentDetails();
        }

        if (node.data.type == 'root') {
            $(".remove-attachment-btn").attr("disabled", true);
        } else {
            $(".remove-attachment-btn").attr("disabled", false);
        }

    });

    tree.jstree({
        'core': {
            'multiple': false
        }
    });

    updateTreeData(tree, treeUrl, atm_owner_id, root_name, root_dir_name);


//--------------------- ATTACHMENTS ----------------------------

    //attachmentsDropzone = new Dropzone('#_dropzone_attachments', {
    //    url: upload_attachment_url,
    //    uploadMultiple: true,
    //    parallelUploads: 1,
    //    // maxFilesize: 1,
    //    paramName: 'attachments',
    //    autoProcessQueue: false,
    //    previewsContainer: '#attachmentBeforeUpload tbody',
    //    previewTemplate: document.querySelector('#attachmentUploadTemplate').innerHTML,
    //    clickable: true, //".add-attachment-btn",
    //    error: function (file, errMSG) {
    //        swal({
    //            title: "Błąd!?!",
    //            text: errMSG,
    //            type: 'error',
    //            confirmButtonText: "ok"
    //        });
    //        attachmentsDropzone.removeFile(file);
    //    },
    //    sending: function (file, xhr, formData) {
    //        formData.append('csrfmiddlewaretoken', window.csrf_token);
    //        formData.append('atm_classname', atm.classname);
    //        formData.append('atm_owner_classname', atm.owner_classname);
    //        formData.append('atm_owner_id', atm_owner_id);
    //        formData.append('dirname', root_dir_name);
    //        formData.append('attachment_description', $(file.previewElement).find('textarea[name="attachment_description"]').val());
    //        formData.append('path', getTreePath(tree, getTreeNodeSelected(tree), true));
    //        //formData.append('code', $(attachment.previewElement).find('input[name="code"]').val());
    //    }
    //});

    attachmentsDropzone = $('#dropzone_attachments').dropzone({
        url: upload_attachment_url,
        uploadMultiple: true,
        parallelUploads: 1,
        // maxFilesize: 1,
        paramName: 'attachments',
        autoProcessQueue: false,
        previewsContainer: '#attachmentBeforeUpload tbody',
        previewTemplate: document.querySelector('#attachmentUploadTemplate').innerHTML,
        clickable: true, //".add-attachment-btn",
        error: function (file, errMSG) {
            swal({
                title: "Błąd!?!",
                text: errMSG,
                type: 'error',
                confirmButtonText: "ok"
            });
            attachmentsDropzone.removeFile(file);
        },
        sending: function (file, xhr, formData) {
            formData.append('csrfmiddlewaretoken', window.csrf_token);
            formData.append('atm_classname', atm.classname);
            formData.append('atm_owner_classname', atm.owner_classname);
            formData.append('atm_owner_id', atm_owner_id);
            formData.append('dirname', root_dir_name);
            formData.append('attachment_description', $(file.previewElement).find('textarea[name="attachment_description"]').val());
            formData.append('path', getTreePath(tree, getTreeNodeSelected(tree), true));
            //formData.append('code', $(attachment.previewElement).find('input[name="code"]').val());
        }
    });


    attachmentsDropzone.on('addedfile', function (file) {
        if ($('#attachmentBeforeUpload tbody tr').length > 0)
            $('#attachmentBeforeUpload, #addAttachmentFiles').show();
    });

    attachmentsDropzone.on('removedfile', function (file) {
        if ($('#attachmentBeforeUpload tbody tr').length == 0)
            $('#attachmentBeforeUpload, #addAttachmentFiles').hide();
    });

    attachmentsDropzone.on('success', function (file, response) {
        attachmentsDropzone.removeFile(file);
        if (response.status == "ERROR") {
            swal({
                title: "Błąd!",
                text: response.errMSG,
                type: 'error',
                confirmButtonText: "ok"
            });
            attachmentsDropzone.removeAllFiles(true);
            return;
        }

        if (response.status == "OK") {

        }

        if (attachmentsDropzone.getQueuedFiles().length > 0) {
            attachmentsDropzone.processQueue();
        } else {
            updateTreeData(tree, treeUrl, atm_owner_id, root_name, root_dir_name);
        }
    });


    $(".open-attachment-btn").click(function () {

        if ($(this).attr('disabled') == 'disabled') {
            return false;
        }

        var node = getTreeNodeSelected(tree);
        window.location.href = download_attachment_url + '/' + node.id;
        //attachmentsDropzone.hiddenFileInput.click();

    });

    $(".add-attachment-btn").click(function () {

        if ($(this).attr('disabled') == 'disabled') {
            return false;
        }
        $('#addAttachmentForm').modal();
        //attachmentsDropzone.hiddenFileInput.click();

    });

    $('#addAttachmentFiles').click(function () {
        // $(this).hide();
        attachmentsDropzone.processQueue();
    });


    $('body').on('click', '.add-directory-btn', function () {

        var node = getTreeNodeSelected(tree);
        path = getTreePath(tree, node, true);

        if (node && node.data.type != 'directory' && node.data.type != 'root') {
            swal('Proszę wybrać katalog', '', 'warning');
            return;
        }

        dirName = $("#directory-name").val();

        if (dirName == '') {
            swal('Proszę wprowadzić nazwę katalogu', '', 'warning');
            return;
        }
        if (dirName.match(/[\\/?*:|"<>\s]/g)) {

            swal('Nazwa katalogu zawiera znaki niedozwolone!', 'Katalog nie może zawierać znaków \ / ? " *: < > oraz znaków białych (przerw)', 'warning');
            return;
        }

        children = node.children;

        for (i in children) {
            n = tree.jstree(true).get_node(children[i]);

            if (n.data.type == 'directory' && n.text.toLowerCase() === dirName.toLowerCase()) {
                swal('Katalog o podanej nazwie już istnieje!', '', 'warning');
                return;
            }
        }


        swal({
            title: 'Czy na pewno dodać katalog?',
            type: 'warning',
            showCancelButton: true,
            confirmButtonText: "Tak, dodaj!",
            cancelButtonText: "Nie",
            closeOnConfirm: false,
        }, function () {

            var dir = {
                path: (path == false ? '' : path),
                name: dirName,
                root_dir_name: root_dir_name,
                atm_owner_id: atm_owner_id
            };

            $.ajax(add_directory_url, {
                dataType: 'json',
                method: 'POST',
                data: {'directory': dir, 'csrfmiddlewaretoken': window.csrf_token},
                success: function (res) {
                    if (res.status != "OK") {
                        swal({
                            title: "Błąd!",
                            text: res.errMSG,
                            type: 'error',
                            confirmButtonText: "ok"
                        });
                        return false;
                    } else {
                        updateTreeData(tree, treeUrl, atm_owner_id, root_name, root_dir_name);
                        swal('Katalog został dodany!', '', 'success');
                    }
                }
            });
        });
    });

    $('body').on('click', '.remove-attachment-btn', function () {
        if ($(this).attr('disabled') == 'disabled') {
            return false;
        }

        var that = $(this);

        node = getTreeNodeSelected(tree); // tree.jstree("get_node", tree.jstree(true).get_node(tree.jstree(true).get_selected()));
        path = getTreePath(tree, node, true); //tree.jstree(true).get_path(tree.jstree(true).get_selected(), "/");

        if (node.data.type == 'root') {
            swal('Katalog główny nie może być usunięty!', '', 'warning');
            return;
        }

        if (!path) {
            swal('Proszę wybrać plik załącznika lub pusty katalog do usunięcia', '', 'warning');
            return;
        }

        if (node.data.type == 'directory' && tree.jstree("get_children_dom", node).length > 0) {
            swal('Można usunąć jedynie pusty katalog', '', 'warning');
            return;
        }

        swal({
            title: 'Uwaga, usunięcie załącznika lub katalogu jest operacją nieodwracalną. Jesteś pewien?',
            type: 'warning',
            showCancelButton: true,
            confirmButtonText: "Tak, usuń!",
            cancelButtonText: "Nie",
            closeOnConfirm: false
        }, function () {

            var attachment = {
                path: path,
                id: node.id,
                type: node.data.type,
                filename: node.data.filename,
                atm_owner_id: atm_owner_id,
                root_dir_name: root_dir_name,
                atm_classname: atm.classname,
                atm_owner_classname: atm.owner_classname
            };

            $.ajax(remove_attachment_url, {
                dataType: 'json',
                method: 'POST',
                data: {'attachment': attachment, 'csrfmiddlewaretoken': window.csrf_token},
                success: function (res) {

                    if (res.status != "OK") {
                        swal({
                            title: "Błąd!",
                            text: res.msg,
                            type: 'error',
                            confirmButtonText: "ok"
                        });
                        return false;

                    } else {
                        updateTreeData(tree, treeUrl, atm_owner_id, root_name, root_dir_name);
                        if (node.data.type == 'file') {
                            t = 'Załącznik';
                        } else {
                            t = 'Katalog';
                        }
                        swal(t + ' został usunięty!', '', 'success');
                    }
                }
            });
        });
    });
});