const map = L.map("map").setView([51.505, -0.09], 13);

L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  attribution:
    'Map data © <a href="<URL>StreetMap</a> contributors',
}).addTo(map);

let selectingArea = false;
let startPoint = null;
let endPoint = null;
let rectangle = null;

document.getElementById("select-area").addEventListener("click", () => {
  selectingArea = true;
});

const markers = L.markerClusterGroup();
map.addLayer(markers);

const icons = {};

function getIcon(value) {
  if (!icons[value]) {
    icons[value] = L.icon({
      // Get Sign-.sgv from github.
      // Some signs don't have an .svg, works anyway.
      iconUrl: `https://raw.githubusercontent.com/mapillary/mapillary_sprite_source/master/package_signs/${value}.svg`, 
      iconSize: [38, 38],
      iconAnchor: [22, 22],
      popupAnchor: [-3, -76],
    });
  }
  return icons[value];
}

let source = null;

document.getElementById("get-data").addEventListener("click", () => {
  const minLon = document.getElementById("min-lon").value;
  const minLat = document.getElementById("min-lat").value;
  const maxLon = document.getElementById("max-lon").value;
  const maxLat = document.getElementById("max-lat").value;
  const apiKey = document.getElementById("api-key").value;

  const params = new URLSearchParams({
    minLon,
    minLat,
    maxLon,
    maxLat,
    apiKey,
  });

  source = new EventSource(
    `http://localhost:5000/get-status?${params.toString()}` // Calls Flask development server.
  );

  source.onmessage = (event) => {
    console.log(event.data);
    if (event.data === "Done!") {
      source.close();
      fetch(`http://localhost:5000/get-data`) // Calls Flask development server.
        .then((response) => {
          if (!response.ok) {
            throw new Error(`An error occurred: ${response.statusText}`);
          }
          return response.json();
        })
        .then((data) => {
          // Display points on map
          data.features.forEach((feature) => {
            const [lon, lat] = feature.coordinates;
            const value = feature.value;
            markers.addLayer(L.marker([lat, lon], { icon: getIcon(value) }));
          });

          // Download JSON data
          const blob = new Blob([JSON.stringify(data)], { type: "application/json" });
          const url = window.URL.createObjectURL(blob);
          const a = document.createElement("a");
          a.href = url;
          a.download = "data.json";
          document.body.appendChild(a);
          a.click();
          a.remove();
        })
        .catch((error) => {
          console.error(error);
        });
    }
  };
});
map.on("click", (e) => {
  // Selecting the box by clicking.
  if (selectingArea) {
    if (!startPoint) {
      startPoint = e.latlng;
    } else {
      endPoint = e.latlng;
      selectingArea = false;

      document.getElementById("min-lon").value = startPoint.lng;
      document.getElementById("min-lat").value = startPoint.lat;
      document.getElementById("max-lon").value = endPoint.lng;
      document.getElementById("max-lat").value = endPoint.lat;

      if (rectangle) {
        map.removeLayer(rectangle);
      }

      rectangle = L.rectangle([startPoint, endPoint], { color: "#ff7800", weight: 1 });
      rectangle.addTo(map);

      startPoint = null;
      endPoint = null;
    }
  }
});

map.on("mousemove", (e) => {
  // Box Preview.
  if (selectingArea && startPoint) {
    if (rectangle) {
      map.removeLayer(rectangle);
    }

    rectangle = L.rectangle([startPoint, e.latlng], { color: "#ff7800", weight: 1 });
    rectangle.addTo(map);
  }
});
