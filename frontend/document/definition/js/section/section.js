class Section {

    render(at) {
        let el = document.createElement('div');
        el.id = at.id;
        el.classList.add(...['document-model-component', 'document-section']);
        return el;
    }
}

export default Section;