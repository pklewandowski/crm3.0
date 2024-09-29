Array.prototype.diff = function (a) {
    return this.filter(function (i) {
        return a.indexOf(i) < 0;
    });
};

let ConditionList = function (el) {
    "use strict";
    this.id = el.data('id');
    this.conditions = null;
    this.selectedConditions = null;
    this.tab = $(`#${attrFormsetTabIdPattern.replace('__ID__', this.id)}`);
    this.template = $('#attr_formset_' + this.id + '_template');
    this.optionRenderTemplate = '<div class="form-group"><label>' +
        '<input type="checkbox" style="display:inline;" ' +
        'class="form-control input-md" __CHECKED__ value="__VALUE__" />__TEXT__</label>' +
        '<div>__DESCRIPTION__</div>' +
        '</div>';

    this._renderOption = function (e, isChecked) {
        return this.optionRenderTemplate
            .replace('__VALUE__', e.val()).replace('__TEXT__', e.text())
            .replace('__CHECKED__', isChecked)
            .replace('__DESCRIPTION__', e.data('description'));
    };

    this._conditionExists = function (value) {
        let exists = false;
        this.selectedConditions.each((i, e) => {
            if (e.val() === value) {
                exists = true;
                return false;
            }
        });
        return exists;
    };

    this.getConditions = function () {
        let node = this.template.prop('content');
        let conditions = [];
        $(node).find(".lov-description option").each(function () {
            conditions.push($(this));
        });
        this.conditions = $(conditions);
    };

    this.getSelectedConditions = function () {
        let conditions = [];
        this.tab.find(".lov-description").each(function (i, e) {
            let delEl = $(this).closest('tr').find('input[name$="DELETE"]');
            if (!delEl.val()) {
                conditions.push($(this));
            }
        });
        this.selectedConditions = $(conditions);
    };

    this.render = function () {
        let options = '';
        this.conditions.each((i, e) => {
            let isChecked = this._conditionExists(e.val()) ? 'checked' : '';
            options += this._renderOption(e, isChecked);
        });
        return options;
    };

    this.init = function () {
        this.getConditions();
        this.getSelectedConditions();
    };

    this.init();
};


let ConditionListModal = function (callback) {
    "use strict";
    this.modal = $("#add_conditions_modal");
    this.conditionListContainer = this.modal.find("#conditionList");
    this.conditionTriggerBtn = this.modal.find("#setConditionsBtn");

    this._initModal = function () {
        this.conditionListContainer.html(null);
        this.conditionTriggerBtn.unbind('click');
        if (typeof callback === 'function')
            this.conditionTriggerBtn.click(callback());
    };

    this.setCallback = function (callback) {
        if (typeof callback === 'function')
            this.conditionTriggerBtn.click(callback());
    };

    this.init = function () {
        this._initModal();
    };

    this.init();
};


let ConditionManager = function (conditionGroup) {
    "use strict";
    this.modal = new ConditionListModal(this.setConditions);
    this.conditionList = new ConditionList(conditionGroup);
    this.conditionGroup = conditionGroup;

    this._fillConditionList = function () {
        this.modal.conditionListContainer.html(this.conditionList.render());
    };

    this.getCheckedConditions = function () {
        let checked = [];
        this.modal.conditionListContainer.find('input:checked').each(function () {
            checked.push($(this).val());
        });
        return checked;
    };

    this._addConditions = function (add) {
        $(add).each((i, e) => {
            let el = this.conditionList.tab.find(`.lov-description option[value="${e}"]:selected`);
            if (el.length) {
                let tr = el.closest('tr');
                tr.find('input[name$="DELETE"]').val(null);
                tr.show();
                return true;
            }

            addRepeatSubsection(this.conditionGroup, this.conditionGroup.data('conditional_name_attribute'), true);

            let tr = this.conditionList.tab.find('tr:last');
            let cList = tr.find('.lov-description');
            let cOpt = cList.find(`option[value="${e}"]`);
            let cDesc = tr.find('.lov-description-target');

            cDesc.val(cOpt.data('description'));
            cOpt.attr('selected', true);
            cList.find('option:not(:selected)').remove();

            this.conditionList.tab.find(".autocomplete").each(function (i1, e1) {
                setAutocomplete($(e1));
            });
            fitTextareaToContent();
        });
    };

    this._deleteConditions = function (del) {
        $(del).each((i, e) => {
            let cOpt = this.conditionList.tab.find(`.lov-description option[value="${e}"]:selected`);
            let tr = cOpt.closest('tr');
            let delEl = tr.find('input[name$="DELETE"]');

            if (delEl.length) {
                delEl.val(1);
                tr.hide();
            } else {
                tr.remove();
            }
        });
    };

    this.setConditions = function () {
        this.conditionList.getSelectedConditions();
        let checked = this.getCheckedConditions();
        let selected = $.map(this.conditionList.selectedConditions, function (x, y) {
            return x.val();
        });

        let add = checked.diff(selected);
        let del = selected.diff(checked);

        this._addConditions(add);
        this._deleteConditions(del);
    };


    this.init = function () {
        this._fillConditionList();
        //
        this.modal.modal.modal();
        // this.modal.setCallback(this.setConditions);
        this.modal.conditionTriggerBtn.click(() => {
            this.setConditions();
        });
    };

    this.init();
};

$(document).ready(function () {

    $('ul[aria-labelledby="repeat_subsection_btn_43"] li a').unbind('click').click(function () {
        new ConditionManager($(this));
    });

    $('ul[aria-labelledby="repeat_subsection_btn_44"] li a').unbind('click').click(function () {
        new ConditionManager($(this));
    });

    $('ul[aria-labelledby="repeat_subsection_btn_46"] li a').unbind('click').click(function () {
        new ConditionManager($(this));
    });

    $('ul[aria-labelledby="repeat_subsection_btn_71"] li a').unbind('click').click(function () {
        new ConditionManager($(this));
    });


    $("#section_43, #section_44, #section_46, #section_71").find('.lov-description option:not(:selected)').remove();

    $(document).on('input', 'input[name$="1_e48dd64d7c9f4b9e93f55590815da6d7"]', function () {
        $(this).val($(this).val().toUpperCase()); //TODO: docelowo uppercase zrobić jako opcję ustawianą przez użytkownika dla atrybutu
    })
});

