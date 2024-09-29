class Field {
    render(at) {
        let el = document.createElement('div');
         el.id = at.id;
        el.classList.add(...['document-model-component', 'document-field']);
        return el;
    }
}

export default Field;