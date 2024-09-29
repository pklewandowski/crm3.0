import Input from "../../../input";
import {Modal} from "../../../modal/modal";
import Alert from "../../../alert";
import {SystemException} from "../../../exception";

const TAG_SEPARATOR = ',';
class TagControlUtils {

    static addTagElement(val, tags) {
        let _val = val.toLowerCase().trim();
        if (Input.isNullValue(_val) || tags.includes(_val)) {
            return;
        }
        tags.push(_val);
    }

    static addTag(tagInput, tags, callback) {
        let val = tagInput.value;

        if (Input.isNullValue(val)) {
            return;
        }
        val = val.split(TAG_SEPARATOR);

        for (let i of val) {
            TagControlUtils.addTagElement(i, tags);
        }
        tagInput.value = null;
        if(typeof callback === 'function') {
            callback();
        }
    }

    static deleteTag(item, tags, callback){
        Alert.questionWarning('Czy na pewno usunąć tag?', 'Tag zostanie usunięty po zapisaniu zmian', (el) => {
            let idx = tags.findIndex(element => element === el.innerText);
            if (idx === -1) {
                throw new SystemException('Niespójność zawartości tagów');
            }
            tags.splice(idx, 1);
            if(typeof callback === 'function') {
                callback();
            }
        }, item);
    }

    static renderTagItem(text, checked = false) {
        let tagItem = jsUtils.Utils.domElement('div', '', 'tag-item');
        if (checked) {
            tagItem.classList.add('tag-item-checked');
        }
        tagItem.innerText = text;
        return tagItem;
    }

    static renderModal(callback, tags) {
        let modal = Modal.getTemplate('addTagModal', 'Nowy Tag');
        document.querySelector('body').appendChild(modal);
        //add modal body
        let modalBody = modal.querySelector('.modal-body');
        modalBody.innerHTML =
            `<div class="row">
                  <div class="col-lg-12">
                      <div class="form-group">
                          <label>Tagi predefiniowane</label>
                          <div id="predefinedTagContainer" class="tag-container"></div>
                      </div>
                  </div>
            </div>
            <div class="row">
                 <div class="col-lg-12">
                     <div class="form-group">
                         <label>Wprowadź własne tagi rozdzielając je znakiem przecinka</label>
                         <input class="form-control input-md tag-input" type="text"/>
                      </div>
                 </div>
             </div>`;

        let saveBtn = modal.querySelector('.saveBtn');
        saveBtn.innerText = 'Dodaj';
        saveBtn.setAttribute('disabled', 'disabled');

        let tagInput = modalBody.querySelector(".tag-input");
        tagInput.addEventListener('keyup', () => {
            if (Input.isNullValue(tagInput.value)) {
                saveBtn.setAttribute('disabled', 'disabled');
                return;
            }
            saveBtn.removeAttribute('disabled');
        });

        saveBtn.addEventListener('click', () => {
            TagControlUtils.addTag(tagInput, tags, callback);
        });

        return modal;
    }
}

export {TagControlUtils, TAG_SEPARATOR};