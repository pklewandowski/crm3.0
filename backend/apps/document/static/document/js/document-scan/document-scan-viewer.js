const DocumentScanViewer = function (documentScanViewerContainer) {
    let _this = this;

    this._redraw = () => {
        this.canvas.width = this.image.width * this.scaleFactor;
        this.canvas.height = this.image.height * this.scaleFactor;
        this.ctx.scale(this.scaleFactor, this.scaleFactor);
        this.ctx.drawImage(this.image, 0, 0);

        if (this.selectBox) {
            this.ctx.fillStyle = "rgba(0,150,255,.3)";
            this.ctx.fillRect(this.selectBox.left, this.selectBox.top, this.selectBox.width, this.selectBox.height);
        }
    };

    this._handleScroll = (evt) => {
        if (evt.shiftKey === true) {
            let delta = (evt.wheelDelta ? evt.wheelDelta / 120 : evt.detail ? -evt.detail : 0) / 30;
            this.zoom(delta);
            return evt.preventDefault() && false;
        }
    };

    this.loadImage = function (url) {
        this.image.onload = () => {
            this._redraw();
        };
        this.image.src = url;
    };

    this.zoom = function (delta) {
        this.scaleFactor = Math.min(2.0, Math.max(.2, this.scaleFactor + delta));
        this._redraw();
    };

    this.getCanvas = function () {
        return _this.canvas;
    };

    this._getMousePosition = (evt) => {
        let rect = this.canvas.getBoundingClientRect();
        return {
            x: parseInt((evt.clientX - rect.left) / (rect.right - rect.left) * (this.canvas.width / this.scaleFactor)),
            y: parseInt((evt.clientY - rect.top) / (rect.bottom - rect.top) * (this.canvas.height / this.scaleFactor))
        };
    };

    this._onMouseMove = (e) => {

        if (this.drawSelectBox) {
            let pos = this._getMousePosition(e);
            let width = pos.x - this.selectBox.left;
            let height = pos.y - this.selectBox.top;


            this.selectBox.width = pos.x - this.selectBox.left;
            this.selectBox.height = pos.y - this.selectBox.top;

            this._redraw();
        }
    };

    this._onMouseDown = (e) => {
        let pos = this._getMousePosition(e);
        this.selectBox = {top: pos.y, left: pos.x, width: 0, height: 0};
        this.drawSelectBox = true;
    };

    this._handleOcr = () => {
        $(".loader-container").fadeIn();
        $.ajax({
            method: 'post',
            url: _g.document.url.ocrBox,
            data: {
                filename: this.image.src.substr(this.image.src.lastIndexOf('/') + 1),
                box: JSON.stringify(this.selectBox)
            },

            complete: () => {
                $(".loader-container").fadeOut();
                this.selectBox = null;
                this._redraw();
            }

        }).done((resp) => {

            let res = JSON.parse(resp);
            let textArea = document.createElement('textarea');
            console.log(res.text.length);
            if (res.text.length) {
                textArea.value = res.text;
                document.body.appendChild(textArea);
                textArea.select();
                document.execCommand("copy");
                document.body.removeChild(textArea);
                let dots = res.text.length > 100 ? '...' : '';
                Alert.info('Skopiowano do schowka:', `${res.text.substr(0, 100)}${dots}`);
            } else {
                Alert.warning('Nie rozpoznano tekstu', '');
            }
        }).fail(function (resp) {
            let res = resp.responseJSON;
            Alert.error('Wystąpił błąd:', res.errmsg);
        });
    };

    this._onMouseUp = (e) => {
        this.drawSelectBox = false;
        if (this.selectBox) {
            if (this.selectBox.width === 0 || this.selectBox.height === 0) {
                this.selectBox = null;
            } else {

                if (this.selectBox.width < 0) {
                    this.selectBox.left = this.selectBox.left + this.selectBox.width;
                    this.selectBox.width = -this.selectBox.width;
                }
                if (this.selectBox.height < 0) {
                    this.selectBox.top = this.selectBox.top + this.selectBox.height;
                    this.selectBox.height = -this.selectBox.height;
                }

                this._handleOcr();
            }
        }
    };

    this.init = () => {
        "use strict";
        this.scaleFactor = 1.0;
        this.drawSelectBox = false;

        this.canvas = document.createElement('canvas');
        this.canvas.id = 'scanCanvas';
        this.canvas.style.zIndex = 1;
        this.canvas.style.border = "1px solid #ddd";
        this.canvas.style.margin = 'auto';

        this.container = document.getElementById(documentScanViewerContainer);
        this.container.appendChild(this.canvas);
        this.ctx = this.canvas.getContext("2d");

        this.image = new Image();

        this.clipboardTextInput = document.getElementById('clipboardTextInput');

        this.selectBox = null;
        this.mouse = {
            x: 0,
            y: 0,
            startX: 0,
            startY: 0
        };

        this.canvas.addEventListener('DOMMouseScroll', this._handleScroll, false);
        this.canvas.addEventListener('mousewheel', this._handleScroll, false);
        this.canvas.addEventListener('mousemove', this._onMouseMove, false);
        this.canvas.addEventListener('mousedown', this._onMouseDown, false);
        this.canvas.addEventListener('mouseup', this._onMouseUp, false);
    };

    this.init();
};

export default DocumentScanViewer;