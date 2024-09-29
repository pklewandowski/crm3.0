class HeadingComponents {
    static btn(id, icon, opt) {
        let el = document.createElement('div');
        el.id = id;
        el.classList.add('atm-heading-btn');
        el.style.cssFloat = 'left';

        let i = document.createElement('i');
        i.classList.add(...['fas', `fa-${icon}`]);

        el.appendChild(i);

        if (opt) {
            if (opt.onClick && typeof opt.onClick === 'function') {
                el.addEventListener('click', evt => {
                    opt.onClick(evt)
                });
            }
        }

        return el;
    }
}

export default HeadingComponents;