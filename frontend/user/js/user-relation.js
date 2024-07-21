import ajaxCall from "../../_core/ajax";

import Alert from "../../_core/alert";
import {ToolbarUtils} from "../../_core/utils/toolbar-utils";
import {SystemException} from "../../_core/exception";
import FormValidation from "../../_core/form/form-validaion";

const className = 'UserRelation';

class UserRelation {
    constructor(container, userId = null, userRelationUrl = null) {
        this.container = container; // should be the panel body covering table handling user relation
        if (!this.container) {
            throw new SystemException(`[${className}][constructor]: Brak podanego kontenera`);
        }
        this.rowContainer = this.container.querySelector('table tbody');

        this.userId = userId ? userId : _g.user.id;
        if (!this.userId) {
            throw new SystemException(`[${className}][constructor]: Brak id użytkownika`);
        }
        this.modal = document.getElementById('userRelationModal');
        if (!this.modal) {
            throw new SystemException(`[${className}][constructor]: Nie zdefiniowano formularza modalnego dla utworzenia nowej relacji`);
        }
        this.newRelationBtn = document.getElementById('newRelationBtn');
        if (!this.newRelationBtn) {
            throw new SystemException(`[${className}][constructor]: Nie zdefiniowano przycisku nowej relacji`);
        }

        this.saveRelationBtn = document.getElementById('saveRelationBtn');
        if (!this.saveRelationBtn) {
            throw new SystemException(`[${className}][constructor]: Nie zdefiniowano przycisku nowej relacji`);
        }

        this.userRelationUrl = userRelationUrl ? userRelationUrl : _g.user.urls.userRelationUrl;
        if (!this.userRelationUrl) {
            throw new SystemException(`[${className}][constructor]: Nie zdefiniowano url`);
        }

        this.init();
    }

    getData() {
        return ajaxCall({
                method: 'get',
                url: this.userRelationUrl,
                data: {userId: this.userId}
            },
            null,
            (resp) => {
                jsUtils.LogUtils.log(resp.responseJSON.errmsg);
                Alert.error('Wystąpił wyjątek systemowy:', resp.responseJSON.errmsg);
            })
    }

    refresh() {
        this.getData().then(data => {
            if(this.rowContainer) {
                this.rowContainer.innerHTML = null;
            }
            this.render(data);
        });
    }

    save() {
        ajaxCall({
                method: 'post',
                url: this.userRelationUrl,
                data: $("form#userRelationForm").serialize()
            },
            () => {
                $(this.modal).modal('toggle');
                this.refresh();

            },
            (resp) => {
                FormValidation.addErrors(resp.responseJSON.errors);
                jsUtils.LogUtils.log(resp.responseJSON.errmsg);
                Alert.error('Wystąpił wyjątek systemowy:', resp.responseJSON.errmsg);
            })
    }

    delete(row) {
        ajaxCall({
                method: 'delete',
                url: this.userRelationUrl,
                data: {relationId: row.dataset['id']}
            },
            () => {
                row.remove();
                // Alert.info('Relacja usunięta');
            },
            (resp) => {
                jsUtils.LogUtils.log(resp.responseJSON.errmsg);
                Alert.error('Wystąpił wyjątek systemowy:', resp.responseJSON.errmsg);
            })
    }

    renderRowContainer() {

        this.container.innerHTML = `<table class="table table-hover table-striped"><thead>
        <tr>
                                            <th>Osoba</th>
                                            <th>Typ relacji</th>
                                            <th style="width:60px;"></th>
                                        </tr>
                                        </thead>
                                        <tbody></tbody></table>`;

        this.rowContainer = this.container.querySelector('table tbody');
    }


    render(data) {
        let _this = this;
        if (!data.left.length && !data.right.length) {
            this.container.innerHTML = '<h5>Brak powiązanych osób</h5>';
            return;
        }

        if (!this.rowContainer) {
            this.renderRowContainer();
        }

        function _render(data, site) {
            for (let i of data) {
                let tr = jsUtils.Utils.domElement('tr');
                tr.dataset['id'] = i.id;

                let td = jsUtils.Utils.domElement('td');
                td.innerText = site === 'L' ? `${i.right.first_name} ${i.right.last_name}` : `${i.left.first_name} ${i.left.last_name}`;
                tr.appendChild(td);

                td = jsUtils.Utils.domElement('td');
                td.innerText = site === 'L' ? i.type.right_name : i.type.left_name;
                tr.appendChild(td);

                td = jsUtils.Utils.domElement('td');
                let delBtn = ToolbarUtils.deleteBtn();
                delBtn.addEventListener('click', (e) => {
                    Alert.questionWarning('Czy na pewno usunąć relację?', 'Relacja zostanie bezpowrotnie usunięta z bazy danych.', (e) => {
                        _this.delete(e.target.closest('tr'));
                    }, e);
                });

                td.appendChild(delBtn);
                tr.appendChild(td);

                _this.rowContainer.appendChild(tr);
            }
        }

        _render(data.left, 'L');
        _render(data.right, 'R');
    }

    init() {
        this.getData();
        // this.modal.querySelector('input[name="userrelation-right"]').dataset['autocomplete_url'] = _g.user.urls.clientAutocompleteUrl;
        this.newRelationBtn.addEventListener('click', () => {
            document.getElementById('id_userrelation-right').value = null;
            document.getElementById('id_userrelation-type').value = null;
            document.getElementById('id_userrelation-description').value = null;
            $(this.modal).modal();
        });

        this.saveRelationBtn.addEventListener('click', () => {
            this.save()
        });
        document.getElementById('id_userrelation-left').value = this.userId;
    }
}

export {UserRelation};