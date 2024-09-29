

const className = 'FormValidation';

class FormValidation {
    constructor(container) {
        this.container = container;
    }

    static _renderErrorContainer(container) {
        let errorContainer = jsUtils.Utils.domElement('div', '', ['error-container', 'dropdown-layer']);
        errorContainer.appendChild(jsUtils.Utils.domElement('ul'));
        container.appendChild(errorContainer);

        let errorCheck = jsUtils.Utils.domElement('div', '', 'error-check');
        errorCheck.appendChild(jsUtils.Utils.domElement('i', '', ['fa', 'fa-times']));
        errorCheck.addEventListener('click', () => {
            errorContainer.style.display = 'block';
        });
        container.appendChild(errorCheck);
        return errorContainer
    }

    static _getItem(itemName, getBy) {
        let item = null;
        switch (getBy) {
            case 'code':
                item = Input.getByCode(itemName);
                break;
            case 'name':
                item = Input.getByName(itemName);
                break;
            default:
                break;
        }
        return item;
    }

    static addErrors(errorList, getBy = 'code', idPrefix = '', directItem = null) {
        if (!errorList) {
            jsUtils.LogUtils.log(`[${className}][attachErrors]: errorList appear to be empty`);
            return;
        }

        for (let [itemName, errors] of Object.entries(errorList)) {
            let item = directItem ? directItem : FormValidation._getItem(itemName, getBy);

            if (item) {
                let fg = directItem ? directItem : item.closest('.form-group');

                if (fg) {
                    fg.classList.add('error');
                    let errorContainer = fg.querySelector('.error-container');
                    if (!errorContainer) {
                        errorContainer = FormValidation._renderErrorContainer(fg);
                    }

                    let ul = errorContainer.querySelector('ul');

                    for (let j of errors) {
                        let li = jsUtils.Utils.domElement('li');
                        li.innerText = j;
                        ul.appendChild(li);
                    }
                }
            }
        }
    }

    static removeErrors(container = null) {
        let _container = document;

        if (container) {
            _container = container;
        }

        for (let i of Array.from(_container.querySelectorAll('.form-group.error'))) {
            i.classList.remove('error');
            i.querySelector('.error-container').remove();
            i.querySelector('.error-check').remove();
        }
    }
}

export default FormValidation;