import '../scss/paginator.scss';

class Paginator {
    constructor(container = null) {
        this.container = container;
        this.pages = 1;
        this.currentPage = 1;
        this.rowsPerPage = 20;
    }

    setCurrentPage(pageNum) {
        this.currentPage = pageNum;
        this.update();
    }

    render() {

    }

    update() {

    }

}

export {Paginator};