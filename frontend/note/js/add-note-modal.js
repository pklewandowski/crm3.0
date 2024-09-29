const addNoteModal = `
<div class="modal-dialog modal-dialog-centered" style="width: 50%">
    <div class="modal-content">
        <!-- Modal Header -->
        <div class="modal-header">
            <button type="button" class="close"
                    data-dismiss="modal">
                <span aria-hidden="true">&times;</span>
                <span class="sr-only">Close</span>
            </button>
            <h4 class="modal-title">Nowa notatka</h4>
        </div>
        <!-- Modal Body -->
        <div class="modal-body" style="display: inline-block; width: 100%;">
            <div class="note-text">
                <textarea class="form-control" style="min-height: 250px;"></textarea>
            </div>
        </div>
        <div class="modal-footer">
            <button id="saveNoteBtn" class="btn btn-success" type="button" data-dismiss="modal">Zapisz</button>
            <button type="button" class="btn btn-default" data-dismiss="modal">Zamknij</button>
        </div>
    </div>
</div>
`;

export {addNoteModal};