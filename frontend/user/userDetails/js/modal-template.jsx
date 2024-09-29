const modalUserData = <div className="panel panel-default" style="margin-bottom: 15px;">
    <div className="panel-heading">Dane</div>
    <div className="panel-body" style="height: 250px;overflow: auto;">
        <div className="widget-user-details-container">
            <div className="widget-user-details-header">
                {/*<div className="widget-user-details-avatar"></div>*/}
                <div className="widget-user-details-header-data">
                    <div className="widget-user-details-title"></div>
                    <div className="widget-user-details-personal-data"></div>
                </div>
            </div>
            <div style="overflow: auto; width: 100%">
                <div>Produkty</div>
                <div className="widget-user-details-documents-data"></div>
            </div>
        </div>
    </div>
</div>;

const modalEvents = <div className="panel panel-default">
    <div className="panel-heading">Wydarzenia</div>
    <div className="panel-body">
        <div className="widget-user-details-events-container" style="height: calc(100vh - 220px);">
            <div className="widget-user-details-events"></div>
        </div>
    </div>
</div>;

const modalNotes = <div className="panel panel-default note-container" style="height: calc(100vh - 455px);">
    <div id="notesHeading" className="panel-heading" style="position: relative;">
        <div className="add-btn add-note-btn">
            <i className="fa fa-plus-circle"></i>
        </div>
        <div className="panel-title">Notatki</div>
    </div>
    <div id="notes" className="panel-body widget-user-details-list">
        <div className="widget-user-details-notes note-items-container"></div>
    </div>
</div>;

const modalTemplate =
    <div className="modal-dialog modal-dialog-centered" style="width: 90%;">
        <div className="modal-content" style="height: calc(100vh - 60px);">
            <div className="modal-header">
                <button type="button" className="close" data={{dismiss:"modal"}}>
                    <span aria-hidden="true">&times;</span>
                    <span className="sr-only">Close</span>
                </button>
                <h4 className="modal-title">Szczegóły</h4>
            </div>
            <div className="modal-body" style="display: inline-block; width: 100%;">
                <div className="row">
                    <div className="col-lg-6">
                        <div className="row">
                            <div className="col-lg-12">{modalUserData}</div>
                        </div>
                        <div className="row">
                            <div className="col-lg-12">{modalNotes}</div>
                        </div>
                    </div>
                    <div className="col-lg-6 nopadding-left" style="position: relative; height: calc(100vh - 160px);">
                        {modalEvents}
                    </div>
                </div>
            </div>
        </div>
    </div>;

export {modalTemplate};