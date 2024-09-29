import {UserDetails} from "../../userDetails/js/user-details";

$(document).ready(() => {
    let userDetails = new UserDetails(_g.currentContacts.urls.userDetailsUrl);

    document.querySelector('.current-contacts-table tbody').addEventListener('click', (evt) => {
            let e = evt.target;
            // if (e.classList.contains('widget-user-details')) {
                userDetails.render(e.closest('tr').dataset['id']);
           // }
        });
});