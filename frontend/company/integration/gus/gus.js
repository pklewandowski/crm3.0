import ajaxCall from "../../../_core/ajax";
import StringUtils from "../../../_core/utils/string-utils";
import Alert from "../../../_core/alert";

class GUS {
    static getData(nip) {
        ajaxCall(
            {
                method: 'get',
                url: _g.user.urls.gusApi,
                data: {nip: nip}
            },
            (res) => {
                //todoL  trow away outside
                let isCompany = document.getElementById('id_user-is_company');
                isCompany.checked = true;
                isCompany.dispatchEvent(new Event('change'));

                let typePrefix = '';
                switch (res.Typ) {
                    case 'F':
                        typePrefix = 'fiz';
                        break;
                    case 'P':
                        typePrefix = 'praw';
                        break;
                    default:
                        return {}
                }

                // Move to populateForm separate function outside this package
                $("#id_user-company_name").val(res.Nazwa);
                $("#id_user-email").val(res.Typ == 'F' ? res.detailed.fizC_adresEmail : res.detailed.praw_adresEmail);

                $("#id_user-first_name").val(res.Typ === 'F' ? StringUtils.initCap(res.detailed.fiz_imie1) : '');
                $("#id_user-second_name").val(res.Typ === 'F' ? StringUtils.initCap(res.detailed.fiz_imie2) : '');
                $("#id_user-last_name").val(res.Typ === 'F' ? StringUtils.initCap(res.detailed.fiz_nazwisko) : '');

                $("#id_user-company_establish_date").val(res.detailed[`${typePrefix}_dataPowstania`]);
                $("#id_user-krs").val(res.Typ === 'P' ? res.detailed.praw_numerWrejestrzeEwidencji : '');
                $("#id_user-phone_one").val(res.Typ === 'F' ? res.detailed.fizC_numerTelefonu : res.detailed.praw_numerTelefonu);

                $("#id_user-company_establish_date").val(res.detailed[`${typePrefix}_dataPowstania`]);

                $("#id_companyaddress-street").val(res.Ulica);
                $("#id_companyaddress-street_no").val(res.detailed[`${typePrefix}_adSiedzNumerNieruchomosci`]);
                $("#id_companyaddress-apartment_no").val(res.detailed[`${typePrefix}_adSiedzNumerLokalu`]);
                $("#id_companyaddress-post_code").val(res.KodPocztowy);
                $("#id_companyaddress-city").val(StringUtils.initCap(res.Miejscowosc));
                $("#id_companyaddress-country").val('Polska'); //StringUtils.initCap(res.detailed.fiz_adSiedzKraj_Nazwa));

                $("#id_user-nip").val(nip);
                $("#id_user-regon").val(res.Regon);

            },
            (res) => {
                Alert.error('Błąd', res.responseJSON.errmsg);
                jsUtils.LogUtils.log(res.responseJSON.errmsg, res.responseJSON.traceback)
            }
        )

    }
}

export default GUS;