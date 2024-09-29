import {SystemException} from "../../_core/exception";

const className = 'Product';

class Product {
    constructor(id) {
        if (!id) {
            throw new SystemException(`${className}: no product id`)
        }
        this.id = id;
        this.data = null;
    }

    getData() {
        return new Promise((resolve, reject) => ajaxCall(
                {
                    method: 'get',
                    url: '/product/api/',
                    data: {productId: this.id}
                }
            ).then(
                (resp) => {
                    this.data = resp;
                    resolve();
                },

                (resp) => {
                    reject();
                    throw new SystemException(resp);
                }
            )
        )
    }
}

export {Product};