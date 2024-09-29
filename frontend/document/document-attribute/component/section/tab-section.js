import HtmlUtils from "../../../../_core/utils/html-utils";
import Section from "./section";

class TabSection {
    static _getId(id, rIdx) {
        return `${id}${rIdx != null ? '__' + rIdx + '__' : ''}-tab`
    }

    static renderTabSectionHeader(at, rIdx) {
        let ul = document.createElement('ul');
        ul.classList.add(...['nav', 'nav-tabs']);
        at.children.map((e, idx) => {
            let li = document.createElement('li');
            if (!idx) {
                li.classList.add('active');
            }
            li.classList.add('nav-item');
            let a = document.createElement('a');
            a.classList.add("nav-link");
            a.dataset['toggle'] = 'tab';
            a.href = `#${TabSection._getId(e.id, rIdx)}`;
            a.innerHTML = HtmlUtils.escapeScriptTag(e.name);
            li.appendChild(a);
            ul.appendChild(li);
        });
        return ul;
    }

    static renderTabSection(at, ver = null, rIdx) {
        let cnt = document.createElement('div');
        cnt.classList.add('col-lg-12');

        let cl = Section.renderSection(at);
        cnt.appendChild(TabSection.renderTabSectionHeader(at, rIdx));
        cl.appendChild(cnt);

        let bd = document.createElement('div');
        bd.classList.add(...['tab-content', 'pad-t']);
        cnt.appendChild(bd);

        if (at.css_class) {
            cl.classList.add(at.css_class);
        }

        if (at.feature && at.feature.style) {
            cl.style.cssText = at.feature.style;
        }

        return {tabSection: cl, tabContent: bd};
    }

    static renderTabPane(at, isActive, ver = null, rIdx) {
        let pane = document.createElement('div');
        pane.classList.add(...['tab-pane', 'fade', 'in']);
        if (isActive) {
            pane.classList.add('active');
        }
        pane.id = TabSection._getId(at.id, rIdx);

        if (at.css_class) {
            pane.classList.add(at.css_class);
        }

        if (at.feature && at.feature.style) {
            pane.style.cssText = at.feature.style;
        }

        return pane;
    }
}

export default TabSection;