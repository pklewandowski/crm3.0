import ParticipantControlAdvancedUtils from './utils/participantControlAdvancedUtils.js'

const ParticipantControlAdvanced = function (containerId, opt) {

        let _this = this;

        this.container = $(`#${containerId}`);

        this.defaults = {
            participantSearch: $('#participantSearchControl'),
            participantList: $('#participantListControl'),
            participantListControls: {
                clear: $("#clearAllParticipants")
            }
        };

        this.opt = $.extend({}, this.defaults, opt);
        this.utils = new ParticipantControlAdvancedUtils();

        this.participant = {
            add: function (id, parentId) {

            },

            confirm: function (id) {

            },

            delete: function (id) {

            },

            getList: function () {
                let l = _this.opt.participantList.jstree().get_json(_this.opt.participantList, {flat: true});
                let p = [];
                for (let i of l) {
                    p.push({id: i.id, parent: i.parent === "#" ? '' : i.parent})
                }
                return p;
            },

            load: function (e) {
                let slaveNode = [];

                for (let i of e) {
                    if (i.parent) {
                        slaveNode.push(i);
                    } else {
                        let node = {
                            id: i.id,
                            icon: "fa fa-user", //"glyphicon glyphicon-user", //false,
                            text: i.text,
                            state: {opened: true}
                        };
                        _this.opt.participantList.jstree().create_node("#", node)
                    }
                }

                for (let i of slaveNode) {
                    let node = {
                        id: i.id,
                        icon: "fa fa-user", //"glyphicon glyphicon-user", //false,
                        text: i.text,
                        state: {opened: true}
                    };
                    _this.opt.participantList.jstree().create_node(i.parent, node)
                }
            }
        };

        this.init = function () {
            this.utils.participantSelect2(this.opt.participantSearch, this.opt.participantList);
            this.utils.participantList(this.opt.participantSearch, this.opt.participantList);
            $("#selectedParticipantInfo").click(function () {
                _this.opt.participantList.jstree().deselect_all();
            });
        };

        this.init();
    }
;

export default ParticipantControlAdvanced;