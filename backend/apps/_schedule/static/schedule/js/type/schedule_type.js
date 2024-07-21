$(document).ready(function () {
    $("input#id_color").ColorPickerSliders({
        size: 'sm',
        placement: 'bottom',
        swatches: false,
        order: {
            hsl: 1
        },
        previewformat:'hex'

    });

    //$("input#id_color").colorpicker({ color: '#AA3399', format: 'hex' });
});
