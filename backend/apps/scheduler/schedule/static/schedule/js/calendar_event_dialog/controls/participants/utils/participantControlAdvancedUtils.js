const ParticipantControlAdvancedUtils = function (opt) {

    let _this = this;

    this.addParticipant = function (id, parentId) {

    }

    this.defaults = {
        participantDataUrl: '/schedule/get-users-for-meeting-filter/'
    };

    this.opt = $.extend({}, this.defaults, opt);

    function _addParticipantToList(id) {

    }

    function _getParticipantSelected(list) {
        let selected = list.jstree(true).get_node(list.jstree(true).get_selected());
        return selected ? selected : null;
    }

    function _getExcluded(list) {
        let l = list.jstree().get_json(list, {flat: true});
        let ids = [];
        for (let i of l) {
            ids.push(parseInt(i.id));
        }
        return JSON.stringify(ids);
    }

    this.participantSelect2 = function (search, list) {
        search.select2({
            theme: 'bootstrap',
            placeholder: "Wpisz nazwisko uczestnika",
            ajax: {
                method: 'post',
                url: _this.opt.participantDataUrl,
                dataType: 'json',
                data: function (params) {
                    return {
                        q: params.term,
                        excluded: _getExcluded(list)
                    };
                },
            },
            minimumInputLength: 2,
            language: "pl",
            width: '100%'
        }).on('select2:select', function (e) {
            let parent = _getParticipantSelected(list);
            if (parent && parent.parent && parent.parent !== '#') {
                Alert.warning('Dodanie nody jest dla tego poziomu niemożliwe')
            } else {
                list.jstree().create_node(parent,
                    {
                        id: e.params.data.id,
                        icon: "fa fa-user", //"glyphicon glyphicon-user", //false,
                        text: e.params.data.text,
                        state: {opened: true}
                    }
                );
                list.jstree().deselect_all();
            }
            search.empty().trigger('change');
        })
    };

    this.participantList = function (search, list) {

        (function ($, undefined) {
            $.jstree.plugins.noclose = function () {
                this.close_node = $.noop;
            };
        })(jQuery);

        list.jstree({
            "core": {
                "check_callback": true,
                "multiple": false
            },
            "plugins": ["noclose", "contextmenu"],
            "contextmenu": {
                "items": function (node) {
                    return {
                        "remove": {
                            "label": "Usuń",
                            "action": function (obj) {

                                Alert.questionWarning(
                                    "Czy na pewno usunąć uczestnika?",
                                    '',
                                    () => {
                                        list.jstree().delete_node(node);
                                    });
                            }
                        }
                    }
                }
            }
        }).on('changed.jstree', function (e, data) {
            if (data.node) {
                $("#selectedParticipantInfo").text(`Powiązanie: ${data.node.text}-(kliknij aby usunąć)`);
            } else {
                $("#selectedParticipantInfo").text(null);
            }
            if (data.node && data.node.parent !== '#') {
                search.prop('disabled', true);
                $("#add_user_btn").attr('disabled', true).prop('disabled', true);
            } else {
                search.prop('disabled', false);
                $("#add_user_btn").attr('disabled', false).prop('disabled', false);
            }
        });
    }
};

export default ParticipantControlAdvancedUtils;