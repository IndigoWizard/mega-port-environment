# importing all project related libraries
import folium
from folium import features
from folium.plugins import MiniMap
from folium import WmsTileLayer
import geojson
import os
import webbrowser

from pygments import highlight

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

#################### SPATIAL FEATURES LAYERS ####################
#################### DATA ####################
# Here I'll store all spatial features layers data variables despite their categories (all new data of same type should be added here)
wilaya_admin_borders = os.path.join(r'layers/tipaza_admin_borders.geojson')

# ########## Administrative features layers
forest_batch_style_function = lambda x: {
  'fillColor' : 'none',
  'color' : 'red',
  'opacity' : 0.50,
  'weight' : 2,
  'dashArray' : '3, 6'}

forest_batch_highlight_function = lambda x: {
  'fillColor': '#555555', 
  'color':'#555555', 
  'fillOpacity': 0.50,
  'opacity' : 0.50,
  'weight': 2,
  'dashArray' : '3, 6'}

WILAYA_ADMIN_INFO = folium.features.GeoJson(
    wilaya_admin_borders,
    name = 'W. Tipaza - Administrative Borders',
    control=True,
    style_function=forest_batch_style_function, 
    highlight_function=forest_batch_highlight_function,
    tooltip=folium.features.GeoJsonTooltip(
        # using fields from the geojson file
        fields=['name', 'area', 'density', 'city_code'],
        aliases=['Wilaya: ', 'Area (km2 ): ', 'Density (popualtion/km2): ', 'City Code: '],
        style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;") # setting style for popup box
    )
)
m.add_child(WILAYA_ADMIN_INFO)

#################### Layer controller ####################

folium.LayerControl().add_to(m)

#################### Creating the map file #################### 

# Generating a file for the map and setting it to open on default browser
m.save('web-map.html')

# Opening the map file in default browser on execution
webbrowser.open('web-map.html')