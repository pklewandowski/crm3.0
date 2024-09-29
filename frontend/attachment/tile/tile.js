import {SystemException} from "../../_core/exception";
import Alert from "../../_core/alert";


const className = 'Tile';

class Tile {

    static renderDir(data, documentId) {
        if (!data) {
            return;
        }

        let tile = document.createElement('div');

        tile.classList.add(...['thumbnail', 'thumbnail-image-container', 'thumbnail-dir']);

        tile.dataset.id = data.id;
        tile.dataset.fileName = data.name;

        let f = document.createElement('img');
        f.classList.add('desaturate');
        f.src = `/static/attachment/img/folder.png`;
        tile.appendChild(f);

        return tile;
    }

    static render(data, documentId, addCallback = null, removeCallback = null) {
        /*
    <div class="thumbnail thumbnail-image-container __THUMBNAIL_SIZE__" tabindex="-1" data-id="__ATTACHMENT_ID__">
        <div class="thumbnail-btn thumbnail-close-btn"><i class="fa fa-times"></i></div>
        <div class="thumbnail-btn thumbnail-restore-btn"><i class="fa fa-redo"></i></div>
        <div class="thumbnail-image __THUMBNAIL_IMAGE_SIZE__" data-id="__ATTACHMENT_ID__" data-file_name="__FILE_NAME__" data-mime_type="__FILE_MIME_TYPE__">
            <img data-type="scan" class="desaturate" src="__FILE_ICON__"/>
        </div>
        <div class="scroll-box">
            <div class="scroll-text" data-toggle="tooltip" title="__FILE_ORIGINAL_NAME__">__FILE_ORIGINAL_NAME__</div>
        </div>


        <input class="thumbnail-value" type="hidden" name="{{ attachment_formset.empty_form.file_name.html_name }}" value="__FILE_NAME__"/>
        <input class="thumbnail-value" type="hidden" name="{{ attachment_formset.empty_form.file_original_name.html_name }}" value="__FILE_ORIGINAL_NAME__"/>
        <input type="hidden" name="{{ attachment_formset.empty_form.file_mime_type.html_name }}" value="__FILE_MIME_TYPE__"/>
        <input type="hidden" name="{{ attachment_formset.empty_form.file_ext.html_name }}" value="__FILE_EXT__"/>
        <input type="hidden" name="{{ attachment_formset.empty_form.file_path.html_name }}" value="__FILE_PATH__"/>
        <input type="hidden" name="{{ attachment_formset.empty_form.DELETE.html_name }}" class="formset-row-delete"/>
        <input type="hidden" name="{{ attachment_formset.empty_form.type.html_name }}" value="__ATTACHMENT_TYPE__"/>
        <input type="hidden" name="{{ attachment_formset.empty_form.id.html_name }}"/>
        <div class="attachment-description">
            <textarea class="form-control input-md attachment-description-field" placeholder="Dodaj opis..."
                      name="{{ attachment_formset.empty_form.description.html_name }}"></textarea>
        </div>

    </div>
         */

        if (!data) {
            jsUtils.LogUtils.log(`[${className}][render]:'brak danych`);
            return;
        }

        let atm = data.attachment;

        if (!atm) {
            jsUtils.LogUtils.log(`[${className}][render]:'brak załącznika`);
            return;
        }

        if (!atm.id) {
            throw new SystemException(`[${className}][render]: attachment id cannot be empty`);
        }
        if (!atm.file_name) {
            throw new SystemException(`[${className}][render]: attachment file name cannot be empty`);
        }
        if (!atm.mime) {
            throw new SystemException(`[${className}][render]: attachment mime type cannot be empty`);
        }

        let tile = document.createElement('div');
        let mimeType = atm.mime.type.split('/')[0];

        tile.classList.add(...['thumbnail', 'thumbnail-image-container']);

        tile.dataset.id = atm.id;
        tile.dataset.fileName = atm.file_name;
        tile.dataset.fileOriginalName = atm.file_original_name;
        tile.dataset.fileExt = atm.fileExt;
        tile.dataset.mime = JSON.stringify(atm.mime);

        // render navButton container
        let navButtonContainer = document.createElement('div');
        navButtonContainer.classList.add('nav-button-container');
        tile.appendChild(navButtonContainer);

        // render play button
        if (mimeType === 'audio') {
            let audio = document.createElement('audio');
            audio.src = `/media/${atm.file_path}${atm.file_name}`;
            // let audio = new Audio(`/media/${atm.file_path}${atm.file_name}`);

            audio.addEventListener('canplay', () => {
            });

            let progresSliderContainer = document.createElement('div');
            let progresSlider = document.createElement('input');

            progresSliderContainer.appendChild(progresSlider);

            let speakerButtonContainer = document.createElement('div');
            let speakerIcon = document.createElement('i');
            speakerButtonContainer.appendChild(speakerIcon);

            speakerIcon.classList.add(...['fa', 'fa-play-circle']);
            speakerIcon.addEventListener('click', (el) => {
                el.stopPropagation();
                // audio.crossOrigin = "anonymous";
                let si = $(speakerIcon);
                if (si.hasClass('fa-play-circle')) {
                    audio.play();
                    progresSlider.interval = setInterval(progresSlider.intervalFunction, 2000);
                } else {
                    audio.pause();
                    console.log('clear interval', progresSlider.interval);
                    clearInterval(progresSlider.interval);
                }
                si.toggleClass('fa-stop-circle fa-play-circle');
                console.log('audio cyr dur', audio.currentTime);
            });

            // audio.volume = .3;
            tile.appendChild(audio);

            // create audio object
            audio.addEventListener('loadedmetadata', () => {

                // create audio contrtols and progress bar
                let audioControl = document.createElement('div');
                audioControl.classList.add('slider-container');

                progresSlider.type = 'range';
                progresSlider.value = 0;
                progresSlider.setAttribute('min', 0);
                progresSlider.setAttribute('max', audio.duration);
                progresSlider.addEventListener('input', () => {
                    audio.currentTime = progresSlider.value;
                    console.log('audio', audio);
                });
                // show audio progress
                progresSlider.intervalFunction = () => {
                    progresSlider.value = parseInt(audio.currentTime);
                };

                audioControl.appendChild(speakerButtonContainer);
                audioControl.appendChild(progresSliderContainer);
                tile.appendChild(audioControl);
            });
        }

        // render close button
        {
            let e = document.createElement('div');
            e.classList.add(...['thumbnail-btn', 'thumbnail-close-btn']);

            let f = document.createElement('i');
            f.classList.add(...['fa', 'fa-times']);

            e.appendChild(f);
            e.addEventListener('click', () => {
                Alert.questionWarning(
                    'Czy na pewno usunąć załącznik?',
                    'Usunięcie załącznika jest operacją nieodwracalną. Plik zostanie fizycznie usunięty z dysku.',
                    () => {
                        $.ajax({
                            method: 'delete',
                            url: _g.document.urls.upload_attachment_url,
                            headers: {"X-CSRFToken": Cookies.get('csrftoken')},
                            data: {
                                documentId: documentId,
                                attachmentId: tile.dataset.id
                            },
                            success: (resp) => {
                                if (typeof removeCallback === 'function') {
                                    removeCallback(data);
                                }
                                tile.remove();
                            },
                            error: (resp) => {
                                Alert.error('Błąd', resp.responseJSON.errmsg);
                            }
                        })
                    });
            });

            navButtonContainer.appendChild(e);
        }

        // render restore button
        {
            let e = document.createElement('div');
            e.classList.add(...['thumbnail-btn', 'thumbnail-restore-btn']);

            let f = document.createElement('i');
            f.classList.add(...['fa', 'fa-redo']);
            e.appendChild(f);

            // render thumbnail image
            e = document.createElement('div');
            e.classList.add('thumbnail-image');

            f = document.createElement('img');
            f.classList.add('desaturate');

            if (mimeType === 'image') {
                f.src = `/media/${atm.file_path}${atm.file_name}`; //todo: get media catalog name from config
            } else {
                f.src = `/static/attachment/img/file_types${atm.mime.icon_lg}`;
            }

            f.addEventListener('click', (e) => {
                console.log('tile image clicked');
                //let mimeType = atm.mime.type;
                let id = atm.id;

                if (mimeType === 'image') {
                    console.log(f);
                    document.getElementById('image_preview').src = f.src;
                    $('#image_preview_modal').modal();

                } else {
                    if (id) {
                        window.location = '/attachment/download/' + id + '/';
                    } else {
                        Alert.info('Plik będzie dostępny do podglądu po zapisaniu danych');
                    }
                }
            });

            e.appendChild(f);
            tile.appendChild(e);
        }

        // render atachment name
        {
            let e = document.createElement('div');
            let f = document.createElement('div');

            e.classList.add('scroll-box');

            f.classList.add('scroll-text');
            f.dataset['toggle'] = 'tooltip';
            f.title = atm.file_original_name;
            f.innerText = atm.file_original_name;

            e.appendChild(f);
            tile.appendChild(e);
        }

        if (atm.thumbnailSize) {
            tile.classList.add(atm.thumbnail_size);
        }
        tile.tabIndex = -1;
        return tile;
    }
}

export default Tile;