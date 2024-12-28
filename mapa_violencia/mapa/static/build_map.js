var map = L.map('map', {zoomSnap: 0.1,
                        fullscreenControl: true,
                        fullscreenControlOptions: {
                        position: 'topleft'
                        }}).setView([-30.096859, -51.152677], 10.6);

//Layer
L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

function getData(filtro_bairros, filtro_crimes, date_min, date_max) { 
    return $.ajax({
        type: 'POST',
        url: "return_filters/",
        credentials: "same-origin",
        headers: {
        "X-Requested-With": "XMLHttpRequest",
        "X-CSRFToken": $('input[name="csrfmiddlewaretoken"]').val(),
        },
        data: {'filtro_bairros': filtro_bairros, 'filtro_crimes': filtro_crimes, 
                'date_min': date_min.toISOString(), 'date_max': date_max.toISOString()},
    });    
};

function onEachFeature(feature, layer) {
    layer.on({
        mouseover: highlightFeature,
        mouseout: resetHighlight,
    });
}

function highlightFeature(e) {
    var layer = e.target;

    layer.setStyle({
        weight: 5,
        color: '#666',
        dashArray: '',
        fillOpacity: 0.7
    });

    layer.bringToFront();
    info.update(layer.feature.properties);
}

function resetHighlight(e) {
    geojson.resetStyle(e.target);
    info.update();
}

function concatGeoJSON(g1, g2){
    return { 
        "type" : "FeatureCollection",
        "features": g1.features.concat(g2)
    }
}

function getColor(feature, total_crimes, n_bairros, percapita) {
    if(percapita){
        if (feature.properties.population === 0) {
            return '#e6e6e6';
        }
        var d = feature.properties.n_crimes/feature.properties.population / total_crimes * 10000;
    }
    else{
        var d = feature.properties.n_crimes/total_crimes;
    }
    if(n_bairros > 8){
        var weight = 3/n_bairros;
    }
    else{
        var weight = 1/n_bairros;
    }
    const scale = chroma.scale(['#f2ff5c', '#e81300']).domain([0, weight]); // Define a color scale between two colors

    // console.log(d);

    return scale(d).hex();
}

function style(feature, total_crimes, n_bairros, percapita) {
    return {
        fillColor: getColor(feature, total_crimes, n_bairros, percapita),
        weight: 2,
        opacity: 1,
        color: 'white',
        dashArray: '3',
        fillOpacity: 1
    };
}

var info = L.control();

info.onAdd = function (map) {
    this._div = L.DomUtil.create('div', 'info'); // create a div with a class "info"
    this.update();
    return this._div;
};

// method that we will use to update the control based on feature properties passed
info.update = function (props) {
    try{
        if(props.population === 0){
            var crime_density = 'Sem dados populacionais';
        }
        else{
            var crime_density = Math.floor((props.n_crimes/props.population)*1000).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".")
             + ' crimes/1000 habitantes';
        }}
    catch(err) {}

    this._div.innerHTML =  (props ?
        '<b>' + props.Bairro + '</b><br />' + props.n_crimes.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".") + ' crimes' +
        '</b><br />' + props.population.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".") +
         ' habitantes' + '</b><br />' + crime_density.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".")
        : 'Passe o mouse sobre o bairro');
};

info.addTo(map);

//Get selected neighborhoods

async function create_map(filtro_bairros, filtro_crimes, percapita, date_min, date_max) {
    try {
        var neighborhods = await getData(filtro_bairros, filtro_crimes, date_min, date_max);

        var total_crimes = neighborhods.reduce((accumulator, obj) => accumulator + obj.n_crimes, 0);
        var n_bairros = neighborhods.length;

        var g1 = { "type" : "FeatureCollection",
        "features" : []};

        for (var i = 0; i < neighborhods.length; i++){
            var neighborhod = {"type":"Feature","id":"01","properties":
            {"Bairro": neighborhods[i].Bairro, 'n_crimes': neighborhods[i].n_crimes, 'population': neighborhods[i].population},
            "geometry": neighborhods[i].geometry};
            g1 = concatGeoJSON(g1, neighborhod);

        }

        try {
            map.removeLayer(geojson);
        } catch(err) {}

        geojson = L.geoJSON(g1, {
            onEachFeature: onEachFeature,
            style: function(feature) {
                return style(feature, total_crimes, n_bairros, percapita);
            }
        }).addTo(map);
    
    } catch(err) {
    console.log(err);
    }
}
