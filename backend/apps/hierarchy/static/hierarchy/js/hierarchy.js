function hierarchyFormReset() {
    $('form#hierarchy-form')[0].reset();
    $.each($("form#hierarchy-form textarea"), function () {
        $(this).text(null);
    });

    $.each($('form#hierarchy-form input[name="privs"]'), function () {
        $(this).prop('checked', false);
    });
}

$(document).ready(function () {

        $('#userListModal').modal({
            keyboard: false,
            backdrop: 'static',
            show: false
        });

        new Treant(chartConfig);

        $('.add-hierarchy').click(function () {
            hierarchyFormReset();
            $('#addHierarchyFormModal').modal('show');
            $('#addHierarchyFormModal input[name="parent"]').val($(this).data('id'));
            // $('#addHierarchyFormModal input[name="type"]').val('C');
        });

        $('.edit-hierarchy').click(function () {
            hierarchyFormReset();
            $('#addHierarchyFormModal').modal('show');
            document.querySelector('#addHierarchyFormModal select[name="type"]').value = this.dataset['type'];
            $('#addHierarchyFormModal input[name="name"]').val(this.dataset['name']);
            $('#addHierarchyFormModal textarea[name="description"]').text(this.dataset['description']);
            $('#addHierarchyFormModal input[name="id"]').val(this.dataset['id']);
            $('#addHierarchyFormModal input[name="parent"]').val(this.dataset['parent']);

            var gr = $(this).data('groups').split(",");

            $.each(gr, function (i, e) {
                if (e != null && e != '') {
                    $.each($("input[name='group']"), function (j, g) {
                        if ($(g).val() == e) {
                            $(g).prop('checked', true);
                        }
                    });
                }
            });
        });

        $('.delete-hierarchy').click(function () {
            let that = $(this);

            Alert.questionWarning("Jesteś pewien?", "Usunięcie gałęzi jest procesem nieodwracalnym!",
                () => {
                    $('#delete-hierarchy-form input[name="node_id"]').val($(that).data('id'));
                    $('#delete-hierarchy-form').submit();
                });
        });

        $(".add-user").click(function () {
            Alert.question("Czy na pewno dodać pracownika?", '',
                () => {
                    window.location.href = "/user/add";
                });
        });

        $(".user-list").click(function () {
            that = $(this);

            function userList(result) {
                let res = $.parseJSON(result.data);
                $("table#user_list_table tbody").html(null);

                $.each(res, function (i, e) {
                    var row = $("#user_list_template").html();

                    row = row.replace("__USEREDIT_URL__", _g.hierarchy.urls.userEditUrl);
                    row = row.replace("__ID__", e.pk);
                    row = row.replace("__NAME_SURNAME__", e.fields.first_name + ' ' + e.fields.last_name);
                    row = row.replace("__EMAIL__", e.fields.email);
                    row = row.replace("__PERSONAL_ID__", e.fields.personal_id);
                    row = row.replace("__NIP__", e.fields.nip);

                    $("table#user_list_table tbody").append(row);
                });

                $("#userListModal .modal-title span").text(that.closest("div").children(".node-name").text());
                $('#userListModal').modal('show');
            }

            ajaxCall({
                    method: 'POST',
                    url: _g.hierarchy.urls.employeeUrl,
                    data: {id: that.data("id")}
                },
                (resp) => {
                    userList(resp);
                },
                (resp) => {
                    console.log(resp);
                }
            );
        });

        let dragOver = null;
        let dragStart = null;


        function getDropable(node, id, dropableList) {
            for (let i of node) {
                if (i.id != id) {
                    if (i.type !== 'POS') {
                        dropableList.push(i.id);
                    }

                    if (i.children) {
                        getDropable(i.children, id, dropableList);
                    }
                } else {
                    // if node is that selected then remove its parent from dropable cause its just attached to
                    let idx = dropableList.indexOf(i.parentId);
                    if (idx !== -1) {
                        dropableList.splice(dropableList.indexOf(i.parentId), 1);
                    }
                }
            }
        }


        function handleDragStart(e) {
            let dropableList = [];

            dragStart = e.target.parentElement.dataset['id'];

            getDropable(chartConfig.nodeStructure.children, dragStart, dropableList);

            for (let i of dropableList) {
                document.querySelector(`[data-id="${i}"] .node-dropable`).style.display = 'inherit';
            }

            e.dataTransfer.setData("text/html", '<div><<i class="fa-edit"></i>/div>');
            e.effectAllowed = 'move';
            console.log('dragStart', dragStart);
        }

        function handleDragOver(e) {
            e.preventDefault();
        }

        function handleDragEnd(e) {
            items = document.querySelectorAll('.node-dropable');
            items.forEach(function (item) {
                item.style.display = 'none';
            });
            console.log('dragEnd', e.target.parentElement.dataset['id']);
        }

        function handleDrop(e) {
            if (e.target.parentElement.dataset['id'] === dragStart) {
                return;
            }
            Alert.questionWarning('Czy na pewno przenieść element?', '', () => {
                ajaxCall({
                        method: 'put',
                        url: _g.hierarchy.urls.moveUrl,
                        data: {nodeId: dragStart, nodeTo: e.target.parentElement.dataset['id']}
                    },
                    () => {
                        window.location.reload();
                    },
                    (resp) => {
                        Alert.error('Błąd!', resp.responseJSON.errmsg);
                    })
            });
        }

        function handleDragEnter(e) {
            e.preventDefault();
            console.log('dragEnter', dragOver);
        }

        function handleDragLeave(e) {
            dragOver = null;
            this.classList.remove('hierarchy-dragenter');
            console.log('dragLeave', this.dataset['id']);
        }

        let items = document.querySelectorAll('.node-draggable');
        items.forEach(function (item) {
            item.addEventListener('dragstart', handleDragStart);
            item.addEventListener('dragend', handleDragEnd);
        });

        items = document.querySelectorAll('.node-dropable');
        items.forEach(function (item) {
            // item.addEventListener('dragenter', handleDragEnter);
            item.addEventListener('drop', handleDrop);
            item.addEventListener('dragover', handleDragOver);
        });
    }
)
;