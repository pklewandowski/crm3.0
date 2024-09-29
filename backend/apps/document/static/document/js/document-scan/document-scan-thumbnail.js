const DocumentScanThumbnail = function (url) {
    let containerClassname = 'document-scan-thumbnail';
    "use strict";
    this.init = function () {
        this.container = document.createElement('div');
        this.container.className = containerClassname; //'document-scan-thumbnail';
        this.container.dataset.status="NEW";
        this.url = url;
        this.image = new Image();
        this.image.src = url;
        this.template = document.getElementById('documentScanTemplate');
        this._render();
    };

    this._render = function () {
        this.image.onload = () => {
            let template = document.importNode(this.template.content, true);
            template.querySelector('img').src = url;
            template.getElementById('id_scan-__prefix__-file_name').value = url.substr(url.lastIndexOf('/') + 1);
            this.container.appendChild(template);
        }
    };

    this.get = function () {
        return this.container;
    };

    this.init();
};

export default DocumentScanThumbnail;