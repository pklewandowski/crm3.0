$(document).ready(function () {
    $("input#id_meeting_room-color").ColorPickerSliders({
        size: 'sm',
        placement: 'bottom',
        swatches: true,
        order: {
            hsl: 1
        },
        previewformat: 'hex'
    });
});

