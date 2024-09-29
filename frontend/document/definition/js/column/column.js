class Column {
    render(at) {
        let el = document.createElement('div');
         el.id = at.id;
        el.classList.add(...['document-model-component', 'document-column']);
        return el;
    }
}

export default Column;