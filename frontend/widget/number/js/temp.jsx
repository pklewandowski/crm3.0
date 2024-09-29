function tempJsx() {
    const listItems = [1,2,3,4].map((x, i) =>
        <li className="xxx">Li1</li>
    );

    return <div className="alamakota">
        <span>Temp</span>
        <ul>{listItems}</ul>
    </div>
}

export {tempJsx}