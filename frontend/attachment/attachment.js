import AttachmentTree from "./tree/attachment-tree";
import Tile from "./tile/tile";
import AttachmentHeading from "./_snippets/heading/attachment-heading";
import MyDropzone from "./basic-attachment-dropzone";
import ajaxCall from "../_core/ajax";
import PrintScreenModal from "./_snippets/print-screen-modal";

const className = 'Attachment';

class Attachment {

    constructor(documentId, containerId) {
        // containers
        this.documentId = documentId;
        this.container = document.getElementById(containerId);
        this.attachmentHeading = new AttachmentHeading();
        this.attachmentPanel = this._renderAttachmentContainer();
        this.attachmentContainer = this.attachmentPanel.querySelector('.panel-body');
        // chlidren objects
        this.tree = new AttachmentTree(this._renderTreeContainer(this.container));

        this.dropzone = null;
        this.rootNodeId = '__root__';
        this.attachments = {}; // {'__root__':[]};

        this.uploadAttachmentUrl = _g.document.urls.upload_attachment_url;

        this.printScreenModal = new PrintScreenModal('paste_screen_modal', this);

        this.container.addEventListener('directoryTree.selectedNode', (e) => {
            if (!['directory', 'root'].includes(e.detail.node.data.type)) {
                return;
            }
            this.render(e.detail.node.id);
        });

        this.addCallback = null;

        this.removeCallback = (data) => {
            let atmElement = null;
            let atmIdx = -1;
            let parent = data.parent ? data.parent : this.rootNodeId;
            for (const [idx, el] of this.attachments[parent].entries()) {
                if (el.id === data.id) {
                    atmElement = el;
                    atmIdx = idx;
                    break;
                }
            }
            if (atmIdx !== -1) {
                this.attachments[parent].splice(atmIdx, 1);
            }
        };

        this.init();
    }

    _renderAttachmentContainer() {
        let cnt = document.createElement('div');
        cnt.id = 'attachmentPanel';
        cnt.classList.add(...['panel', 'panel-default']);
        cnt.appendChild(this.attachmentHeading.render());

        let attachmentBody = document.createElement('div');
        attachmentBody.classList.add('panel-body');
        cnt.appendChild(attachmentBody);

        return cnt;
    }

    _renderTreeContainer() {

    }

    getAttachments(documentId, parentId = null) {
        return ajaxCall(
            {
                method: 'get',
                url: _g.document.urls.upload_attachment_url,
                data: {id: documentId, parent: parentId}
            },
            (resp) => {
                if (Array.isArray(resp)) {
                    let t = [];
                    resp.map(e => {
                        t.push(e);
                    });
                    this.attachments[parentId ? parentId : this.rootNodeId] = t;
                }
            },
            (resp) => {
                reject(resp);
            })
    }

    renderTiles(attachments) {
        if (!Array(attachments)) {
            return;
        }
        attachments.map(e => {
            if (!e.is_dir) {
                if (e.attachment) {
                    this.attachmentContainer.appendChild(Tile.render(e, this.documentId, this.addCallback, this.removeCallback));
                }
            } else {
                //this.attachmentContainer.appendChild(Tile.renderDir(e, this.documentId));
            }
        });
    }

    render(parentId = null) {
        let _parentId = parentId ? parentId : this.rootNodeId;

        this.attachmentPanel.getElementsByClassName('panel-body')[0].innerHTML = '';

        if (!this.attachments[_parentId]) {
            this.getAttachments(this.documentId, parentId).then(
                () => {
                    this.renderTiles(this.attachments[_parentId]);
                });
        } else {
            this.renderTiles(this.attachments[_parentId]);
        }
    }

    sizeToggle() {
        jsUtils.Utils.toggleClass(this.attachmentPanel, 'thumbnail-small');
    }

    add(type) {
        $("#addAttachmentForm").modal();
    }

    pasteScreen() {
        this.printScreenModal.render();
    }

    getZip() {
    }

    getParent() {
        let selectedNode = $("#atmDirectoryTree").jstree(true).get_selected();
        if (Array.isArray(selectedNode) && selectedNode.length) {
            return selectedNode[0];
        } else {
            //todo: drut. Poprawić
            return '__root__';
        }
    }

    _handleAttachment(e) {
        let parent = this.getParent();
        if (parent) {
            this.attachments[parent].push(e);
        } else {
            this.attachments[this.rootNodeId].push(e);
        }
        this.attachmentContainer.appendChild(Tile.render(e, this.documentId, this.addCallback, this.removeCallback));
    }

    init() {
        let _this = this;
        document.getElementById('attachmentPanel').appendChild(this.attachmentPanel);

        this.attachmentHeading.sizeBtn.addEventListener('click', () => {
            this.sizeToggle();
        });

        this.attachmentHeading.addBtn.addEventListener('click', () => {
            this.add();
        });
        this.attachmentHeading.pasteScreenBtn.addEventListener('click', () => {
            this.pasteScreen();
        });
        this.attachmentHeading.zipBtn.addEventListener('click', () => {
            this.getZip();
        });

        this.dropzone = new MyDropzone({
            uploadUrl: this.uploadAttachmentUrl,
            container: '#dropzone_atm',
            previewTemplate: '#attachmentUploadTemplate',
            previewContainer: '#attachmentBeforeUpload tbody',
            dropzoneForm: '#addAttachmentForm',
            documentId: _g.document.id,
            createAttachment: true,

            getPath: function () {
                // let node = atmTree.getSelected();
                // if (node) {
                //     let path = atmTree.getPath(node, true);
                //     return path ? path: '';
                // }
                // else {
                //     return '';
                // }
            },

            onSavedFiles: function (i, e, file) {
                _this._handleAttachment(e);
            },

            onComplete: function () {
                // atmTree.update();
            },

            getParent: _this.getParent,

            setCsrf: function () {
                return _g.csrfmiddlewaretoken;
            }

        });
    }
}

export default Attachment;