$(document).ready(function () {


    $('.lvh-txt-control .dropdown-menu').click(function () {
        return false;
    });

    $.each($('.lvh-txt-control'), function (i, e) {
        var that = $(this);
        var tree_item = $(this).find($('div#hierarchy-tree'));
        var j = $(e).find('.lvh-txt-json');
        var lvh = {};

        if (tree_item) {
            tree_item.jstree({
                "core": {
                    "data": tree_item.data('json'),
                    "multiple": false
                },
                "plugins": ["checkbox"],

                'checkbox': {
                    'deselect_all': true,
                    'three_state': false
                }
            });
        }

        tree_item.on('loaded.jstree', function (e, data) {

            if (j.val() != null && j.val() != '' && j.val() != 'null') {

                var json_text = $.parseJSON(j.val().replace(/\'/g, "\""));
                var dtc = json_text.dtc;
                var custom = json_text.custom;

                tree_item.jstree('select_node', '#' + dtc);

            }
        });

        tree_item.on('changed.jstree', function (e, data) {

            j_node = data.instance.get_node(data.selected[0])
            lvh['dtc'] = j_node.id;
            lvh['custom'] = '';

            console.log(lvh);
            that.find('input.lvh-txt-json').val(JSON.stringify(lvh));
            that.find('input.lvh-txt-display').val(j_node.text);
            that.find('[data-toggle="dropdown"]').parent().removeClass('open');
            that.find('button.dropdown-toggle').focus();
        });
    });


    $.each($('.lv-txt-control'), function (i, e) {

        var j = $(e).find('.lv-txt-json');

        if (j.val() != null && j.val() != '' && j.val() != 'null') {

            var json_text = $.parseJSON(j.val().replace(/\'/g, "\""));
            var dtc = json_text.dtc;
            var custom = json_text.custom;

            if (custom.length > 0) {

                $(this).find('.lv-txt-custom').val(custom);
                //$('input:radio[name="gender"]').filter('[value="Male"]').attr('checked', true);
                $(this).find('.lv-txt-dtc-radio-custom').prop('checked', true);
                $(this).find('.lv-txt-dtc-radio-custom').attr('checked', 'checked');
                $(this).find('.lv-txt-dtc-option').css('display', 'none');
                $(this).find('.lv-txt-custom').css('display', 'inherit');

            } else {
                $(this).find('.lv-txt-dtc-option').val(dtc);
                $(this).find('.lv-txt-dtc-radio-option').prop('checked', true);
                $(this).find('.lv-txt-dtc-radio-option').attr('checked', 'checked');
                $(this).find('.lv-txt-dtc-option').css('display', 'inherit');
                $(this).find('.lv-txt-custom').css('display', 'none');
            }
        }
        else {
            $(this).find('.lv-txt-dtc-radio-option').prop('checked', true);
            $(this).find('.lv-txt-dtc-radio-option').attr('checked', 'checked');
        }
    });

    $.each($('.lvm-txt-control'), function (i, e) {

        var j = $(e).find('.lvm-txt-json');

        if (j.val() != null && j.val() != '' && j.val() != 'null') {

            var json_text = $.parseJSON(j.val().replace(/\'/g, "\""));
            var dtc = json_text.dtc;
            var custom = json_text.custom;

            for (i in dtc) {

                $.each($(this).find('.lvm-txt-dtc'), function () {
                    if ($(this).val() == dtc[i]) {
                        $(this).prop('checked', true);
                    }
                });
            }

            $(this).find('.lvm-txt-dtc-option').val(dtc);
            $(this).find('.lvm-txt-custom').val(custom);
            if (dtc.length > 0) {
                $(this).find('button.dropdown-toggle').addClass('lvm-dropdown-checked');
            }
            else {
                $(this).find('button.dropdown-toggle').removeClass('lvm-dropdown-checked');
            }
        }
    });

    $('[checked="checked"]').parent().addClass("active");


//$.each($('.lvm-txt-control'), function (i, e) {
//    console.log(e.find('.lvm-txt-json'));
//}); #5cb85c


    $('.lvm-txt-dtc, .lvm-txt-custom').change(function () {

        var values = [];
        var lvm = {};

        $.each($(this).parents('.lvm-txt-control').find('input.lvm-txt-dtc'), function (i, e) {
            var el = $(e);
            if (el.is(':checked')) {
                values.push(el.val());
            }
        });

        lvm['dtc'] = values;
        lvm['custom'] = $(this).parents('.lvm-txt-control').find('input.lvm-txt-custom').val();

        if (lvm['dtc'].length > 0) {
            $(this).parents('.lvm-txt-control').find('button.dropdown-toggle').addClass('lvm-dropdown-checked');
        }
        else {
            $(this).parents('.lvm-txt-control').find('button.dropdown-toggle').removeClass('lvm-dropdown-checked');
        }

        if (lvm['dtc'].length == 0 && !lvm['custom']) {
            $(this).parents('.lvm-txt-control').children('input.lvm-txt-json').val(null);
        }
        else {

            $(this).parents('.lvm-txt-control').children('input.lvm-txt-json').val(JSON.stringify(lvm));
        }
    });

    $('.lv-txt-dtc, .lv-txt-dtc-option, .lv-txt-custom').change(function () {

        var lv = {};
        var container = $(this).parents('.lv-txt-control');
        var custom = container.find('.lv-txt-custom');
        var option = container.find('.lv-txt-dtc-option');
        var json_value = container.children('input.lv-txt-json');

        if ($(this).data('type') == 'dtc-custom' || $(this).data('type') == 'custom') {
            custom.css('display', 'inherit');
            option.css('display', 'none');

            lv['dtc'] = '';
            lv['custom'] = custom.val();

        }
        else {
            option.css('display', 'inherit');
            custom.css('display', 'none');
            //custom.val(null);

            lv['dtc'] = option.val();
            lv['custom'] = '';
        }

        if (!lv['dtc'] && !lv['custom']) {
            json_value.val(null);
        }
        else {
            json_value.val(JSON.stringify(lv));
        }
    });
});
