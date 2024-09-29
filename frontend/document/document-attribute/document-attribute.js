import DocumentAttributeContainer from "./document-attribute-container";
import DocumentAttributeRenderer from "./renderer/document-attribute-renderer";


class DocumentAttribute {
    constructor(container, documentData, errorList = null) {
        this.documentData = documentData;
        this.containerElement = document.getElementById(container);
        this.container = new DocumentAttributeContainer(this.containerElement);
        this.renderer = new DocumentAttributeRenderer(
            this.container.labelContainer,
            this.container.contentContainer,
            this.documentData,
            errorList
        );
        this.errorList = errorList;
        this.init();
    }

    init() {
    }
}

export default DocumentAttribute;
