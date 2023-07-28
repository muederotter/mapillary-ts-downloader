import requests, math
from vt2geojson.tools import vt_bytes_to_geojson

class ts_data:
    def __init__(self, access_token:str, bbox:list) -> None:
        """
        :param access_token: API Key from Mapillary.
        :param bbox: Boundary Box [min Longitude, min Latitude, max Longitude, max Latitude]
        """
        self.access_token = access_token
        self.z = 14 # Standard Value for zoom

        self.llx,self.lly = self.deg2num(bbox[1],bbox[0],self.z) # Lower Left
        self.urx,self.ury = self.deg2num(bbox[3],bbox[2],self.z) # Upper Right
        self.number_of_steps = abs((self.urx-self.llx)*(self.ury-self.lly))

        self.data = {}

    def get_data(self):
        """
        Return the stored dictionary.
        """
        return self.data

    def generate_data(self):
        """
        Makes the API Requests and saves Coordinates and Value of the street signs to a dictionary.
        """
        data_temp = {"from": [self.llx,self.lly], "to": [self.urx,self.ury], "features": []}
        i=0
        for x in range(min(self.llx,self.urx),max(self.llx,self.urx),1):
            for y in range(min(self.lly,self.ury),max(self.lly,self.ury),1):
                i+=1
                yield f"data:Step {i}/{self.number_of_steps}\n\n"
                # API does not take coordinats as input, instead Mapillary, like Open Street Map, uses tilenames.
                # https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames
                # For each Tile a new request has to be made.
                url = f"https://tiles.mapillary.com/maps/vtp/mly_map_feature_traffic_sign/2/{self.z}/{x}/{y}?access_token={self.access_token}"
                r = requests.get(url)
                content = r.content
                features = vt_bytes_to_geojson(content, x, y, self.z)
                for f in features["features"]:
                    if f["properties"]!={}: # Sometimes features don't have properties, don't return those.
                        f_strip = {"coordinates": f["geometry"]["coordinates"], "value": f["properties"]["value"]}
                        data_temp["features"].append(f_strip)
        self.data = data_temp
        yield "data:Done!\n\n" # Tells the script.js that it can now call the data.
    
    def deg2num(self, lat_deg, lon_deg, zoom):
        """
        Translate Coordinates to tilenames.
        Function from https://stackoverflow.com/questions/28476117/easy-openstreetmap-tile-displaying-for-python
        """
        lat_rad = math.radians(lat_deg)
        n = 2.0 ** zoom
        xtile = int((lon_deg + 180.0) / 360.0 * n)
        ytile = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
        return (xtile, ytile)