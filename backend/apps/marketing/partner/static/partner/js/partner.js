$(document).ready(function () {

    $(".delete-lead-btn").click(function () {
        let tr = $(this).closest('tr');
        let id = tr.data('id');
        let status = 'DL';

        Alert.questionWarning(
            'Jesteś pewien?',
            'Czy na pewno usunąć lead?',
            () => {
                ajaxCall({
                    method: 'post',
                    url: _g.partner.urls.status,
                    data: {id: id, status: status}
                }, () => {
                    tr.remove();
                }, (resp) => {
                    Alert.error('Błąd!', resp.responseJSON.errmsg);
                });
            });
    })
});