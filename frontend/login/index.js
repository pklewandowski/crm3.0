import {Login} from "./js/login";

$(document).ready(() => {
    let login = new Login();
    let username = document.getElementById('inputUsername');
    let pResetBtn = document.getElementById('passwordReset');

    pResetBtn.addEventListener('click',(e)=>{
        login.passwordReset(username.value);
    })
});