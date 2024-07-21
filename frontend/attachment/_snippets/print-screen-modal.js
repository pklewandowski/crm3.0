import ajaxCall from "../../_core/ajax";
import Tile from "../tile/tile";
import ClipboardImage from "../../_core/clipboard/clipboard-image";

class PrintScreenModal {
    constructor(modalContainerId, attachment) {
        this.attachment = attachment;
        this.modalContainerId = modalContainerId ? modalContainerId : 'paste_screen_modal';
        this.modalContainer = document.getElementById(modalContainerId);
        this.pasteCanvas = this.modalContainer.getElementsByClassName('paste-canvas')[0];

        this.init();
    }

    _save(evt) {
        ajaxCall({
                method: 'post',
                url: _g.document.urls.upload_attachment_url,
                data: {
                    parent: this.attachment.getParent(),
                    documentId: _g.document.id,
                    createAttachment: true,
                    image_data: this.pasteCanvas.toDataURL('image/jpeg'),
                }
            },
            resp => {
                this.attachment._handleAttachment(resp.saved_files[0]);
                // this.attachment.attachmentContainer.appendChild(Tile.render(resp.saved_files[0], _g.document.id));
            },
            resp => {
                Alert.error('Błąd', resp.responseJSON.errmsg);
            })
    }

    render() {
        this.pasteCanvas.getContext("2d").clearRect(0, 0, this.pasteCanvas.width, this.pasteCanvas.height);
        this.pasteCanvas.width = 300;
        this.pasteCanvas.height = 300;
        $(this.modalContainer).modal();
    }

    init() {
        this.modalContainer.getElementsByClassName('add-printscreen-btn')[0].addEventListener('click', (evt) => {
            this._save(evt);
        });new ClipboardImage(this.pasteCanvas, true);

    }
}

export default PrintScreenModal;