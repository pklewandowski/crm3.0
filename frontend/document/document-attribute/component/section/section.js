import Component from "../component";
import HtmlUtils from "../../../../_core/utils/html-utils";

class Section {

    static setLabelItemContainer(sectionLabelContainer) {
        let ul = document.getElementById('labelItemContainer');
        if (!ul) {
            ul = document.createElement('ul');
            ul.id = 'labelItemContainer';
            sectionLabelContainer.appendChild(ul);
        }
        return ul;
    }

    static setActive(sectionId) {
        Array.from(document.querySelectorAll(`#documentSectionLabelContainer li`)).forEach(e => {
            if (e.dataset['id'] == sectionId) {
                e.classList.add(...['item-active', 'section-label-active']);
            } else {
                e.classList.remove(...['section-label-active', 'item-active']);
            }
        });

        Array.from(document.getElementsByClassName('section-container')).forEach(e => {
            if (e.dataset['id'] == sectionId) {
                e.classList.remove('section-inactive');
            } else {
                e.classList.add('section-inactive');
            }
        })
    }

    static renderLabel(section, active, callback) {
        let li = document.createElement('li');
        li.dataset['id'] = section.id;
        li.dataset['type'] = ''; //section.view_type;
        li.innerHTML = `<div class="section-label-text">${section.name}</div></li>`;

        if (active) {
            li.classList.add(...['item-active', 'section-label-active']);
        }

        li.addEventListener('click', () => Section.setActive(section.id));

        if (callback && callback.fn && typeof callback.fn === 'function') {
            callback.fn(li, callback.opt);
        }

        return li;
    }

    static renderMainSection(scModel, isActive) {
        let sc = document.createElement('div');
        sc.id = `section_${scModel.id}`;
        sc.dataset['id'] = scModel.id;
        sc.classList.add(...['row', 'section-container']);
        if (!isActive) {
            sc.classList.add('section-inactive');
        }
        sc.style.cssText = "height: 100%, overflow: auto, display:block";

        return sc;
    }

    static renderSection(at) {
        let cl = document.createElement('div');
        cl.id = at.id;
        if (at.name) {
            let panel = document.createElement('div');
            panel.classList.add('heading-title');
            panel.innerHTML = HtmlUtils.escapeScriptTag(at.name);
            cl.appendChild(panel);
        }

        cl.classList.add(...['row', 'subsection-container']);
        if (at.css_class) {
            cl.classList.add(at.css_class);
        }

        if (at.feature && at.feature.style) {
            cl.style.cssText = at.feature.style;
        }

        return cl;
    }
}

export default Section;