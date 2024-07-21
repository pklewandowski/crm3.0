import StringUtils from "../../../utils/string-utils";
import {panel, panelBody, panelHeading} from "./panel-dom";
import {SystemException} from "../../../exception";

const className = 'Panel';

class Panel {
    /**
     *
     * @param title
     * @param existContainer - if specified, then it means that the panel exists and we want to reverse html to panel object
     */
    constructor(title = '', existContainer = null) {
        this.title = StringUtils.toProperTitleCase(title);
        this.container = null;

        if(existContainer) {
            this.container = jsUtils.Utils.setContainer(existContainer, this.constructor.name);
            this.panel = this.container.querySelector('.panel');
            if (!this.panel) {
                throw new SystemException(`${this.constructor.name}: Couldn't find .panel class object`);
            }
            this.panelHeading = this.panel.querySelector('.panel-heading');

            if (!this.panelHeading) {
                throw new SystemException(`${this.constructor.name}: Couldn't find .panel-heading class object`);
            }

            this.panelBody = this.panel.querySelector('.panel-body');

            if (!this.panelBody) {
                throw new SystemException(`${this.constructor.name}: Couldn't find .panel-body class object`);
            }
        } else {

            this.panel = panel();
            this.panelHeading = panelHeading();
            this.panelBody = panelBody();

            this.panelHeading.innerText = this.title;
            this.panel.appendChild(this.panelHeading);
            this.panel.appendChild(this.panelBody);
        }
    }

    addClass(classList, body = false) {
        if (body) {
            this.panelBody.classList.add(...classList);
        } else {
            this.panel.classList.add(...classList);
        }
    }

    setTitle(title) {
        this.panelHeading.innerText = StringUtils.toProperTitleCase(title);
    }
}

export {Panel};