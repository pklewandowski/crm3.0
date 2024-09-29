import {SystemException} from "../../../exception";
import {BaseControl} from "../../base-control";
import {Loader} from 'google-maps';
import Input from "../../../input";

const className = 'GoogleMapControl';

const addressGuide = {
    street_number: 'short_name',
    route: 'long_name',
    locality: 'long_name',
    administrative_area_level_2: 'long_name', //miasto
    administrative_area_level_1: 'long_name', //prowincja, wojewodztwo
    country: 'long_name',
    postal_code: 'short_name'
};

const mapStyles = [
    {
        stylers: [
            // { hue: "#00ffe6" },
            {
                saturation: -20
            }]
    },
    {
        featureType: "road",
        elementType: "geometry",
        stylers: [
            {lightness: 100},
            {visibility: "simplified"}
        ]
    },
    {
        featureType: "road",
        elementType: "labels",
        stylers: [{
            visibility: "off"
        }]
    }
];

class GoogleMapControl extends BaseControl {
    constructor(container, data = null, autoRender = true) {
        super(container, data, autoRender);
        this.map = null;
        this.apiKey = this.getApiKey();
        this.mapStyles = mapStyles;
        this.mapContainer = this.container.querySelector('.eventLocationMap');
        this.marker = null;
        this.autocomplete = null;
        // todo: finally replace it with ./MapAddress object
        this.addressForm = {
            id: this.getByName('eventAddressId'),
            street: this.getByName('eventAddressStreet'),
            street_no: this.getByName('eventAddressStreetNo'),
            apartment_no: this.getByName('eventAddressApartmentNo'),
            post_code: this.getByName('eventAddressZipCode'),
            city: this.getByName('eventAddressCity'),
            country: this.getByName('eventAddressCountry'),
            lat: this.getByName('eventAddressLat'),
            lng: this.getByName('eventAddressLng')
        };

        if (!this.mapContainer) {
            throw new SystemException(`[${className}]: no map container found`);
        }

        this.initMap().then(() => {
            if (autoRender) {
                this.render();
            }
        });

    }

    getApiKey(apiKey) {
        if (apiKey) {
            return apiKey;
        }
        if (!_g?.googleMaps?.apiKey) {
            throw new SystemException('No Google Maps api key provided')
        }
        return _g.googleMaps.apiKey;

    }

    reset() {
        for (let i in Object.keys(this.addressForm)) {
            Input.setValue(this.addressForm[i], null);
        }
        this.removeMarker();
        this.resetAddress();
    }

    async initMap() {
        console.log('initializing google map objects...');

        if (window.intializingGoogleMapAPI || window.googleMapAPI) {
            return;
        }
        window.intializingGoogleMapAPI = true;

        const loader = new Loader(this.apiKey, {libraries: ['places']});
        window.googleMapAPI = await loader.load().then(
            () => {
            },
            () => {
                window.intializingGoogleMapAPI = null;
                window.googleMapAPI = null;
                Alert.error('Google Map API initalization failed');
            }
        );
    }

    setMarker(position, infoWindow = null) {
        this.removeMarker();

        this.marker = new google.maps.Marker({
            map: this.map,
        });
        this.marker.setPosition(position);
        this.marker.setVisible(true);

        if (infoWindow) {
            this.marker.addListener("click", () => {
                infoWindow.open({
                    anchor: this.marker,
                    map: this.map,
                    shouldFocus: false,
                });
            });
        }
    }

    removeMarker() {
        if (this.marker) {
            this.marker.setMap(null);
            this.marker = null;
        }
    }

