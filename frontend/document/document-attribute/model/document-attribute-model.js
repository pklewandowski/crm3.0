import {SystemException} from "../../../_core/exception";

class DocumentAttributeModel {
    constructor(documentType, documentStatus = null, cache = true) {
        this.documentType = documentType;
        this.documentStatus = documentStatus;
        this.model = null;
        // VisibleEditableRequired - ver
        this.ver = null;
        this.className = 'DocumentAttributeModel';
        this.cache = cache;
        this.init();
    }

    getModel() {
        let setModel = data => {
            this.model = data.model;
            this.ver = data.ver;
            return true;
        };

        return new Promise((resolve, reject) => {
                ajaxCall({
                        method: 'get',
                        url: '/document/api/attribute/model',
                        data: {
                            cache: this.cache,
                            documentType: this.documentType,
                            documentStatus: this.documentStatus
                        }
                    },
                    (resp) => {
                        resolve(setModel(resp));
                    },
                    (resp) => {
                        reject(() => {
                            console.log(resp.responseJSON);
                        });
                    }
                )
            }
        )
    }

    findSectionModel(sectionId, raiseError = true) {
        let section = null;
        this.model.forEach(e => {
            if (e.id == sectionId) {
                section = e;
                return false;
            }
        });

        if (raiseError && !section) {
            throw new SystemException(`[${this.className}][findSectionModel]: Section model not found!`);
        }
        return section;
    }


    static findAttributeById(id, currentNode) {
        let attribute = null;
        (function f(node) {
            if (attribute) {
                return;
            }
            node.forEach(e => {
                if (e.id == id) {
                    attribute = e;
                } else if (e.children) {
                    f(e.children);
                }
            })
        })(Array.isArray(currentNode) ? currentNode : [currentNode]);

        return attribute;
    }

    static findAttributeBySelectorClass(selector_class, currentNode) {
        let attribute = null;

        (function f(node) {
            if (attribute) {
                return;
            }
            node.forEach(e => {
                if (e.selector_class === selector_class) {
                    attribute = e;
                } else if (e.children) {
                    f(e.children);
                }
            })
        })(Array.isArray(currentNode) ? currentNode : [currentNode]);

        return attribute;
    }

    static findAttributeByCode(code, currentNode) {
        let attribute = null;
        (function f(node) {
            if (attribute) {
                return;
            }
            node.forEach(e => {
                if (e.code == code) {
                    attribute = e;
                } else if (e.children) {
                    f(e.children);
                }
            })
        })(Array.isArray(currentNode) ? currentNode : [currentNode]);

        return attribute;
    }


    init() {
    }
}

export default DocumentAttributeModel;
