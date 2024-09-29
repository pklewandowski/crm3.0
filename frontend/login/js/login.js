import Alert from "../../_core/alert";
import ajaxCall from "../../_core/ajax";

class Login {
    passwordReset(username) {
        if (!username) {
            Alert.warning('Wprowadź poprawny login, PESEL, NIP, lub adres e-mail');
            return;
        }

        let callback = (username) => {
            $(".loader-container").fadeIn();
            ajaxCall({
                    method: 'post',
                    url: '/user/api/reset-password/',
                    data: {username: username}
                },
                (resp) => {
                    if (resp?.email === 'OK') {
                        Alert.info('Pomyślnie zresetowano hasło', 'Nowe hasło inicjalne zostało wysłane na Twój adres e-mail zarejestrowany w systemie.');
                        return;
                    }
                    if (resp.password) {
                        Alert.info('Pomyślnie zresetowano hasło', `Ze względu na to, że nie posiadasz adresu e-mail w systemie, nie zostało ono wysłane. 
Twoje hasło inicjalne to: <strong>${resp.password}</strong>`);
                        return;
                    }
                    Alert.error('Błąd', 'Pomyślnie zresetowano hasło, jednakże system nie przekazał go do użytkownika!');
                },
                (resp) => {
                    let _resp = resp.responseJSON;
                    Alert.error('Błąd', _resp.errmsg);
                    jsUtils.LogUtils.log(_resp);
                },
                () => {
                    $(".loader-container").fadeOut();
                }
            )
        };

        Alert.questionWarning('Czy na pewno zresetować hasło?',
            'Hasło zostanie zresetowane do hasła inicjalnego. Nowe hasło zostanie przesłane na Twój adres e-mail zarejestrowany w systemie', callback, username);
    }
}

export {Login};