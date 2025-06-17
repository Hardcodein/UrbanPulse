

const circleToPolygon = require('circle-to-polygon');

const turf = require('turf');

fs = require('fs');

var args = process.argv.slice(2);
var path_string = args[0];
console.log("Output dir:", path_string);

var precision = 3;

function polyMask(mask, bounds) {
  var bboxPoly = turf.bboxPolygon(bounds);
  return turf.difference(bboxPoly, mask);
}

function saveFile(content, filepath) {
    fs.writeFile(filepath, content, function (err) {
        if (err) return console.log(err);
});
}

function floatsToFixed(key, value) {
    if (typeof value === 'number')
        return parseFloat(value.toFixed(precision));
    return value;
}

function prepareCity(name, circleCenter, radius, bounds) {

    let prefix = path_string + "/" + name

    const numberOfEdgesSql = 25;
    const numberOfEdgesMask = 40;

    let polygonSql = circleToPolygon(circleCenter, radius, numberOfEdgesSql);
    let polygonMask = circleToPolygon(circleCenter, radius, numberOfEdgesMask);

    jsonSql = JSON.stringify(polygonSql, floatsToFixed);

    saveFile(jsonSql, prefix + "_borders_for_clipping.geojson");

    jsonForOsmiumExtract = {
          "type": "Feature",
          "properties": {},
          "geometry": polygonSql
        };

    saveFile(JSON.stringify(jsonForOsmiumExtract, floatsToFixed), prefix + "_borders_for_osmium_extract.geojson");

}


let rawdata = fs.readFileSync(path_string + "/implement_cities.json");
let supportedCities = JSON.parse(rawdata);
console.log(supportedCities);

supportedCities["cities"].forEach(function(city) {
    console.log(city);
    console.log("Handling", city["title_en"]);

    center = [city["center"]["lon"], city["center"]["lat"]]

    prepareCity(city["title_en"], center, city["radius_meters"], {});

    console.log("Done handling", city["title_en"]);
});


console.log("Готово.")
