function clear_form_elements(ele) {

    $(ele).find(':input').each(function () {
        switch (this.type) {
            case 'password':
            case 'select-multiple':
            case 'select-one':
            case 'text':
            case 'textarea':
                $(this).val('');
                break;
            case 'checkbox':
            case 'radio':
                this.checked = false;
        }
    });

    $(ele).find('.select2').each(function(){
        $(this).val(null).trigger('change');
    });
}

function toggle_form_elements(ele, enabled) {

    $(ele).find(':input').each(function () {
        if(!enabled) {
            $(this).attr('disabled', true);
        }else {
            $(this).removeAttr('disabled');
        }
    });
}


