# importing all project related libraries
import folium
from folium.plugins import MiniMap
from folium import WmsTileLayer
import webbrowser

# setting up the main map for the project
m = folium.Map(location = [36.6193, 2.2547], tiles='OpenStreetMap', zoom_start = 15, control_scale = True)

# setting up a minimap for general orientation when on zoom
miniMap = MiniMap(
  toggle_display = True,
  zoom_level_offset = -7,
  tile_layer='Stamen Terrain',
  width=140,
  height=100
).add_to(m)

m.add_child(miniMap)


#################### BASEMAPS ####################
# Adding different types of basemaps helps better visualize the different map features.

# ########## Primary basemaps (victor data):
basemap1 = folium.TileLayer('stamenterrain', name='Stamen Terrain')
basemap1.add_to(m)

basemap2 = folium.TileLayer('cartodbdark_matter', name='Dark Matter')
basemap2.add_to(m)

# ########## Secondary basemaps (raster data):
# ##### ESRI sattelite imagery service
basemap3 = (
    'http://services.arcgisonline.com/arcgis/rest/services/World_Imagery' + '/MapServer/tile/{z}/{y}/{x}'
)
WmsTileLayer(
  url=basemap3,
  layers=None,
  name='ESRI Sattelite Imagery',
  attr='ESRI World Imagery'
).add_to(m)

# ##### Google sattelite imagery service
basemap4 = (
    'https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}'
)
WmsTileLayer(
  url=basemap4,
  layers=None,
  name='Google Sattelite Imagery',
  attr='Google'
).add_to(m)


#################### Layer controller ####################

folium.LayerControl().add_to(m)

#################### Creating the map file #################### 

# Generating a file for the map and setting it to open on default browser
m.save('web-map.html')

# Opening the map file in default browser on execution
webbrowser.open('web-map.html')