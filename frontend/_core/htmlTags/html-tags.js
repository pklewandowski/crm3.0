import HtmlUtils from "../utils/html-utils";

class HtmlTags {
    static th(at, text) {
        let th = jsUtils.Utils.domElement('th');
        th.innerText = HtmlUtils.escapeScriptTag(text);
        if (at?.feature?.width) {
            th.style.width = at.feature.width;
        }
        return th;
    }
}

export {HtmlTags}