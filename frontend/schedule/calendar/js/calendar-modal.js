const calendarModal =
<div className="modal-dialog modal-dialog-centered" style="width: 90%;">
    <div className="modal-content">
        <div className="modal-header">
            <button type="button" className="close" data-dismiss="modal">
                <span aria-hidden="true">&times;</span>
                <span className="sr-only">Close</span>
            </button>
            <h4 className="modal-title">Wydarzenie</h4>
        </div>
        <div className="modal-body" style="height: calc(100vh - 120px);">
            <div className="loader-container"></div>
            <div className="calendar-body"></div>
        </div>
    </div>
</div>;

export {calendarModal};