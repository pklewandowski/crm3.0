const documentSectionContainerId = 'documentSectionContainer';
const documentSectionLabelContainerId = 'documentSectionLabelContainer';
const documentSectionContentContainerId = 'documentSectionContentContainer';


class DocumentAttributeContainer {
    constructor(container) {
        this.className = 'DocumentAttributeContainer';
        if (!container) {
            console.log(`[${this.className}]: Class variable 'container' referring to main document attribute container is not defined`);
        }
        this.container = container;
        this.init();
    }

    init() {
        if (!this.container) {
            return;
        }
        this.container
            .innerHTML = document.getElementById('attributeContainerTemplate').innerHTML
            .replace('__DOCUMENT_SECTION_CONTAINER_ID__', documentSectionContainerId)
            .replace('__DOCUMENT_SECTION_LABEL_CONTAINER_ID__', documentSectionLabelContainerId)
            .replace('__DOCUMENT_SECTION_CONTENT_CONTAINER_ID__', documentSectionContentContainerId);
    }

    get labelContainer() {
        return this.container.querySelector(`#${documentSectionLabelContainerId}`);
    }

    get contentContainer() {
        return this.container.querySelector(`#${documentSectionContentContainerId}`);
    }

}

export default DocumentAttributeContainer;