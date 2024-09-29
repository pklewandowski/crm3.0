import IMask from "imask";

class BalanceControl {
    constructor(at, initialValue) {
        this.at = at;
        this.percentLeft = jsUtils.Utils.domElement('input', `${at.id}_pl`, ['form-control', 'input-md', 'text-right']);// todo: finally get inpyt classes from somwhere global settings
        this.percentLeft.readOnly = true;
        this.percentRight = jsUtils.Utils.domElement('input', `${at.id}_pr`, ['form-control', 'input-md', 'text-right']);
        this.percentRight.readOnly = true;
        this.left = jsUtils.Utils.domElement('input', `${at.id}_l`, ['form-control', 'input-md', 'text-right']);
        this.left.readOnly = true;
        this.right = jsUtils.Utils.domElement('input', `${at.id}_r`, ['form-control', 'input-md', 'text-right']);
        this.right.readOnly = true;
        this.slider = document.createElement('input');
        this.initialValue = initialValue ? JSON.parse(initialValue).slider: null;

        this.init();
    }

    _setInput(type = null) {
        if (!type) {
            this._setLeft();
            this._setRight();
            this._setPercentLeft();
            this._setPercentRight();
            return;
        }
        switch (type) {
            case 'left':
                this._setLeft();
                break;
            case 'right':
                this._setRight();
                break;
            case 'percentLeft':
                this._setPercentLeft();
                break;
            case 'percentRight':
                this._setPercentRight();
                break;
        }
    }

    _setPercentLeft() {
        this.percentLeft.dataset['code'] = this.percentLeft.id;
        this.percentLeft.imask = IMask(this.percentLeft, {
            mask: Number,
            scale: 0,
            lazy: false,
            thousandsSeparator: ' '
        });
    }

    _setPercentRight() {
        this.percentRight.dataset['code'] = this.percentRight.id;
        this.percentRight.imask = IMask(this.percentRight, {
            mask: Number,
            scale: 0,
            lazy: false,
            thousandsSeparator: ' '
        });
    }

    _setLeft() {
        this.left.dataset['code'] = this.left.id;
        this.left.imask = IMask(this.left, {
            mask: Number,
            scale: 2,
            lazy: false,
            placeholderChar: '_',
            thousandsSeparator: ' ',
            normalizeZeros: true,
            padFractionalZeros: true
        });
    }

    _setRight() {
        this.right.dataset['code'] = this.right.id;
        this.right.imask = IMask(this.right, {
            mask: Number,
            scale: 2,
            lazy: false,
            placeholderChar: '_',
            thousandsSeparator: ' ',
            normalizeZeros: true,
            padFractionalZeros: true
        });
    }

    clear() {
        Input.setValue(this.left, null);
        Input.setValue(this.right, null);
        Input.setValue(this.percentLeft, null);
        Input.setValue(this.percentRight, null);
    }

    update() {
        let referenceValue = parseFloat(Input.getValue(Input.getByCode(this.at.feature.balance.referenceInput)));
        if (Input.isNullValue(referenceValue)) {
            this.clear();
        } else {
            Input.setValue(this.left, referenceValue * (this.at.feature.balance.rightRange - parseInt(this.slider.value)) / 100);
            Input.setValue(this.right, referenceValue * parseInt(this.slider.value) / 100);
            Input.setValue(this.percentLeft, this.at.feature.balance.rightRange - parseInt(this.slider.value));
            Input.setValue(this.percentRight, this.slider.value);
        }
    }

    _setSlider() {
        this.slider.id = this.at.id;
        this.slider.dataset['code'] = this.at.code;
        this.slider.dataset['datatype'] = this.at.attribute.generic_datatype;
        this.slider.dataset['id'] = this.at.id;

        this.slider.setAttribute('type', 'range');
        this.slider.classList.add('balance-control-slider');

        this.slider.setAttribute('min', this.at.feature.balance.leftRange);
        this.slider.setAttribute('max', this.at.feature.balance.rightRange);
        this.slider.setAttribute('step', this.at.feature.balance.step);
        this.slider.value = this.initialValue ? this.initialValue : parseInt(this.at.feature.balance.rightRange / 2);

        this.slider.addEventListener('input', (e) => {
            this.update();
        });

        this.slider.addEventListener('change', (e) => {
            this.update();
        });

        document.addEventListener('documentAttributeEvt:afterAttributesRender', () => {
            this.slider.dispatchEvent(new Event('change'));

            let referenceInput = Input.getByCode(this.at.feature.balance.referenceInput);
            referenceInput.addEventListener('change', () => {
                this.slider.dispatchEvent(new Event('change'));
            });
        });
    }

    _setInputGroup() {
        let e = document.createElement('div');
        e.classList.add('input-group');
        return e;
    }

    _appendInput(container, e, labelText, className) {
        let label = jsUtils.Utils.domElement('label', '', ['read-only']);
        label.innerText = labelText;
        label.setAttribute('for', e.id);

        let inputContainer = jsUtils.Utils.domElement('div', null, ['form-group']);
        inputContainer.classList.add(className);

        inputContainer.appendChild(label);
        inputContainer.appendChild(e);

        container.appendChild(inputContainer);
    }

    render() {
        let container = document.createElement('div');
        container.classList.add('balance-control');

        this._setInput();
        this._setSlider();

        this._appendInput(container, this.percentLeft, '%', 'balance-control-percent-left');
        this._appendInput(container, this.left, this.at.feature.balance.leftName, 'balance-control-left');
        this._appendInput(container, this.right, this.at.feature.balance.rightName, 'balance-control-right');
        this._appendInput(container, this.percentRight, '%', 'balance-control-percent-right');

        container.appendChild(this.slider);
        return container;
    }

    init() {
    }
}

export default BalanceControl;
