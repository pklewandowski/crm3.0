import CompanyNumbersValidator from "../../_core/validators/companyNumbersValidator";
import ajaxCall from "../../_core/ajax";
import Alert from "../../_core/alert";
import DocumentAttachment from "../../document/js/document-attachment";
import DirectoryTree from "../../_core/controls/directory-tree";
import Address from "../../address/js/address";
import {UserRelation} from "./user-relation";
import {TagControl} from "../../_core/controls/tag-control/js/tag-control";
import GUS from "../../company/integration/gus/gus";

$(document).ready(() => {

    // new AvatarControl(document.getElementById('avatarContainer')).render();

    // let test = document.getElementById('avatarTestBtn');
    //
    // test.addEventListener('click', () => {
    //     console.log('test click');
    //     let fd = new FormData();
    //     fd.append('avatarFile', document.getElementById('idAvatar').files[0]);
    //
    //     ajaxCall({
    //             url: '/dummy/',
    //             method: 'post',
    //             data: fd,
    //             processData: false,
    //             contentType: false,
    //         },
    //         (resp) => {
    //         },
    //         (resp) => {
    //         });
    // });


    window.companyNumbersValidator = CompanyNumbersValidator;

    let gusBtn = document.getElementById("getFromGusBtn");

    let userRelationContrainer = document.getElementById('userRelationContainer');

    if (userRelationContrainer) {
        let userRelation = new UserRelation(userRelationContrainer);
        userRelation.getData().then(result => {
            userRelation.render(result)
        });
    }

    if (gusBtn) {
        gusBtn.addEventListener('click', () => {
            // TODO: move to separate class, ie. GusUtils
            let nip = $("#id_user-nip").val();
            nip = nip.replaceAll('-', '');
            if (!companyNumbersValidator.isValidNip(nip)) {
                Alert.error('Błąd', 'Niepoprawny numer NIP');
                return;
            }
            GUS.getData(nip);
        });
    }

    if (_g.mode && _g.mode !== 'C') {
        window.attachment = new DocumentAttachment(_g.document.id, 'attachmentContainer');
        window.directoryTree = new DirectoryTree("atmDirectoryTree", _g.document.id, _g.document.code, {attachment: window.attachment});
    }

    ajaxCall({
            method: 'get',
            url: "/hierarchy/api/",
        },
        (hierarchy) => {
            console.log(hierarchy)
        },
        (resp) => {
            jsUtils.LogUtils.log(resp.responseJSON)
        }
    );

    function sendAgreementRequest() {
        ajaxCall({
                method: "post",
                url: _g.user.urls.agreementRequestUrl,
                data: {userId: _g.user.id}
            },
            (res) => {
                Alert.info('Prośba o zaakceptowanie zgód została zarejestrowana do wysłania klientowi.');
            },
            (resp) => {
                jsUtils.LogUtils.log(resp.responseJSON);
            })
    }

    $(".send-agreement-request-btn").click((e) => {
        // todo: show message filled in template for view before proceeding
        Alert.question('Czy na pewno wysłać prosbę o zaakceptowanie zgód?', "", sendAgreementRequest);
    });

    let address = new Address('addressHistoryModal');

    $('.address-history-btn').click((e) => {
        if (e.target.dataset['id']) {
            address.getHistory(e.target.dataset['id']);
        } else {
            Alert.info('Dla tego typu adresu nie wprowadzono jeszcze żadnych danych')
        }
    });

    new TagControl(document.getElementById('tagList'), document.getElementById('id_user-tags'));

});
