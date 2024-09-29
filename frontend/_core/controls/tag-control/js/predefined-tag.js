import {TagControlUtils} from "./tag-control-utils";
import {SystemException} from "../../../exception";

class PredefinedTag {
    constructor(tagControl) {
        this.predefinedTagList = null; // todo: add predefined tags to list
        this.predefinedTagContainer = null;
        this.tagControl = tagControl;
    }

    _togglePredefinedTagChecked(e) {
        if (e.classList.contains('tag-item-checked')) {
            e.classList.remove('tag-item-checked');
            return false;
        }
        e.classList.add('tag-item-checked');
        return true;
    }

    getPredefinedTagList() {
        return ajaxCall({
                method: 'get',
                url: _g.user.urls.predefinedTagListUrl
            },
            (resp) => {
                this.predefinedTagList = resp;
            },
            (resp) => {
                jsUtils.LogUtils.log(resp.responseJSON.errmsg, true);
            })
    }

    renderPredefinedTags(initial = false) {
        if (!this.predefinedTagContainer) {
            this.predefinedTagContainer = document.getElementById('predefinedTagContainer');
            if(!this.predefinedTagContainer) {
                throw new SystemException('Brak kontenera dla tagów predefiniowanych');
            }

            this.predefinedTagContainer.addEventListener('click', (e) => {
                let el = e.target;
                let tagName = el.innerText;
                if (el.classList.contains('tag-item')) {
                    if (this._togglePredefinedTagChecked(el)) {
                        TagControlUtils.addTagElement(tagName, this.tagControl.tags);
                    } else {
                        if (this.tagControl.tags.indexOf(tagName) !== -1) {
                            this.tagControl.tags.splice(this.tagControl.tags.indexOf(tagName), 1);
                        }
                    }
                    this.tagControl.renderTags();
                }
            });
        }
        this.predefinedTagContainer.innerHTML = null;

        if (this.predefinedTagList) {
            for (let i of this.predefinedTagList) {
                let checked = false;
                if (this.tagControl.tags.indexOf(i) !== -1) {
                    checked = true
                }
                this.predefinedTagContainer.appendChild(TagControlUtils.renderTagItem(i, checked));
            }
        }
    }

    init() {
    }
}

export {PredefinedTag};