function ClipboardImage(canvas, autoresize) {
    var _self = this;
    if (canvas) {
        if(typeof canvas === 'object') {
            this.canvas = canvas
        }
        this.canvas = document.getElementById(canvas);
    }
    if (!this.canvas) {
        this.canvas = document.getElementById('paste_canvas'); //

        if (!$(this.canvas).is("canvas")) {
            return;
        }
    }
    var ctx = this.canvas.getContext("2d");
    var ctrl_pressed = false;
    var reading_dom = false;
    var text_top = 15;
    var pasteCatcher;
    var paste_mode;

    //handlers
    document.addEventListener('keydown', function (e) {
        _self.on_keyboard_action(e);
    }, false); //firefox fix
    document.addEventListener('keyup', function (e) {
        _self.on_keyboardup_action(e);
    }, false); //firefox fix
    document.addEventListener('paste', function (e) {
        _self.paste_auto(e);
    }, false); //official paste handler

    //constructor - prepare
    this.init = function () {
        //if using auto
        // if (window.Clipboard)
        //     return true;

        pasteCatcher = document.createElement("div");
        pasteCatcher.setAttribute("id", "paste_ff");
        pasteCatcher.setAttribute("contenteditable", "");
        pasteCatcher.style.cssText = 'opacity:0;position:fixed;top:0px;left:0px;';
        pasteCatcher.style.marginLeft = "-20px";
        pasteCatcher.style.width = "0px";
        document.body.appendChild(pasteCatcher);
    }();
    //default paste action
    this.paste_auto = function (e) {
        paste_mode = '';
        pasteCatcher.innerHTML = '';
        if (e.clipboardData) {
            var items = e.clipboardData.items;
            if (items) {
                paste_mode = 'auto';
                //access data directly
                for (var i = 0; i < items.length; i++) {
                    if (items[i].type.indexOf("image") !== -1) {
                        //image
                        var blob = items[i].getAsFile();

                        var URLObj = window.URL || window.webkitURL;
                        var source = URLObj.createObjectURL(blob);
                        this.paste_createImage(source);
                    }
                }
            }
            else {
                //wait for DOMSubtreeModified event
                //https://bugzilla.mozilla.org/show_bug.cgi?id=891247
            }
        }
    };
    //on keyboard press -
    this.on_keyboard_action = function (event) {
        let k = event.keyCode;
        //ctrl
        if (k === 17 || event.metaKey || event.ctrlKey) {
            if (ctrl_pressed === false)
                ctrl_pressed = true;
        }
        //c
        if (k === 86) {
            if (document.activeElement !== undefined && document.activeElement.type === 'text') {
                //let user paste into some input
                return false;
            }

            if (ctrl_pressed === true && !window.Clipboard) {
                // pasteCatcher.focus();
            }
        }
    };
    //on kaybord release
    this.on_keyboardup_action = function (event) {
        let k = event.keyCode;
        //ctrl
        if (k === 17 || event.metaKey || event.ctrlKey || event.key === 'Meta')
            ctrl_pressed = false;
    };
    //draw image
    this.paste_createImage = function (source) {

        var pastedImage = new Image();

        pastedImage.onload = function () {
            if (autoresize === true) {
                //resize canvas
                _self.canvas.width = pastedImage.width;
                _self.canvas.height = pastedImage.height;
            }
            else {
                //clear canvas

                ctx.clearRect(0, 0, _self.canvas.width, _self.canvas.height);
            }
            ctx.drawImage(pastedImage, 0, 0);
        };
        pastedImage.src = source;
    };
}

export default ClipboardImage;