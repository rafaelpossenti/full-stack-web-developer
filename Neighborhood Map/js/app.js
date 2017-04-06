var map;
var defaultIcon;
var highlightedIcon;


function googleError() {
    $('#query-summary').text("Could not load Google Maps");
    $('#list').hide();
}


//function to initialize map
function initMap() {
    "use strict";

    map = new google.maps.Map(document.getElementById('map'), {
        center: {lat:  -25.431196, lng: -49.271958},
        zoom: 13,
        mapTypeControl: false
    });
    ko.applyBindings(new AppViewModel());
}


String.prototype.contains = function (other) {
    return this.indexOf(other) !== -1;
};


//Knockout's View Model
var AppViewModel = function () {
    var self = this;

    function initialize() {
        fetchparks();
    }

    if (typeof google !== 'object' || typeof google.maps !== 'object') {
    } else {
        defaultIcon = makeMarkerIcon('00FF00');
        highlightedIcon = makeMarkerIcon('F6FF00');
        var infoWindow = new google.maps.InfoWindow();
        google.maps.event.addDomListener(window, 'load', initialize);
    }
    self.parkList = ko.observableArray([]);
    self.query = ko.observable('');
    self.queryResult = ko.observable('');

    self.search = function () {
        //To prevent reload of page on click search button
    };


    //List of park's after filter based on query added in search
    self.FilteredparkList = ko.computed(function () {
        self.parkList().forEach(function (park) {
            park.marker.setMap(null);
        });

        var results = ko.utils.arrayFilter(self.parkList(), function (park) {
            return park.name().toLowerCase().contains(self.query().toLowerCase());
        });

        results.forEach(function (park) {
            park.marker.setMap(map);
        });

        return results;
    });


    //function called when a park is clicked from the filtered list
    self.selectpark = function (park) {
        infoWindow.setContent(park.formattedInfoWindowData());
        infoWindow.open(map, park.marker);
        map.panTo(park.marker.position);
        park.marker.setAnimation(google.maps.Animation.BOUNCE);
        park.marker.setIcon(highlightedIcon);
        self.parkList().forEach(function (unselected_park) {
            if (park != unselected_park) {
                unselected_park.marker.setAnimation(null);
                unselected_park.marker.setIcon(defaultIcon);
            }
        });
    };


    //function to fetch parks in Curitiba
    function fetchparks() {
        var data;

        $.ajax({
            url: 'https://api.foursquare.com/v2/venues/search',
            dataType: 'json',
            data: 'client_id=ZY4CDJNSF1SWOWSP1AYCW3WKA5CEAUR1YBRCRE4LTGNQN5ZG&client_secret=OBRHMM00CX5DGDRTKTMMEDST1U00PA33UCQXMD0HBMCQQCAC&v=20130815%20&ll=-25.431196,-49.271958%20&query=park',
            async: true,
        }).done(function (response) {
            data = response.response.venues;
            data.forEach(function (park) {
                foursquare = new Foursquare(park, map);
                self.parkList.push(foursquare);
            });
            self.parkList().forEach(function (park) {
                if (park.map_location()) {
                    google.maps.event.addListener(park.marker, 'click', function () {
                        self.selectpark(park);
                    });
                }
            });
        }).fail(function (response, status, error) {
            $('#query-summary').text('park\'s could not load...');
        });
    }
};


//function to make default and highlighted marker icon
function makeMarkerIcon(markerColor) {
    var markerImage = new google.maps.MarkerImage(
        'http://chart.googleapis.com/chart?chst=d_map_spin&chld=1.15|0|' + markerColor +
        '|40|_|%E2%80%A2',
        new google.maps.Size(25, 37),
        new google.maps.Point(0, 0),
        new google.maps.Point(10, 34),
        new google.maps.Size(25, 37));
    return markerImage;
}


//Foursquare model
var Foursquare = function (park, map) {
    var self = this;
    self.name = ko.observable(park.name);
    self.location = park.location;
    self.lat = self.location.lat;
    self.lng = self.location.lng;
    //map_location returns a computed observable of latitude and longitude
    self.map_location = ko.computed(function () {
        if (self.lat === 0 || self.lon === 0) {
            return null;
        } else {
            return new google.maps.LatLng(self.lat, self.lng);
        }
    });
    self.formattedAddress = ko.observable(self.location.formattedAddress);
    self.formattedPhone = ko.observable(park.contact.formattedPhone);
    self.marker = (function (park) {
        var marker;

        if (park.map_location()) {
            marker = new google.maps.Marker({
                position: park.map_location(),
                map: map,
                icon: defaultIcon
            });
        }
        return marker;
    })(self);
    self.id = ko.observable(park.id);
    self.url = ko.observable(park.url);
    self.formattedInfoWindowData = function () {
        return '<div class="info-window-content">' + '<a href="' +
               (self.url()===undefined?'/':self.url()) + '">' +
               '<span class="info-window-header"><h4>' +
               (self.name()===undefined?'park name not available':self.name()) + '</h4></span>' +
               '</a><h6>' +
               (self.formattedAddress()===undefined?'No address available':self.formattedAddress()) +
               '<br>' + (self.formattedPhone()===undefined?'No Contact Info':self.formattedPhone()) +
               '</h6>' + '</div>';
    };
};

