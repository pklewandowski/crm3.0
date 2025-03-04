function fillAnnexList() {
    let annex = Input.getByCode('annex');
    let clientId = Input.getValue(Input.getByCode('owner'));
    if (!clientId) {
        return;
    }
    ajaxCall(
        {
            method: 'get',
            url: '/document/api/get-for-annex/',
            data: {
                documentTypeId: _g.document.type.id,
                clientId: clientId
            }
        },
        (resp) => {
            annex.innerHTML = null;
            annex.appendChild(new Option('----', ''));
            for (let item of resp) {
                let opt = new Option(item.text, item.value);
                annex.appendChild(opt);
            }
        }
    );
}