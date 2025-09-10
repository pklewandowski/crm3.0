import {SystemException} from "../../../../../_core/exception";

const className = 'RepeatableSectionBase';

class RepeatableSectionBase {
    constructor(at, renderCallback, level, ver = null) {
        this.at = at;
        this.renderCallback = renderCallback;
        this.level = level;
        this.ver = ver;
        this.at = at;
        this.cl = jsUtils.Utils.domElement('div', at.id, 'repeatable-section-panel');

        // add actions for repeatable section
        if (this.at?.feature?.actions) {
                // change action
                if (this.at.feature.actions.change) {
                    this.cl.addEventListener('change', (e) => {
                        eval(this.at.feature.actions.change.fn)(e);
                    });
                }
            }

        // if (this.at?.feature?.allow_fullscreen) {
        //     let fullscreen = jsUtils.Utils.domElement('div', null, 'fullscreen-button')
        //     let fullscreen_icon = jsUtils.Utils.domElement('i', null, ["fas", "fa-expand-arrows-alt"])
        //     fullscreen.appendChild(fullscreen_icon);
        //
        //     fullscreen_icon.addEventListener('click', () => {
        //         this.cl.requestFullscreen();
        //     })
        //     this.cl.appendChild(fullscreen);
        // }
    }

    _isEditable() {
        if (!this.ver){
            return true;
        }
        return this.ver[this.at.id] ? this.ver[this.at.id].e : true;
    }

    readonly() {
        return !this._isEditable() || this.at?.feature?.readonly; // || !this.at?.feature?.predefined?.allowCustom;
    }

    getTabLength() {
        return this.rowHeader.querySelectorAll('.repeatable-section-tabs .tab-pane').length;
    }

    reset() {
        jsUtils.LogUtils.log(`[${className}][reset()]: function not implemented`);
    }

    static idx(el, regexp = new RegExp(/\d+__(\d+)__/)) {

        let idx = el.id.match(regexp);
        if (idx){
            return parseInt(idx[1]);
        }
        return null;
    }

    get(idx) {}

    add() {}

    update(){}

    delete() {}
}

export default RepeatableSectionBase;