    render(force = false) {
        if (this.map) {
            if (force) {
                delete this.map;
                this.map = null;
            }
            else {
                return;
            }
        }

        try {
            this.map = new google.maps.Map(this.mapContainer, {
                center: {lat: 52.2372074, lng: 21.012852599999974},
                zoom: 13,
                disableDefaultUI: true
            });

        } catch (err) {
            alert(err);
            if (this.map) {
                delete this.map;
                this.map = null;
            }
            return;
        }

        this.map.setOptions({
            styles: mapStyles
        });

        let card = this.container.querySelector('.pac-card');
        let input = card.querySelector('.pac-input');
        let types = document.getElementById('type-selector');
        let strictBounds = document.getElementById('strict-bounds-selector');

        this.map.controls[google.maps.ControlPosition.TOP_RIGHT].push(card);

        if (input) {
            this.autocomplete = new google.maps.places.Autocomplete(input);

            // Bind the map's bounds (viewport) property to the autocomplete object,
            // so that the autocomplete requests use the current map bounds for the
            // bounds option in the request.
            this.autocomplete.bindTo('bounds', this.map);
        }

        const infoWindow = new google.maps.InfoWindow();
        const infoWindowContent = this.container.querySelector('.infowindow-content');

        if (infoWindowContent) {
            infoWindow.setContent(infoWindowContent);
        }

        let _this = this;
        if (this.autocomplete) {
            this.autocomplete.addListener('place_changed', function () {

                infoWindow.close();
                let place = _this.autocomplete.getPlace();

                if (!place.geometry) {
                    // User entered the name of a Place that was not suggested and
                    // pressed the Enter key, or the Place Details request failed.
                    window.alert("No details available for input: '" + place.name + "'");
                    return;
                }

                // If the place has a geometry, then present it on a map.
                if (place.geometry.viewport) {
                    _this.map.fitBounds(place.geometry.viewport);
                    _this.map.setZoom(13);

                } else {
                    _this.map.setCenter(place.geometry.location);
                    _this.map.setZoom(13);  // Why 17? Because it looks good.

                }


                let address = '';
                if (place.address_components) {
                    _this.fillAddressForm(place, addressGuide, true);

                    address = [
                        (place.address_components[0] && place.address_components[0].short_name || ''),
                        (place.address_components[1] && place.address_components[1].short_name || ''),
                        (place.address_components[2] && place.address_components[2].short_name || '')
                    ].join(' ');
                }

                if (infoWindowContent) {
                    infoWindowContent.style.display = 'block';
                    infoWindowContent.children['place-icon'].src = place.icon;
                    infoWindowContent.children['place-name'].textContent = place.name;
                    infoWindowContent.children['place-address'].textContent = address;
                }

                _this.setMarker(place.geometry.location, infoWindow);
                infoWindow.open(_this.map, _this.marker);
            });
        }


// Sets a listener on a radio button to change the filter type on Places
// Autocomplete.
//function setupClickListener(id, types) {
//    var radioButton = document.getElementById(id);
//    radioButton.addEventListener('click', function () {
//        autocomplete.setTypes(types);
//    });
//}

//setupClickListener('changetype-all', []);
//setupClickListener('changetype-address', ['address']);
//setupClickListener('changetype-establishment', ['establishment']);
//setupClickListener('changetype-geocode', ['geocode']);

//document.getElementById('use-strict-bounds')
//    .addEventListener('click', function () {
//        console.log('Checkbox clicked! New state=' + this.checked);
//        autocomplete.setOptions({strictBounds: this.checked});
//    });
    }

    fillAddressForm(place, guide, addressContainerId) {
        function _resolveUndefined(value) {
            if (!value) {
                return '';
            }
            return value;
        }

        let addressFormContainer = this.container.querySelector('.eventLocationAddress');
        if (!addressFormContainer) {
            Alert.warning('Uwaga!', 'Nie znaleziono formularza adresu');
            return;
        }

        let form = [];

        for (let i = 0; i < place.address_components.length; i++) {
            let addressType = place.address_components[i].types[0];
            if (guide[addressType]) {
                let val = place.address_components[i][guide[addressType]];
                form[addressType] = val;
            }
        }

        form['lat'] = place.geometry.location.lat();
        form['lng'] = place.geometry.location.lng();

        Input.setValue(this.addressForm.street, _resolveUndefined(form['route']));
        Input.setValue(this.addressForm.street_no, _resolveUndefined(form['street_number']));
        Input.setValue(this.addressForm.post_code, _resolveUndefined(form['postal_code']));
        Input.setValue(this.addressForm.city, _resolveUndefined(form['administrative_area_level_2']));
        Input.setValue(this.addressForm.lat, _resolveUndefined(form['lat']));
        Input.setValue(this.addressForm.lng, _resolveUndefined(form['lng']));

        return form;
    }

    getAddress() {
        let _this = this;
        let address = {};

        Object.keys(this.addressForm).map(function (key, index) {
            address[key] = Input.getValue(_this.addressForm[key]);
        });

        return address;
    }

    setAddress(address) {
        if (!address) {
            jsUtils.LogUtils.log(`[${className}]::setAddress: no address param provided.`);
            return;
        }
        let _this = this;
        Object.keys(address).map(key => {
            if (_this.addressForm[key]) {
                Input.setValue(_this.addressForm[key], address[key]);
            }
        });
    }

    resetAddress() {
        let _this = this;
        Object.keys(_this.addressForm).map(key => {
            Input.setValue(_this.addressForm[key], null);
        });
    }
}

export {GoogleMapControl}