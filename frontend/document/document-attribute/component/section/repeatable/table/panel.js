import {SectionTable} from "./sectionTable";
import {Toolbar} from "./toolbar";

class Panel {
    constructor(section) {
        this.section = section;

        this.item = jsUtils.Utils.domElement('div', '', ['panel', 'panel-default']);
        this.item.style.position = 'relative';
        this.panelBody = jsUtils.Utils.domElement('div', '', 'panel-body');
        this.container = jsUtils.Utils.domElement('div', `${this.section.at.id}-tab`, 'repeatable-section-container');

        this.toolbar = new Toolbar(section);
        this.table = new SectionTable(section);

        this.item.appendChild(this.toolbar.item);
        this.item.appendChild(this.panelBody);

        this.panelBody.appendChild(this.container);
        this.container.appendChild(this.table.item);
        this._render();
    }

    _render() {
        if(window.documentDefinitionMode) {
            return;
        }
        if (this.section?.at?.feature?.container?.style) {
            this.container.style.cssText = this.section.at.feature.container.style;
        }

        if (this.section.at.css_class) {
            this.section.cl.classList.add(this.section.at.css_class);
        }

        if (this.section.at.selector_class) {
            this.section.cl.classList.add(this.section.at.selector_class);
            this.section.cl.dataset['selector'] = this.section.at.selector_class;
        }

        if (this.section?.at?.feature?.style) {
            this.section.cl.style.cssText = this.section.at.feature.style;
        }
    }
}
export {Panel};