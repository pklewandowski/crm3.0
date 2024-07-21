import {QuickMenuRing} from "./quick-menu-ring";
import '../scss/quick-menu.scss';
import {TOOLBAR_BTN, ToolbarUtils} from "../../../_core/utils/toolbar-utils";

const QUICK_MENU_DEFAULT_SIZE = 400;

class QuickMenu {
    constructor(size = null, ring = false) {
        let container = document.getElementById('quickMenuContainer');
        if (container) {
            this.container = container;

        } else {
            this.container = jsUtils.Utils.domElement('div', 'quickMenuContainer', 'widget-quick-menu-container');
            document.body.appendChild(this.container);
        }
        this.size = size ? size : QUICK_MENU_DEFAULT_SIZE;

        this.container.style.width = `${this.size}px`;
        this.container.style.height = `${this.size}px`;

        if (ring) {
            this.ring = new QuickMenuRing().ring;
        } else {
            this.ring = null;
        }

        this.items = [];

        this.pos = null;
        this.mousedown = false;

        $(this.container).draggable({
            // containment: "parent", - todo: firefox get stupid when it's set. Subject to bypass / fix it
            classes: {'ui-draggable-dragging': 'widget-quick-menu-container-drag'}
        });
    }

    addItem(name, iconClass, url, bgColor = null, color = null) {
        this.items.push({name: name, iconClass: iconClass, url: url, color: color, bgColor: bgColor});
    }

    _addCloseBtn() {
        let btnContainer = jsUtils.Utils.domElement('div', '', 'widget-quick-menu-close-button');
        btnContainer.appendChild(ToolbarUtils.closeBtn(TOOLBAR_BTN.sm));
        btnContainer.addEventListener('click', () => {
            this._hide();
            sessionStorage.setItem('qmDisplay', 'none');
        });

        this.container.appendChild(btnContainer);
    }

    _hide() {
        this.container.style.display = 'none';
    }

    deleteItem(idx) {
    }

    _renderItem(name, iconClass = [], url, color = null, bgColor = null) {
        let a = jsUtils.Utils.domElement('a', '', 'widget-quick-menu-button');
        a.href = url;
        if (color) {
            a.style.color = color;
        }
        if (bgColor) {
            a.style.backgroundColor = bgColor;
        }

        let div = jsUtils.Utils.domElement('div', '');
        div.classList.add('widget-quick-menu-button-content');
        let i = jsUtils.Utils.domElement('i', '', iconClass);
        let title = jsUtils.Utils.domElement('div', '', 'widget-quick-menu-text');

        let titleText = jsUtils.Utils.domElement('span');
        titleText.innerText = name;

        a.appendChild(div);
        div.appendChild(i);
        div.appendChild(title);
        title.appendChild(titleText);

        return a;
    }

    reset() {
        this.container.innerHTML = null;
    }

    render() {
        let angle = 0;
        this.reset();

        if (this.ring) {
            this.container.appendChild(this.ring);
        }

        let pos = jsUtils.Utils.position(this.container);
        let tileRadius = 120 / 2; // todo: DRUT!!! zrobić klasę QuickMenuItem i przenieść kod tam
        let ringWidth = 25;
        let containerRadius = pos.height / 2 - ringWidth / 2;


        for (let i of this.items) {
            let item = this._renderItem(i.name, i.iconClass, i.url, i.color, i.bgColor);
            this.container.appendChild(item);

            let top = pos.height / 2 - tileRadius - Math.round((containerRadius) * Math.cos(angle));
            let left = pos.width / 2 - tileRadius - 5 + Math.round((containerRadius) * Math.sin(angle));

            item.style.top = `${top}px`;
            item.style.left = `${left}px`;
            angle += 2 * Math.PI / this.items.length;
        }

        this._addCloseBtn();

        let qmDisplay = sessionStorage.getItem('qmDisplay');
        if (!qmDisplay) {
            sessionStorage.setItem('qmDisplay', 'block');
            qmDisplay = 'block';
        }

        this.container.style.display = qmDisplay;

    }
}

export {QuickMenu};