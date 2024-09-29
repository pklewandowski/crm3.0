import {DateUtils} from "../../_core/utils/date-utils";
import {SystemException} from "../../_core/exception";
import {addNoteModal} from "./add-note-modal";
import "../scss/note.scss";

class Note {
    constructor(id, url, container) {
        this.id = id;
        this.url = url;
        this.container = container;
        this.noteItemsContainer = this.container.querySelector('.note-items-container');
        this.notes = [];
        this.addNoteBtn = this.container.querySelector('.add-note-btn');

        this.modal = document.getElementById('addNoteModal');

        if (!this.modal) {
            this.modal = jsUtils.Utils.domElement('div', 'addNoteModal', ['modal', 'fade']);
            this.modal.tabIndex = -1;
            this.modal.role = "dialog";
            this.modal.innerHTML = addNoteModal;

            document.body.appendChild(this.modal);
            document.getElementById('saveNoteBtn').addEventListener('click', () => {
                this.add();
            });
        }

        this.addNoteBtn.addEventListener('click', () => {
            this.showAddNoteModal();
        })
    }

    setNotes(notes) {
        this.notes = notes;
        return this;
    }

    showAddNoteModal() {
        this.modal.querySelector('.note-text textarea').value = null;
        $(this.modal).modal({backdrop: 'static', keyboard: false});
    }

    add() {
        ajaxCall({
            method: 'post',
            url: this.url,
            data: {id: this.id, text: this.modal.querySelector('.note-text textarea').value}
        }).then(note => {
                if(!this.notes.length) {
                    this.reset();
                }
                this.notes.push(note);
                this.noteItemsContainer.prepend(this._renderNote(note));
            },
            resp => {
                throw new SystemException(resp);
            });
    }

    reset() {
        if (!this.noteItemsContainer) {
            return;
        }
        this.noteItemsContainer.innerHTML = null;
    }

    getData(force = false, render = false) {
        if (!force && this.notes.length) {
            return;
        }
        ajaxCall({
            method: 'get',
            url: this.url
        }).then(notes => {
                this.notes = notes;
                if (render) {
                    this.render();
                }
            },
            resp => {
                throw new SystemException(resp);
            });
    }

    _renderNote(note) {
        let noteHeader = DateUtils.formatDate(note.creation_date, true);

        let noteContainer = jsUtils.Utils.domElement('div', null, 'note-container');
        let noteHeaderContainer = jsUtils.Utils.domElement('div', null, 'note-header', null, null, null, noteHeader);
        let noteBodyContainer = jsUtils.Utils.domElement('div', null, 'note-body', null, null, null, note.text);
        noteContainer.appendChild(noteHeaderContainer);
        noteContainer.appendChild(noteBodyContainer);

        return noteContainer
    }

    render() {
        this.reset();
        if (this.notes.length) {
            for (let i of this.notes) {
                this.noteItemsContainer.appendChild(this._renderNote(i));
            }
            return;
        }
        let noNotes = jsUtils.Utils.domElement(
            'div',
            null,
            'note-container-no-notes',
            null,
            null,
            '<span class="note-no-notes-header">W tej chwili nie ma notatek</span>.<br/>' +
            '<span class="note-no-notes-description">Dodaj nową notatkę klikając w ikonę ' +
            '<span class="add-note-btn"><i class="fa fa-plus-circle"></i></span></span>'
        );
        let iDiv = jsUtils.Utils.domElement('div', null, 'note-no-notes-icon');
        iDiv.appendChild(jsUtils.Utils.domElement('i', null, ['far', 'fa-comment-dots']));
        noNotes.appendChild(iDiv);

        this.noteItemsContainer.appendChild(noNotes);
    }
}

export {Note};