
import '../scss/avatar-control.scss';

class AvatarControl {
    constructor(container) {
        if (typeof container === 'object') {
            this.container = container;
        } else {
            this.container = document.getElementById(container);
        }

        // this.html = '<div class="avatar-wrapper">\n' +
        //     '\t<img class="profile-pic" src="" />\n' +
        //     '\t<div class="upload-button">\n' +
        //     '\t\t<i class="fa fa-arrow-circle-up" aria-hidden="true"></i>\n' +
        //     '\t</div>\n' +
        //     '\t<input class="file-upload" type="file" accept="image/*"/>\n' +
        //     '</div>';
    }

    readURL = function (input) {
        if (input.files && input.files[0]) {
            let reader = new FileReader();

            reader.onload = function (e) {
                $('.profile-pic').attr('src', e.target.result);
            };
            reader.readAsDataURL(input.files[0]);
        }
    };

    init() {

        $(".upload-button").on('click', function () {
            $(".file-upload").click();
        });
    }

    render() {
        let avatarWrapper = jsUtils.Utils.domElement('div', null, 'avatar-wrapper');

        let avatarImg = jsUtils.Utils.domElement('img', null, 'profile-pic');
        avatarImg.src = "";

        let uploadButton = jsUtils.Utils.domElement('div', null, 'upload-button');
        let uploadButtonI = jsUtils.Utils.domElement('i', null, ['fa', 'fa-arrow-circle-up']);
        uploadButtonI.setAttribute('aria-hidden', true);
        uploadButton.appendChild(uploadButtonI);


        let fileUpload = jsUtils.Utils.domElement('input', 'idAvatar', 'file-upload');
        fileUpload.type = 'file';
        fileUpload.setAttribute('accept', 'image/*');
        fileUpload.addEventListener('change', (e) => {
            this.readURL(e.target);
        });

        uploadButton.addEventListener('click', () => {
            $(fileUpload).click();
            // fileUpload.dispatchEvent(new Event('click'));
        });

        avatarWrapper.appendChild(avatarImg);
        avatarWrapper.appendChild(uploadButton);
        avatarWrapper.appendChild(fileUpload);

        this.container.appendChild(avatarWrapper);
    }

}

export {AvatarControl};