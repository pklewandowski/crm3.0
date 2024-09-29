// todo: finally move it to new class handling form processing frontend/Form
import FormValidation from "../../_core/form/form-validaion";

function collectFormData(formContainer) {
    let data = new FormData(formContainer);
    data.append('csrfmiddlewaretoken', _g.csrfmiddlewaretoken);

    ajaxCall({
            url: _g.fileRepository.urls.api,
            method: 'post',
            data: data,
            processData: false,
            contentType: false,
            enctype: 'multipart/form-data',
        },
        (resp) => {
            window.location.reload();
        },
        (resp) => {
            FormValidation.removeErrors(formContainer);
            FormValidation.addErrors(resp.responseJSON.formErrors, 'name')
            console.log(resp);
        }
    )
}

$(document).ready(() => {
    document.getElementById('addNewReportTemplateBtn').addEventListener('click', () => {
        document.querySelector('#reportTemplateFormModal form').reset();
        $('#reportTemplateFormModal').modal();
    });

    document.getElementById('saveReportTemplateBtn').addEventListener('click', () => {
        Alert.question('Czy na pewno zatwierdzić cane?', '', () => {
                collectFormData(document.getElementById('reportTemplateForm'));
            }
        );
    });

    $('.get-report-file').click((e) => {
        let id = e.target.closest('tr').dataset['id'];
        window.location = `${_g.fileRepository.urls.getFile}${id}/`;
    });
})
