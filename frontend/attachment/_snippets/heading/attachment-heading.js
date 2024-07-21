import HeadingButtons from "./heading-buttons";
import ClipboardImage from "../../../_core/clipboard/clipboard-image"

import ajaxCall from "../../../_core/ajax";

class AttachmentHeading {
    constructor() {
        this.addBtn = HeadingButtons.addBtn();
        this.sizeBtn = HeadingButtons.sizeBtn();
        this.pasteScreenBtn = HeadingButtons.pasteScreenBtn();

        this.zipBtn = HeadingButtons.zipBtn();
    }

    render() {
        let heading = document.createElement('div');
        heading.classList.add(...['panel-heading', 'attachment-heading']);

        let left = document.createElement('div');
        left.style.cssFloat = 'left';

        let right = document.createElement('div');
        right.style.cssFloat = 'right';

        left.appendChild(this.sizeBtn);

        [this.addBtn, this.pasteScreenBtn, this.zipBtn].map(e => {
            right.appendChild(e);
        });
        heading.appendChild(left);
        heading.appendChild(right);

        return heading;
    }


}

export default AttachmentHeading;