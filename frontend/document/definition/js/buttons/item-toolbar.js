class ItemToolbar {

    static handleBtn(type = 'X', icon) {
        let btn = document.createElement('div');
        btn.tabIndex = '0';
        btn.classList.add(...['item-btn', 'handle']);
        let btnIcon = document.createElement('i');
        btnIcon.tabIndex = '0';
        btnIcon.classList.add(...['fa', 'handle-icon', icon]);
        switch (type) {
            case 'V':
                btnIcon.classList.add('fa-arrows-v');
                break;
            case 'H':
                btnIcon.classList.add('fa-arrows-h');
                break;
            default:
                btnIcon.classList.add('fa-arrows');
                break;
        }

        btn.appendChild(btnIcon);
        return btn;
    }

    static removeBtn(icon = 'remove-icon') {
        let btn = document.createElement('div');
        btn.tabIndex = '0';
        btn.classList.add(...['item-btn', 'remove']);
        let btnIcon = document.createElement('i');
        btnIcon.classList.add(...['fa', 'fa-times', icon ? icon: '']);
        btn.appendChild(btnIcon);
        return btn;
    }

    static editBtn(icon = 'edit-icon') {
        let btn = document.createElement('div');
        btn.tabIndex = '0';
        btn.classList.add(...['item-btn', 'edit']);
        let btnIcon = document.createElement('i');
        btnIcon.classList.add(...['fa', 'fa-pencil', icon]);
        btn.appendChild(btnIcon);
        return btn;
    }

    static render(el, opt) {

        if (el && el.getElementsByClassName('item-btn-container')[0]) {
            return;
        }
        if (!opt) {
            return;
        }

        let container = document.createElement('div');
        container.classList.add(...['item-btn-container']);

        if (opt.handle) {
            container.appendChild(ItemToolbar.handleBtn(opt.handle.type, opt.icon));
        }


        if (opt.remove) {
            container.appendChild(ItemToolbar.removeBtn());
        }
        if (opt.edit) {
            container.appendChild(ItemToolbar.editBtn());
        }

        if (el) {
            el.appendChild(container);
        }

        return container;
    }
}

export default ItemToolbar;