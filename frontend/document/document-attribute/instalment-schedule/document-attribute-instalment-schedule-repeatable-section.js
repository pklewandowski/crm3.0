import RepeatableTableSection from "../../../document/document-attribute/component/section/repeatable/table/repeatable-table-section";
import {DocumentAttributeInstalmentSchedule} from "./document-attribute-instalment-schedule";

const className = 'DocumentAttributeInstalmentScheduleRepeatableSection';

class DocumentAttributeInstalmentScheduleRepeatableSection extends RepeatableTableSection {
    constructor(at, renderCallback, level, ver = null) {
        super(at, renderCallback, level, ver);

        if (_g?.document?.mode !== 'DEFINITION' || !window.documentDefinitionMode) {
            this.schedule = new DocumentAttributeInstalmentSchedule(this, _g.document.id, at?.feature?.mapping);

            this.panel.toolbar.addButton(`section_${this.at.id}_instalment_schedule`,
                '',
                'fa fa-redo',
                'Generuj harmonogram',
                () => {
                    this.schedule.generate(true, true);
                },
                null);
        }
    }



}

export {DocumentAttributeInstalmentScheduleRepeatableSection}