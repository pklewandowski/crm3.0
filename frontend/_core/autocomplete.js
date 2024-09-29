const defaultOpts = {
    allowClear: true,
    placeholder: 'Kliknij aby wybrać...',
    theme: 'bootstrap',
    minimumInputLength: 2,
    language: "pl",
    width: '100%'
};

let bundleOpts;

function _setAutocomplete(e, addQuery = null) {
    bundleOpts.ajax = {
        method: 'get',
        url: e.data('autocomplete_url'),
        dataType: 'json',
        delay: 200
    };

    if (addQuery) {
        bundleOpts.ajax.data = function (params) {
            return {
                q: params.term,
                term: params.term,
                addQuery: JSON.stringify(addQuery)
            }
        }
    }
    e.select2(bundleOpts);
}

function _setDefault(e) {
    e.select2({
        allowClear: true,
        theme: 'bootstrap',
        language: "pl",
        placeholder: "Kliknij aby wybrać...",
        width: '100%'
    });
    // temporary - until find out how to set select2 multiple without adding first option automatically after init.
    // s.val(null).trigger("change");
}

function setSelect2(e, autocomplete = false, addQuery = null, opts = null) {
    bundleOpts = Object.assign({}, defaultOpts, opts);
    if (autocomplete) {
        _setAutocomplete(e, addQuery)
    } else {
        _setDefault(e);
    }
}

export {setSelect2};
