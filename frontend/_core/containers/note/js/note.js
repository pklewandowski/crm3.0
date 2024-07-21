
import HtmlUtils from "../../../utils/html-utils";

import '../scss/note.scss';

class NoteContainer {
    constructor(headerText, bodyText, id = null, buttons = null) {
        this.headerText = HtmlUtils.escapeScriptTag(headerText);
        this.bodyText = HtmlUtils.escapeScriptTag(bodyText);
        this.id = id;
        this.buttons = buttons;
        this.container = jsUtils.Utils.domElement('div', null, 'container-note-container');
        this.toolbar = jsUtils.Utils.domElement('div', null, 'container-note-toolbar');
        this.noteBodyContent = jsUtils.Utils.domElement('div', null, 'container-note-body-content');
        this.noteHeader = jsUtils.Utils.domElement('div', null, 'container-note-header', null, null, this.headerText);
        this.noteBody = jsUtils.Utils.domElement('div', null, 'container-note-body', null, null, this.bodyText);
        this.editable = false;
        // this.noteBody.setAttribute('tabindex', 0);

        this.container.dataset['id'] = this.id;
        this.container.appendChild(this.toolbar);
        this.container.appendChild(this.noteHeader);
        this.noteBodyContent.appendChild(this.noteBody);
        this.container.appendChild(this.noteBodyContent);

        this.noteBody.dataset['text'] = 'Kliknij dwukrotnie aby dodać tekst...';

        if (buttons) {
            for (let i of buttons) {
                this._addButton(i);
            }
        }
    }

    setEditable(editable = true) {
        if (editable) {
            this.noteBody.setAttribute('contenteditable', true);
            this.noteBody.classList.add('container-note-body-editable');
            this.editable = true;
        } else {
            this.noteBody.removeAttribute('contenteditable');
            this.noteBody.classList.remove('container-note-body-editable');
            this.editable = false;
        }
    }


    updateHeaderText(text, update = true) {
        this.headerText = text;
        if (update) {
            this._update();
        }
    }

    updateBodyText(text, update = true) {
        this.bodyText = HtmlUtils.escapeScriptTag(text);
        if (update) {
            this._update();
        }
    }

    _update() {
        this.noteHeader.innerHTML = this.headerText;
        this.noteBody.innerHTML = this.bodyText;
    }

    reset() {
        this.noteHeader.innerText = null;
        this.noteBody.innerText = null;
    }

    update(headerText, bodyText) {
        if (headerText) {
            this.updateHeaderText(headerText, false);
        }
        if (bodyText) {
            this.updateBodyText(bodyText, false);
        }
        this._update();
    }


    getText() {
        return this.noteBody.innerHTML;
    }
}

export {NoteContainer}