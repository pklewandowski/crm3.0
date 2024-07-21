const calendarEventFormModal = `
<div class="modal-dialog modal-dialog-centered" style="width: 80%;" xmlns="http://www.w3.org/1999/html">
    <div class="modal-content">
        <!-- Modal Header -->
        <div class="modal-header">
            <button type="button" class="close" data-dismiss="modal">
                <span aria-hidden="true">&times;</span>
                <span class="sr-only">Close</span>
            </button>
            <h4 class="modal-title">Szczegóły wydarzenia</h4>
        </div>
        <!-- Modal Body -->
        <div class="modal-body" style="display: inline-block; width: 100%; padding-bottom: 0;">
            <div class="calendar-event-form-body">
                <div class="row">
                    <div class="col-lg-4">
                        <div class="form-group">
                            <select class="form-control input-md eventType"></select>
                            <label for="eventType">Rodzaj wydarzenia</label>
                        </div>
                    </div>
                    <div class="col-lg-8 nopadding-left">
                        <div class="form-group">
                            <input type="text" class="form-control input-md eventTitle"
                            placeholder="Wprowadź tytuł. Domyślny tytuł to rodzaj wydarzenia."/>
                            <label for="eventTitle">Tytuł</label>
                        </div>
                    </div>
                </div>
                <div class="row">
                    <div class="col-lg-4">
                        <div class="row">
                            <div class="col-lg-6">
                                <div class="form-group">
                                     <input type="text" class="form-control input-md datetime-field eventStart" readonly="readonly"/>
                                     <label for="eventStart">Początek</label>
                                </div>
                            </div>
                            <div class="col-lg-6 nopadding-left">
                                <div class="form-group">
                                     <input type="text" class="form-control input-md datetime-field eventEnd" readonly="readonly"/>
                                     <label for="eventEnd">Koniec</label>
                                </div>    
                            </div> 
                            <div class="col-lg-12">
                                <div class="form-group">
                                    <div class="form-control schedule-form-participants eventParticipants">
                                        <div class="eventAddParticipant">
                                            <select class="form-control input-md" data-autocomplete_url="/user/api/get-for-select2/"></select>
                                        </div>
                                        <div class="eventParticipantListContainer">
                                            <ul class="schedule-form-participants-list"></ul>
                                        </div>
                                   </div>
                                    <label for="eventParticipants">Uczestnicy</label>
                                </div>
                            </div>
                            <div class="col-lg-12">
                                <div class="form-group">
                                    <input name="eventIsPrivate" class="form-control input-md eventIsPrivate" type="checkbox"/>
                                    <label for="eventIsPrivate">Wydarzenie prywatne</label>
                                </div>
                            </div>
                            
                        </div>
                    </div> 
                    <div class="col-lg-8 nopadding-left">
                        <div class="row">
                            <div class="col-lg-12">
                                <div class="form-group">
                                    <textarea class="form-control input-md eventDescription"></textarea>
                                    <label for="eventDescription">Opis</label>
                                </div>
                            </div> 
                            <div class="col-lg-12">
                                <div class="form-group">
                                    <div class="form-control schedule-form-location eventLocation">
                                        
                                        <div class="pac-card" style="padding: 10px; width:100%; background: transparent;">
                                            <input class="form-control input-sm pac-input" type="text"
                                                   placeholder="Wyszukaj lokalizację...">
                                        </div>
                                        <div class="infowindow-content" style="display: none;">
                                            <img src="" width="16" height="16" id="place-icon">
                                            <span id="place-name" class="title"></span><br>
                                            <span id="place-address"></span>
                                        </div>
                                        
                                        <div class="row">
                                            <div class="col-lg-4">
                                                <div class="eventLocationAddress">
                                                    <div class="form-group">
                                                        <input name="eventAddressStreet" type="text" class="form-control input-md eventAddressStreet"/>
                                                        <label>Ulica</label>
                                                    </div>
                                                    <div class="form-group">
                                                        <input name="eventAddressStreetNo" type="text" class="form-control input-md eventAddressStreetNo"/>
                                                        <label>Numer</label>
                                                    </div>
                                                    <div class="form-group">
                                                        <input name="eventAddressApartmentNo" type="text" class="form-control input-md eventAddressApartmentNo"/>
                                                        <label>Lokal</label>
                                                    </div>
                                                    <div class="form-group">
                                                        <input name="eventAddressZipCode" type="text" class="form-control input-md eventAddressZipCode"/>
                                                        <label>Kod</label>
                                                    </div>
                                                    <div class="form-group">
                                                        <input name="eventAddressCity" type="text" class="form-control input-md eventAddressCity"/>
                                                        <label>Miejscowość</label>
                                                    </div>
                                                    
                                                    <input name="eventAddressCountry" type="hidden" value="Polska"/>
                                                    <input name="eventAddressLat" type="hidden"/>
                                                    <input name="eventAddressLng" type="hidden"/>
                                                    <input name="eventAddressId" type="hidden"/>
                                                
                                                </div>
                                            </div>
                                            <div class="col-lg-8 nopadding-left">
                                                <div class="eventLocationMap"></div>
                                            </div>
                                        </div>
                                    </div>
                                    <label for="eventLocation">Lokalizacja</label>
                                </div>
                            </div>      
                        </div>
                    </div>
                </div>
                
            </div>
        </div>
        <div class="modal-footer">
            <button class="btn btn-success saveEventBtn" type="button">Zapisz</button>
            <button class="btn btn-danger deleteEventBtn" type="button" style="display:none;">Usuń</button>
            <button type="button" class="btn btn-default" data-dismiss="modal">Zamknij</button>
        </div>
    </div>
</div>
`;

export {calendarEventFormModal}