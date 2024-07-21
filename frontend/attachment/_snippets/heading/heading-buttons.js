import HeadingComponents from "./heading-components";

class HeadingButtons extends HeadingComponents {
    constructor() {
        super();
    }

    static sizeBtn() {
        return HeadingButtons.btn('attachmentSizeToggleBtn', 'search');
    }

    static zipBtn() {
        return HeadingButtons.btn('attachmentZipBtn', 'download');
    }

    static pasteScreenBtn() {
        return HeadingButtons.btn('attachmentPasteScreenBtn', 'camera');
    }

    static addBtn() {
        return HeadingButtons.btn('attachmentAddBtn', 'paperclip');
    }
}

export default HeadingButtons;