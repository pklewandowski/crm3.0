import {SystemException} from "../../../../../_core/exception";

class InterestGlobal {
    constructor(listContainer, formContainer, formTemplate) {
        this.listContainer = jsUtils.Utils.setContainer(listContainer);
        this.formTemplate = jsUtils.Utils.setContainer(formTemplate);
        this.formContainer = jsUtils.Utils.setContainer(formContainer);

        this.form = new formUtils.Form(this.formContainer, this.formTemplate, null, null, {'reloadOnSave': true});

        this.listContainer.addEventListener('click', (evt) => {
            let el = evt.target;
            if (el.classList.contains('edit-interest-global-btn')) {
                this.form.getData(el.closest('tr').dataset['id']);
                this.form.show();
            }
        });
    }

    static delete(id) {
        return ajaxCall({
            method: 'delete',
            url: '/product/global-interest/api/',
            data: {id: id}
        })
    }
}

export default InterestGlobal;