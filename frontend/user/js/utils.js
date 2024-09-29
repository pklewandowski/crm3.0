function getPersonalTitle(data) {
    return `${data.first_name ? data.first_name : ''} ${data.last_name ? data.last_name : ''} ${data.company_name ? data.company_name : ''}`;
}

export {getPersonalTitle};