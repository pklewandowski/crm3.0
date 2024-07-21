import {SystemException} from "../../../_core/exception";
import {
    INSTALMENT_CAPITAL_SELECTOR,
    INSTALMENT_COMMISSION_SELECTOR,
    INSTALMENT_INTEREST_SELECTOR,
    INSTALMENT_MATURITY_DATE_SELECTOR,
    INSTALMENT_TOTAL_SELECTOR,
    InstalmentSchedule
} from "../../../product/js/financePack/schedule/instalment-schedule";
import DocumentAttributeModel from "../model/document-attribute-model";

const className = 'DocumentAttributeInstalmentSchedule';

class DocumentAttributeInstalmentSchedule extends InstalmentSchedule {
    constructor(section, idDocument, customMapping = null, opts = null) {
        if (!section) {
            throw new SystemException(`[${className}][constructor]: brak zdefiniowanej sekcji harmonogramu`);
        }

        super(section.rowContainer, idDocument, customMapping, opts);

        this.section = section;
    }

    getErrorContainer(){
        return this.section.errorContainer;
    }

    displayErrors(errMsg, reset = true) {
        this.section.displayErrors(errMsg, reset);
    }

    cleanErrors() {
        this.section.cleanErrors();
    }

    reset(rows = 0, callback = null) {
        this.section.reset(rows, callback);
    }

    getRow(idx) {
        return this.section.get(idx);
    }

    getLastRow(idx) {
        return this.section.getLast(idx);
    }

    addRow(data) {
        return this.section.add(data);
    }

    updateRow(idx, data) {
        this.section.update(idx, data);
    }

    _getScheduleItemsIds() {
        let at = DocumentAttributeModel.findAttributeBySelectorClass(INSTALMENT_MATURITY_DATE_SELECTOR.substr(1), this.section.at);
        this.mappingIds['instalment-maturity-date'] = {code: at ? at.id : null, htmlId: at ? `${at.id}__{prefix}__` : null};

        at = DocumentAttributeModel.findAttributeBySelectorClass(INSTALMENT_CAPITAL_SELECTOR.substr(1), this.section.at);
        this.mappingIds['instalment-capital'] = {code: at ? at.id : null, htmlId: at ? `${at.id}__{prefix}__` : null};

        at = DocumentAttributeModel.findAttributeBySelectorClass(INSTALMENT_COMMISSION_SELECTOR.substr(1), this.section.at);
        this.mappingIds['instalment-commission'] = {code: at ? at.id : null, htmlId: at ? `${at.id}__{prefix}__` : null};

        at = DocumentAttributeModel.findAttributeBySelectorClass(INSTALMENT_INTEREST_SELECTOR.substring(1), this.section.at);
        this.mappingIds['instalment-interest'] = {code: at ? at.id : null, htmlId: at ? `${at.id}__{prefix}__` : null}

        at = DocumentAttributeModel.findAttributeBySelectorClass(INSTALMENT_TOTAL_SELECTOR.substring(1), this.section.at);
        this.mappingIds['instalment-total'] = {code: at ? at.id : null, htmlId: at ? `${at.id}__{prefix}__` : null}
    }
}

export {DocumentAttributeInstalmentSchedule};
