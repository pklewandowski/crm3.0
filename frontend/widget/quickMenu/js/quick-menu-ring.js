class QuickMenuRing {
    constructor() {
        this.ring = this.render();
    }

    render() {
        return jsUtils.Utils.domElement('div', '', 'widget-quick-menu-ring');
    }
}

export {QuickMenuRing};