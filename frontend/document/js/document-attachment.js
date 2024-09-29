import Attachment from "../../attachment/attachment";

class DocumentAttachment extends Attachment {

    constructor(documentId, containerId) {
        super(documentId, containerId);
        this.render();
    }
}

export default DocumentAttachment;