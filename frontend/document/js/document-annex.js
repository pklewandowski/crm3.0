import ajaxCall from "../../_core/ajax";

const className = 'DocumentAnnex';

class DocumentAnnex {
    setAnnex() {
        let annex = Input.getByCode('annex');
        let owner = Input.getByCode('owner');

        if (!annex) {
            console.log(`${className}: no annex input`);
            return;
        }

        if (!owner) {
            console.log(`${className}: no owner input`);
            return;
        }
        let clientId = Input.getValue(owner);

        if (!clientId) {
            annex.innerHTML = '';
            annex.setAttribute('disabled', 'true');
            console.log('setAnnex: no clientId');
            return;
        }

        ajaxCall(
            {
                method: 'get',
                url: _g.document.urls.agreementsForAnnexUrl,
                data: {clientId: clientId, documentTypeId: _g.document.type.id, documentId: _g.document.id, mode: _g.mode}
            },
            (resp) => {
                annex.innerHTML = '';

                if (!resp.length) {
                    annex.setAttribute('disabled', 'true');
                    return;
                }
                annex.removeAttribute('disabled');
                //if (_g.mode === 'C') {
                annex.appendChild(new Option('', ''));
                for (let i of resp) {
                    annex.appendChild(new Option(i.text, i.value));
                }
                // } else {
                //  annex.appendChild(new Option(resp[0].text, resp[0].value, true, true));
                // }
            },
            (resp) => {
                console.error(resp.responseJSON.errmsg)
            }
        );
    }
}

export {DocumentAnnex};