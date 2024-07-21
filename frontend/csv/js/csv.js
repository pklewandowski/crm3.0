class Csv {
    constructor(container, processCsvUrl) {
        this.container = jsUtils.setContainer(container);
        this.processCsvUrl = processCsvUrl;
        this.header = this.getHeader();
    }

    getHeader() {
        let header = {};
        for (let i of this.container.querySelectorAll('table thead th')) {
            header[i.dataset['column']] = i.innerText;
        }
        return header;
    }

    processCsv(fileName, validators) {
        ajaxCall({
                method: 'post',
                url: this.processCsvUrl,
                data: {header: JSON.stringify(this.header)}
            },
            (resp) => {
                return resp.data;
            },
            (resp) => {
                jsUtils.LogUtils.log(resp.responseJSON);
                throw new Error(resp);
            });
    }
}

export {Csv};