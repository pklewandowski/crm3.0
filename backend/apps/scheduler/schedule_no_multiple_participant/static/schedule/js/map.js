var map;
var addressGuide = {
    street_number: 'short_name',
    route: 'long_name',
    locality: 'long_name',
    administrative_area_level_2: 'short_name', //miasto
    administrative_area_level_1: 'short_name', //prowincja, wojewodztwo
    country: 'long_name',
    postal_code: 'short_name'
};


var map_styles = [{
    stylers: [
        // { hue: "#00ffe6" },
        {
            saturation: -20
        }]
}, {
    featureType: "road",
    elementType: "geometry",
    stylers: [{
        lightness: 100
    }, {
        visibility: "simplified"
    }]
}, {
    featureType: "road",
    elementType: "labels",
    stylers: [{
        visibility: "off"
    }]
}];


function getPositionFromId(placeId, form) {

    var geocoder = new google.maps.Geocoder;

    geocoder.geocode({'placeId': placeId}, function (results, status) {
        if (status === 'OK') {
            if (results[0]) {

                var latlng = [];
                latlng['lat'] = results[0].geometry.location.lat();
                latlng['lng'] = results[0].geometry.location.lng();

                console.log(latlng);
                return latlng;

            }
        }
    });
}

function initMap() {
    if (map) {
        delete map;
    }

    try {

        map = new google.maps.Map(document.getElementById('map'), {
            center: {lat: 52.2372074, lng: 21.012852599999974},
            zoom: 13,
            disableDefaultUI: true
        });

    } catch (err) {
        map = null;
        return;
    }

    map.setOptions({
        styles: map_styles
    });
    var card = document.getElementById('pac-card');
    var input = document.getElementById('pac-input');
    var types = document.getElementById('type-selector');
    var strictBounds = document.getElementById('strict-bounds-selector');

    map.controls[google.maps.ControlPosition.TOP_RIGHT].push(card);

    var autocomplete = new google.maps.places.Autocomplete(input);

// Bind the map's bounds (viewport) property to the autocomplete object,
// so that the autocomplete requests use the current map bounds for the
// bounds option in the request.
    autocomplete.bindTo('bounds', map);

    var infowindow = new google.maps.InfoWindow();
    var infowindowContent = document.getElementById('infowindow-content');
    infowindow.setContent(infowindowContent);
    var marker = new google.maps.Marker({
        map: map,
        anchorPoint: new google.maps.Point(0, -29)
    });

    autocomplete.addListener('place_changed', function () {

        infowindow.close();

        marker.setVisible(false);

        var place = autocomplete.getPlace();

        console.log(place);

        if (!place.geometry) {
            // User entered the name of a Place that was not suggested and
            // pressed the Enter key, or the Place Details request failed.
            window.alert("No details available for input: '" + place.name + "'");
            return;
        }

        // If the place has a geometry, then present it on a map.
        if (place.geometry.viewport) {
            map.fitBounds(place.geometry.viewport);
            map.setZoom(13);
        } else {
            map.setCenter(place.geometry.location);
            map.setZoom(13);  // Why 17? Because it looks good.
        }
        marker.setPosition(place.geometry.location);
        marker.setVisible(true);

        var address = '';
        if (place.address_components) {

            fillAddressForm(place, addressGuide, true);

            address = [
                (place.address_components[0] && place.address_components[0].short_name || ''),
                (place.address_components[1] && place.address_components[1].short_name || ''),
                (place.address_components[2] && place.address_components[2].short_name || '')
            ].join(' ');
        }

        infowindowContent.children['place-icon'].src = place.icon;
        infowindowContent.children['place-name'].textContent = place.name;
        infowindowContent.children['place-address'].textContent = address;
        infowindow.open(map, marker);
    });

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
