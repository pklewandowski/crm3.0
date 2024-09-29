const userList = (userList) => {
    let users = userList.filter(i => i.id != _g.credentials.user.id).map((v, _) => {
        return <span data={{id: v.id}} className="widget-incoming-events-userList">{v.name}</span>
    });

    return users;
};

const formatEndDate = (startDate, endDate) => {
    if (startDate.date === endDate.date) {
        return <span>{endDate.hour}</span>;
    } else {
        return <span style="font-size: 14px;"><strong>{endDate.date}</strong><span>{endDate.hour}</span></span>;
    }
};

const incomingEventsRow = (startDate, endDate, title, type, invitedUsers = []) => {
    let bgColor = `background-color:${type.color}`;
    return <li className="home-event-container">
        <div className="type-color-dot" style={bgColor}></div>
        <div>
            <span style="font-size: 14px;">
                <strong>{startDate.date}</strong></span>&nbsp;{startDate.hour}&nbsp;-&nbsp;
            {formatEndDate(startDate, endDate)}
        </div>
        <div className="home-event-title">{title}</div>

        <div className="home-event-users">
            {userList(invitedUsers)}
        </div>
    </li>;
};

export {incomingEventsRow};