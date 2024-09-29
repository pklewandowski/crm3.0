import {SystemException} from "../../../_core/exception";
import {NoteContainer} from "../../../_core/containers/note/js/note";
import {ToolbarUtils} from "../../../_core/utils/toolbar-utils";

const className = 'DocumentNotes';

class DocumentNotes {
    constructor(container, idDocument, columns = 4, blockNewLine = true) {
        if (!container) {
            throw new SystemException(`[${className}] no container provided`);
        }
        if (!idDocument) {
            throw new SystemException(`[${className}] no document id provided`);
        }

        this.container = container;
        this.notesContainer = jsUtils.Utils.domElement('div', null, 'container-notes-container');
        this.idDocument = idDocument;
        this.columns = columns;
        this.notes = [];

        this.addNoteBtn = jsUtils.Utils.domElement('div', null, 'container-notes-addnotebtn');
        let i = jsUtils.Utils.domElement('i', null, ['fa', 'fa-plus-circle']);
        this.addNoteBtn.appendChild(i);

        this.addNoteBtn.addEventListener('click', () => {
            this.create();
        });

        this.container.appendChild(this.addNoteBtn);
        this.container.appendChild(this.notesContainer);

        this.container.classList.add('container-notes');


        document.addEventListener('click', () => {
            for (let i of this.notes) {
                i.setEditable(false);
            }
        });

        //prevent 'enter' key
        if (blockNewLine) {
            this.notesContainer.addEventListener('keypress', (evt) => {
                if (evt.target.classList.contains('container-note-body') && evt.key === 'Enter') {
                    evt.preventDefault();
                }
            });
        }


        this.notesContainer.addEventListener('dblclick', (evt) => {
            evt.stopPropagation();

            for (let i of this.notes) {
                i.setEditable(false);
            }

            if (evt.target.classList.contains('container-note-body')) {
                let note = this.findNote(this.getNoteId(evt.target));
                note.setEditable();
                note.noteBody.focus();
            }
        });

        document.addEventListener('blur', (evt) => {
            if (evt.target?.classList?.contains('container-note-body')) {
                let note = this.findNote(this.getNoteId(evt.target));
                this.update(note.id);
                note.setEditable(false);
            }
        }, true);

        this.notesContainer.addEventListener('click', (evt) => {
            evt.stopPropagation();
            if (evt.target.classList.contains('note-toolbar-button-delete')) {
                this.delete(this.findNote(this.getNoteId(evt.target)));
                return;
            }

            if (evt.target.classList.contains('note-toolbar-button-save')) {
                let note = this.findNote(this.getNoteId(evt.target));
                this.update(note.id);
                note.setEditable(false);
            }
        });
    }

    getNoteId(el) {
        let id = el.closest('.container-note-container').dataset['id'];
        if (!id) {
            throw new SystemException(`[${className}]:getNote: No note id found`);
        }
        return id;
    }

    findNote(id) {
        for (let i of this.notes) {
            if (i.id == id) {
                return i;
            }
        }
        return null;
    }

    reset() {
        this.notesContainer.innerHTML = null;
    }

    _addButton(note, buttonTypes) {
        for (let buttonType of buttonTypes) {
            let tbContainer = jsUtils.Utils.domElement('div', null, 'container-note-toolbar-button-container');
            let btn;

            switch (buttonType) {

                case 'delete':
                    btn = ToolbarUtils.deleteBtn();
                    btn.addEventListener('click', () => {
                        this.delete(note.id)
                    });
                    tbContainer.appendChild(btn);
                    tbContainer.classList.add('note-toolbar-button-delete');
                    note.toolbar.appendChild(tbContainer);
                    break;

                case 'update':
                    btn = ToolbarUtils.saveBtn();
                    btn.addEventListener('click', () => {
                        this.update(note.id)
                    });
                    tbContainer.appendChild(btn);
                    tbContainer.classList.add('note-toolbar-button-save');
                    note.toolbar.appendChild(tbContainer);
                    break;
            }
        }
    }

    _renderNote(note, prepend = false) {
        let noteContainer = jsUtils.Utils.domElement('div', null, ['document-notes-note-container']);
        noteContainer.appendChild(note.container);
        if (prepend) {
            this.notesContainer.prepend(noteContainer);
            return;
        }
        this.notesContainer.appendChild(noteContainer);
    }

    render() {
        this.reset();
        for (let i of this.notes) {
            this._renderNote(i);
        }
    }


    /**
     * _addNote
     * function adds new note object to the notes array
     * @param data
     * @returns {NoteContainer}
     * @private
     */
    _addNote(data) {
        let note = new NoteContainer(`${data.update_date}`, data.text, data.id);
        this._addButton(note, ['update', 'delete']);
        this.notes.push(note);
        return note;
    }

    /**
     * get
     * function gets all notes for document form database and render it into layout
     */
    get() {
        ajaxCall({
            method: 'get',
            url: _g.document.urls.noteUrl, data: {idDocument: this.idDocument}
        }).then((data) => {
            this.notes = [];
            for (let i of data) {
                this._addNote(i);
            }
            this.render(data);
        }, (error) => {
            throw new SystemException(error);
        })
    }

    /**
     * create
     * function creates new note, adds it to notes array and render as first in queue.
     * @param text - note text
     */
    create(text = null) {
        for (let i of this.notes) {
            if (!i.bodyText) {
                Alert.info('Istnieje już pusta notatka. Wypełnij ją.');
                return;
            }
        }
        ajaxCall({
            method: 'post',
            url: _g.document.urls.noteUrl, data: {idDocument: this.idDocument, text: text}
        }).then((data) => {
            this._renderNote(this._addNote(data), true);

        }, (result) => {
            throw new SystemException(result);
        });
    }


    update(id) {
        let note = this.findNote(id);
        if (!note) {
            throw new SystemException(`Nie znaleziono notaki o ID: ${id}`);
        }
        let text = note.getText();
        if (!text) {
            Alert.warning('Notatka musi posiadać tekst');
            note.update(note.headerText, note.bodyText);
            return;
        }
        ajaxCall({
            method: 'put',
            url: _g.document.urls.noteUrl, data: {id: id, text: text}
        }).then(() => {
            note.update(note.headerText, text);

        }, (result) => {
            throw new SystemException(result);
        })
    }

    delete(note) {
        if (!note) {
            throw new SystemException('Nie znaleziono notatki po ID. Zgłoś problem do administratora systemu.');
        }
        Alert.questionWarning('Czy na pewno usunąć notatkę?', 'Usunięcie spowoduje bezpowrotną utratę notatki', () => {
            ajaxCall({
                method: 'delete',
                url: _g.document.urls.noteUrl, data: {id: note.id}
            }).then(() => {
                let index = this.notes.indexOf(note);
                if (index > -1) {
                    note.container.closest('.document-notes-note-container').remove();
                    this.notes.splice(index, 1);
                }

            }, (result) => {
                throw new SystemException(result);
            })
        });
    }
}

export {DocumentNotes};