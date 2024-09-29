class Modal {
    static getTemplate(modalId, title, buttons = null) {
        let modal = jsUtils.Utils.domElement('div', modalId, ['modal', 'fade']);
        modal.setAttribute('tabindex', '-1');
        modal.setAttribute('role', 'dialog');
        modal.setAttribute('aria-labelledby', '');
        modal.setAttribute('aria-hidden', true);

        modal.innerHTML =
            `<div class="modal-dialog" style="width: 70%">
                <div class="modal-content">
                
                    <div class="modal-header">
                        <button type="button" class="close" data-dismiss="modal">
                            <span aria-hidden="true">&times;</span>
                            <span class="sr-only">Close</span>
                        </button>
                        <h4 class="modal-title">${title}</h4>
                    </div>
                    
                    <div class="modal-body"></div>  
                                                        
                    <div class="modal-footer">
                        <button type="button" class="btn btn-primary saveBtn">Zapisz</button>
                        <button type="button" class="btn btn-default" data-dismiss="modal">Zamknij</button>
                    </div>
                </div>
            </div>`;

        return modal;
    }
}

export {Modal};