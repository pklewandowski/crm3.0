import FieldRenderer from "../../../js/document-field-renderer";
import {SystemException} from "../../../../_core/exception";
import {TOOLBAR_BTN, ToolbarUtils} from "../../../../_core/utils/toolbar-utils";
import DocumentAttributeModel from "../../model/document-attribute-model";

const className = 'Combo';

class Combo {
    static getContent(cl, at) {
        let content = '';

        if (at?.children[0]?.is_section) {
            content = 'Kliknij aby rozwinąć dane...';
        } else {

            for (let i of Array.from(cl.container.querySelectorAll('input, select, textarea'))) {
                content += `<span class="combo-field-item" data-toggle="tooltip" title="${DocumentAttributeModel.findAttributeByCode(i.dataset['code'], at.children).name}">`;
                if (i.dataset['name_icon']) {
                    content += `<i class="${i.dataset['name_icon'].replace(/,/g, ' ')}"></i>${Input.isNullValue(i.value) ? '' : i.value}`;
                } else
                    content += ` | ${i.dataset['name_short']}: ${Input.isNullValue(i.value) ? '' : i.value}`;

                content += '</span>';
            }
        }
        cl.content.innerHTML = content;
    }

    static render(at, callback = null, opt = null) {

        let clContainer = jsUtils.Utils.domElement('div', null, 'form-group');

        let cl = jsUtils.Utils.domElement('div');
        let cmb = jsUtils.Utils.domElement('div');

        clContainer.appendChild(FieldRenderer.renderLabel(at, at.name, false));
        clContainer.appendChild(cl);

        cl.id = at.id;
        cl.dataset['code'] = at.code;

        cmb.style.position = 'absolute';
        cmb.style.display = 'none';
        cmb.classList.add(...['combo-container', 'dropdown-layer']);

        if (at?.feature?.width) {
            cmb.style.width = at.feature.width;
        }

        let closeBtn = ToolbarUtils.closeBtn(TOOLBAR_BTN.sm);
        closeBtn.classList.add('combo-close-btn');
        closeBtn.addEventListener('click', () => {
            cmb.style.display = "none";
        });
        cmb.appendChild(closeBtn);

        document.body.appendChild(cmb);

        cl.classList.add(...['form-control', 'input-md', 'combo-content']);
        cl.addEventListener('click', (e) => {
            let pos = jsUtils.Utils.position(cl);
            if (!pos) {
                throw new SystemException(`[${className}][render]:Nie udało się określić pozycji elementu`);
            }

            if (at.feature?.width) {
                // TODO: drut - get the actual width of side bar not absolut value of 130
                cmb.style.width = Math.min(at.feature.width, window.innerWidth - 130) + "px";
            } else {
                cmb.style.width = `${parseInt(pos.width) + 15}px`;
            }

            if (at?.feature?.center) {
                // TODO: drut - get the actual width of side bar not absolut value of 130
                pos.left = (window.innerWidth - Math.min((at.feature?.width ? at.feature?.width: pos.width), window.innerWidth - 130)) / 2;
            }
            else if (at?.feature?.left) {
                pos.left = at.feature.left;
            }

            else if (at?.feature?.right) {
                pos.right = at.feature.right;
            }


            cmb.style.top = `${parseInt(pos.top) - 15}px`;
            cmb.style.left = `${parseInt(pos.left) - 15}px`;
            cmb.style.display = 'block';

        });

        if (callback && callback.fn && typeof callback.fn === 'function') {
            callback.fn(cl, callback.opt);
        }
        return {clContainer: clContainer, content: cl, container: cmb};
    }
}

export default Combo;