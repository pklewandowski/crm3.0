class ProductForm {
    constructor(id, formContainer, formTemplate) {
        this.id = id;
        this.formTemplate = jsUtils.Utils.setContainer(formTemplate);
        this.formContainer = jsUtils.Utils.setContainer(formContainer);
        this.form = new formUtils.Form(this.formContainer, this.formTemplate, null, null, {'reloadOnSave': true});
    }

}

export {ProductForm}