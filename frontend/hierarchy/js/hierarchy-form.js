import {SystemException} from "../../_core/exception";
import Utils from "../../_core/utils/utils";

const hierarchyTypesDisableGuide = {
    'ROOT': ['HDQ', 'DEP', 'POS'],
    'CMP': ['CMP', 'POS'],
    'HDQ': ['CMP', 'HDQ', 'POS'],
    'DEP': ['CMP', 'HDQ'],
};

class HierarchyForm {
    constructor(container) {
        this.container = Utils.setContainer(container);
        this.groups = null;
        this.form = this.container.querySelector('form');
        this.submitButton = this.form.querySelector('.save-hierarchy-btn');
        this.getGroups();
    }

    _populateGroups() {
        let groups = this.form.querySelector('#groupSelect2');
        groups.innerHTML = null;
        for (let group of this.groups) {
            groups.appendChild(new Option(group.name, group.id));
        }
        $(groups).select2();
    }

    getGroups() {
        ajaxCall({
                method: 'get',
                url: _g.hierarchy.urls.groupUrl,
            },
            (groups) => {
                this.groups = groups;
                this._populateGroups();
            },
            (resp) => {
                jsUtils.LogUtils.log(resp.responseJSON);
            }
        )
    }

    getData(nodeId) {
        if (!nodeId) {
            return new Promise((resolve, reject) => {
                resolve(null);
            });
        }
        return ajaxCall({
                method: 'get',
                url: _g.hierarchy.urls.apiUrl,
                data: {nodeId: nodeId, detail: true}
            },
            (data) => {
                return data;
            },
            (resp) => {
                jsUtils.LogUtils.log(resp.responseJSON);
            }
        )
    }

    getFormData() {
        let hierarchy = {};
        for (let item of Array.from(
            this.form.querySelector('fieldset#hierachyFormHierarchyData').querySelectorAll('input, select, textarea'))) {
            hierarchy[item.name] = item.value;
        }
        hierarchy.hierarchy_groups = [];
        for (let group of $(this.form.querySelector('#groupSelect2')).select2('data')) {
            hierarchy.hierarchy_groups.push({id: parseInt(group.id)});
        }

        hierarchy.address = {}
        for (let item of Array.from(
            this.form.querySelector('fieldset#hierachyFormAddressData').querySelectorAll('input, select, textarea'))) {
            hierarchy.address[item.name] = item.value;
        }

        return hierarchy;
    }

    _resetForm() {
        this.form.querySelector('[name="type"]').removeAttribute('disabled');
        this.form.querySelector('[name="type"]').value = null;
        for (let i of Array.from(this.form.querySelectorAll('[name="type"] option'))) {
            i.removeAttribute('disabled');
        }
        for (let opt of Array.from(this.form.querySelector('[name="type"] option'))) {
            opt.removeAttribute('disabled');
        }

        for (let item of Array.from(
            this.form.querySelectorAll('input, select, textarea'))) {
            item.value = null;
        }
    }

    _disableHierarchyTypes(type) {
        for (let i of hierarchyTypesDisableGuide[type]) {
            this.form.querySelector(`select[name="type"] option[value="${i}"]`).setAttribute('disabled', 'disabled');
        }
    }

    _populateForm(data, parent) {
        if (!parent) {
            throw new SystemException('Brak parent id dla node');
        }

        this.form.querySelector('[name="parent"]').value = parent.id;
        let groups = this.form.querySelector('#groupSelect2');
        $(groups).val(data?.hierarchy_groups);
        $(groups).trigger('change');

        if (data) {
            this.form.querySelector('[name="id"]').value = data.id;

            this.form.querySelector('[name="type"]').setAttribute('disabled', 'disabled');
            this.form.querySelector('[name="type"]').value = data.type;
            this.form.querySelector('[name="name"]').value = data.name;
            this.form.querySelector('[name="nip"]').value = data.nip;
            this.form.querySelector('[name="regon"]').value = data.regon;
            this.form.querySelector('[name="krs"]').value = data.krs;
            this.form.querySelector('[name="email"]').value = data.email;
            this.form.querySelector('[name="phone"]').value = data.phone;
            this.form.querySelector('[name="share_capital_amount"]').value = data.share_capital_amount;

            this.form.querySelector('[name="description"]').value = data.description? data.description : '';

            if (data.address) {
                this.form.querySelector('[name="street"]').value = data.address.street;
                this.form.querySelector('[name="street_no"]').value = data.address.street_no;
                this.form.querySelector('[name="apartment_no"]').value = data.address.apartment_no;
                this.form.querySelector('[name="post_code"]').value = data.address.post_code;
                this.form.querySelector('[name="city"]').value = data.address.city;
                this.form.querySelector('[name="country"]').value = data.address.country;
                this.form.querySelector('[name="address_id"]').value = data.address.id;
            }

        } else {
            this._disableHierarchyTypes(parent.type);
        }
    }

    show(nodeId = null, parent = null) {
        this._resetForm();
        this.getData(nodeId).then((node) => {
            this._populateForm(node, parent ? parent : node?.parent);
            $(this.container).modal('show');
        });
    }

    hide() {
        $(this.container).modal('hide');
    }
}

export {HierarchyForm};