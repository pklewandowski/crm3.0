import '../scss/tag-control';

import {ToolbarUtils} from "../../../utils/toolbar-utils";
import {Modal} from "../../../modal/modal";
import Alert from "../../../alert";
import Input from "../../../input";
import {SystemException} from "../../../exception";
import {PredefinedTag} from "./predefined-tag";
import {TAG_SEPARATOR, TagControlUtils} from "./tag-control-utils";

const className = 'TagControl';

class TagControl {
    constructor(container, tagFormField) {

        this.container = container;
        this.tagContainer = null;
        this.tagModal = null;
        this.tagFormField = tagFormField;
        this.tags = [];
        this.predefinedTag = new PredefinedTag(this);

        this.init();
    }

    renderTags() {
        for (let i of Array.from(this.tagContainer.querySelectorAll('.tag-item'))) {
            i.remove();
        }

        for (let i of this.tags) {
            this.tagContainer.appendChild(TagControlUtils.renderTagItem(i));
        }

        if (this.tagFormField) {
            this.tagFormField.value = this.tags.join(',');
        }
    }

    showTagModal() {
        if (!this.predefinedTag.predefinedTagContainer) {
            this.predefinedTag.predefinedTagContainer = document.getElementById('predefinedTagContainer');
            this.predefinedTag.getPredefinedTagList().then(() => {
                this.predefinedTag.renderPredefinedTags();
            });
        }
        $(this.tagModal).modal();
    }

    render() {
        let formGroup = jsUtils.Utils.domElement('div', '', 'form-group');
        let label = jsUtils.Utils.domElement('label');
        label.innerText = 'Tagi';
        formGroup.appendChild(label);

        this.tagContainer = jsUtils.Utils.domElement('div', '', ['tag-container']);

        let tagToolbar = jsUtils.Utils.domElement('div', '', ['control-toolbar', 'tag-toolbar']);
        let addBtn = ToolbarUtils.addBtn();
        tagToolbar.appendChild(addBtn);
        this.tagContainer.appendChild(tagToolbar);

        addBtn.addEventListener('click', () => {
            if (!this.predefinedTag.predefinedTagList) {
                this.predefinedTag.getPredefinedTagList().then(() => {
                    this.predefinedTag.renderPredefinedTags();
                    this.showTagModal();
                })
            } else {
                this.predefinedTag.renderPredefinedTags();
                this.showTagModal();
            }
        });

        formGroup.appendChild(this.tagContainer);
        this.container.appendChild(formGroup);

    }

    setData() {
        if (!Input.isNullValue(this.tagFormField?.value)) {
            this.tags = this.tagFormField.value.split(TAG_SEPARATOR);
        }
    }


    handleTagClick(e) {
        let item = e.target;
        if (item.classList.contains('tag-item')) {
            TagControlUtils.deleteTag(item, this.tags, () => {
                this.renderTags();
            });
        }
    }

    init() {
        this.render();
        this.setData();
        if (this.tags.length) {
            this.renderTags();
        }
        this.tagModal = TagControlUtils.renderModal(() => {
            this.renderTags();
        }, this.tags);
        this.tagContainer.addEventListener('click', (e) => {
            this.handleTagClick(e);
        })
    }
}

export {TagControl};