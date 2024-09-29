function desaturate(r, g, b) {
    var intensity = 0.3 * r + 0.59 * g + 0.11 * b;
    var k = 1;
    r = Math.floor(intensity * k + r * (1 - k));
    g = Math.floor(intensity * k + g * (1 - k));
    b = Math.floor(intensity * k + b * (1 - k));
    return [r, g, b];
}


/*
 color - hex value
 saturation - [0:100]
  */

function desaturateColor(color, saturation) {
    var col = hexToRgb(color);
    var sat = Number(saturation) / 100;
    var gray = col.r * 0.3086 + col.g * 0.6094 + col.b * 0.0820;

    col.r = Math.round(col.r * sat + gray * (1 - sat));
    col.g = Math.round(col.g * sat + gray * (1 - sat));
    col.b = Math.round(col.b * sat + gray * (1 - sat));

    var out = rgbToHex(col.r, col.g, col.b);

    $('#output').val(out);

    $('body').css("background", out);
}

function componentToHex(c) {
    var hex = c.toString(16);
    return hex.length == 1 ? "0" + hex : hex;
}

function rgbToHex(r, g, b) {
    return "#" + componentToHex(r) + componentToHex(g) + componentToHex(b);
}

function hexToRgb(hex) {
    var result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16)
    } : null;
}

/*
* uruchamianie klasy ctrl-c ctrl-v obrazu
*  var CLIPBOARD = new CLIPBOARD_CLASS("my_canvas", true);
*
*  */

function ClipboardImage(canvasId, autoresize) {
    let _self = this;
    if (canvasId) {
        this.canvas = document.getElementById(canvasId);
    }
    if (!this.canvas) {
        this.canvas = document.getElementById('paste_canvas'); //

        if (!$(this.canvas).is("canvas")) {
            console.log('not canvas!');
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
        // document.getElementById('paste_ff').addEventListener('DOMSubtreeModified', function () {
        //     if (paste_mode === 'auto' || ctrl_pressed === false) {
        //         return true;
        //     }
        //     //if paste handle failed - capture pasted object manually
        //     if (pasteCatcher.children.length === 1) {
        //         if (pasteCatcher.firstElementChild.src !== undefined) {
        //
        //             //image
        //             _self.paste_createImage(pasteCatcher.firstElementChild.src);
        //         }
        //     }
        //     //register cleanup after some time.
        //     setTimeout(function () {
        //         pasteCatcher.innerHTML = '';
        //     }, 20);
        // }, false);
    }();
    //default paste action
    this.paste_auto = function (e) {
        // if (!$(document.activeElement).is("canvas")) {
        //     console.log('not canvas');
        //     return;
        // }
        // console.log(document.activeElement);

        paste_mode = '';
        pasteCatcher.innerHTML = '';
        var plain_text_used = false;
        if (e.clipboardData) {
            var items = e.clipboardData.items;
            if (items) {
                paste_mode = 'auto';
                //access data directly
                for (var i = 0; i < items.length; i++) {
                    if (items[i].type.indexOf("image") !== -1) {
                        //image
                        var blob = items[i].getAsFile();


                        //alternatywny z ajaxem

                        //  var form = new FormData();
                        //  form.append('blob', blob);
                        //
                        // var request = new XMLHttpRequest();
                        //
                        //  request.open(
                        //      "POST",
                        //      "/attribute/save-pasted-image/",
                        //      true
                        //  );
                        //  request.send(form);
                        //
                        //  $.ajax({
                        //      type: 'POST',
                        //      url: '/attribute/save-pasted-image/',
                        //      data: form,
                        //      processData: false,
                        //      contentType: false
                        //  }).done(function (data) {
                        //      console.log(data);
                        //      _self.paste_createImage('/media/tmp/' + data.name);
                        //  });

                        //--koniec


                        var URLObj = window.URL || window.webkitURL;
                        var source = URLObj.createObjectURL(blob);
                        this.paste_createImage(source);
                    }
                }
                // e.preventDefault();
            }
            else {
                //wait for DOMSubtreeModified event
                //https://bugzilla.mozilla.org/show_bug.cgi?id=891247
            }
        }
    };
    //on keyboard press -
    this.on_keyboard_action = function (event) {
        k = event.keyCode;
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
        k = event.keyCode;
        //ctrl
        if (k === 17 || event.metaKey || event.ctrlKey || event.key === 'Meta')
            ctrl_pressed = false;
    };
    //draw image
    this.paste_createImage = function (source) {

        // if (!this.canvas) {
        //     this.canvas = document.getElementById('paste_canvas'); //
        //
        //     if (!$(this.canvas).is("canvas")) {
        //         console.log('not canvas!');
        //         return;
        //     }
        // }

        var pastedImage = new Image();

        console.log('created image');

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
        console.log(pastedImage.src)
    };
}