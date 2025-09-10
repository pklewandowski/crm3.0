import Utils from "../../_core/utils/utils";

class HierarchyUser {
    constructor(container) {
        this.container = Utils.setContainer(container);
        this.userTable = this.container.querySelector('.user-list-table');
        this.userTableBody = this.userTable.querySelector('tbody');
        this.hierarchyId = this.container.querySelector('input[name="userListHierarchy"]');
        this.userInput = $('#addUserInputId');

        this._setAddUserInput(this.userInput);
        this._setDeleteUser();
    }

    _clear() {
        this.userTableBody.innerHTML = null;
        this.hierarchyId.value = null;
        this.userInput.empty();
    }

    _getUserRow(user) {
        let row = <tr>
            <td>{user.first_name ? user.first_name : ''}&nbsp;{user.last_name ? user.last_name : ''}</td>
            <td>{user.email ? user.email : '-'}</td>
            <td>{user.personal_id ? user.personal_id : '-'}</td>
            <td>{user.nip ? user.nip : '-'}</td>
            <td className={"hierarchy-user-delete delete-user"}><i className={"fa fa-trash-alt"} style={"pointer-events: none"}></i></td>
        </tr>;

        row.dataset.id = user.id;

        return row;
    }

    _populateUsers(data, container) {
        container.innerHTML = null;

        for (let item of data) {
            container.appendChild(this._getUserRow(item.user));
        }
    }

    _getUsers(nodeId) {
        return ajaxCall({
                method: 'get',
                url: _g.hierarchy.urls.employeeUrl,
                data: {id: nodeId}
            }
        )
    }

    populate(nodeId) {
        this._clear();
        this.hierarchyId.value = nodeId;

        this._getUsers(nodeId).then(
            (data) => {
                this._populateUsers(data, this.userTableBody);
            },
            (resp) => {
                jsUtils.LogUtils.log(resp.responseJSON);
                Alert.error(null, resp.responseJSON.errmsg, null, null, resp.responseJSON.errtype);
            }
        );
    }

    show(nodeId, reset = true) {
        $(this.container).modal('show');
        this.populate(nodeId);
    }

    _setAddUserInput(container) {
        let el = $(container);
        let _that = this;

        el.select2({
            allowClear: true,
            ajax: {
                method: 'get',
                url: _g.hierarchy.urls.getEmployeeUrl,
                dataType: 'json',
                delay: 200,
                data: function (params) {
                    return {
                        q: params.term,
                        page: params.page,
                        nodeId: _that.hierarchyId.value,
                        csrfmiddlewaretoken: _g.csrfmiddlewaretoken
                    };
                }
            },
            theme: 'bootstrap',
            minimumInputLength: 2,
            language: "pl",
            dropdownParent: $("#userListModal")

        });

        el.on('change', (e) => {
            _that.addUser(el.val())
        })
    }

    _setDeleteUser() {
        this.userTable.addEventListener('click', (e) => {
            let el = e.target;
            if (el.classList.contains('delete-user')) {
                let tr = el.closest('tr');
                let userId = tr.dataset.id;
                let hierarchyId = this.hierarchyId.value;

                Alert.questionWarning('Czy na pewno usunąć pracownika ze stanowiska?',
                    '',
                    () => {
                        ajaxCall({
                                method: 'delete',
                                url: _g.hierarchy.urls.employeeUrl,
                                data: {nodeId: hierarchyId, userId: userId}
                            },

                            (data) => {
                                tr.remove();
                            },
                            (resp) => {
                                jsUtils.LogUtils.log(resp.responseJSON);
                                Alert.error(null, resp.responseJSON.errmsg, null, null, resp.responseJSON.errtype);
                            });
                    });
            }
        })
    }

    addUser(userId) {
        let hierarchyId = this.hierarchyId.value;
        let _that = this;

        Alert.questionWarning('Czy dodać wybranego pracownika do stanowiska?',
            '',
            () => {
                ajaxCall({
                        method: 'post',
                        url: _g.hierarchy.urls.employeeUrl,
                        data: {nodeId: hierarchyId, userId: userId}
                    },

                    (user) => {
                        this.userTableBody.appendChild(this._getUserRow(user));
                    },
                    (resp) => {
                        jsUtils.LogUtils.log(resp.responseJSON);
                        Alert.error(null, resp.responseJSON.errmsg, null, null, resp.responseJSON.errtype);
                    });
            },
            '',
            () => {
                _that.userInput.empty();
            }
        )
    }
}

export {HierarchyUser};