import Rules from "./financePack/rules";
import HierarchicalCheckbox from "../../_core/controls/hierarchical-checkbox/hierarchical-checkbox";

let hierarchy = null;

$(document).ready(() => {
    let actionBtn = document.getElementById('addActionBtn');
    let actionRowContainer = document.getElementById('actionRowContainer');
    let rules = new Rules(actionRowContainer);

    actionBtn.addEventListener('click', (e) => {
        let row = document.getElementById('ruleFormsetRowTemplate').innerHTML;
        let idx = document.getElementById('id_action_formset-TOTAL_FORMS');
        row = row.replace(/__prefix__/g, idx.value);
        idx.value = parseInt(idx.value) + 1;
        let tr = document.createElement('tr');
        tr.innerHTML = row;
        actionRowContainer.appendChild(tr);
        rules.sortActionList();
        rules.setFinancialRulesLayout(tr);
        new HierarchicalCheckbox(tr.querySelector('.rule-generate-alert-for'), hierarchy);
    });

    ajaxCall({
            method: 'get',
            url: '/hierarchy/api/',
        },
        (resp) => {
        hierarchy = resp;
            // todo: not optimal. Better solution is to create one instance of hierarchy and attach it to the field when user enter the field
            for (let i of Array.from(actionRowContainer.querySelectorAll('.rule-generate-alert-for'))) {
                new HierarchicalCheckbox(i, hierarchy);
            }
        },
        (resp) => {
            console.error(resp);
        }
    ).then(() => {

    });
});

