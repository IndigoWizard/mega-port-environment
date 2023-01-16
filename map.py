import ee
from ee import image
import folium
from folium import features
from folium.plugins import GroupedLayerControl
import os
import webbrowser

# Triggering authentification to earth engine services
# Run in terminal: earthengine authenticate
# Or
# Uncomment then execute the kine bellow only once per session > auth succecfull > put back as a comment to avoid executing it over and over while testing the project:

# ee.Authenticate()

# initializing the earth engine library (always keep this on)
ee.Initialize()


# ##### Define a method for displaying Earth Engine image tiles to folium map
def add_ee_layer(self, ee_image_object, vis_params, name):
  map_id_dict = ee.Image(ee_image_object).getMapId(vis_params)
  folium.raster_layers.TileLayer(
      tiles = map_id_dict['tile_fetcher'].url_format,
      attr = 'Map Data &copy; <a href="https://earthengine.google.com/">Google Earth Engine</a>',
      name = name,
      overlay = True,
      control = True
  ).add_to(self)

# Add EE drawing method to folium.
folium.Map.add_ee_layer = add_ee_layer

# Working with a specific satellite imagery ID (sentinel-2)
image_satellite = ee.Image('COPERNICUS/S2/20220218T102949_20220218T103126_T31SDA')

# Sattelite image visual parameters
image_params = {
  'bands': ['B4',  'B3',  'B2'],
  'min': 0,
  'max': 0.3,
  'gamma': 1
}

#################### MAIN PROJECT MAP ####################
# setting up the main map for the project
m = folium.Map(location = [36.5711, 2.2834], tiles=None, zoom_start = 12, control_scale = True)

# ########## Primary basemaps (victor data):
basemap1 = folium.TileLayer('cartodbdark_matter', name='Dark Matter').add_to(m)
basemap2 = folium.TileLayer('openstreetmap', name='Open Street Map').add_to(m)

#################### SPATIAL FEATURES LAYERS ####################
#################### DATA ####################
squares = os.path.join(r'squares.geojson')
triangles = os.path.join(r'triangles.geojson')
markers = os.path.join(r'markers.geojson')

# #### SQUARES features layers
squares_style_function = lambda x: {
  'fillColor' : 'fill',
  'color' : '#555555',
  'opacity' : 0.50,
  'weight' : 2,
  'dashArray' : '3, 6'
}

# style change on highlight defining fuction (for the hover effect)
squares_highlight_function = lambda x: {
  'fillColor': '#555555', 
  'color':'#555555', 
  'fillOpacity': 0.50,
  'opacity' : 0.50,
  'weight': 2,
  'dashArray' : '3, 6'
}

# main function of drawing and displaying the spatial feature 
SQUARES_INFO = folium.features.GeoJson(
  squares,
  name = 'SQUARES',
  control = True,
  style_function = squares_style_function, 
  highlight_function = squares_highlight_function,
)
m.add_child(SQUARES_INFO)

# #### TRIANGLES features layers
triangles_style_function = lambda x: {
  'fillColor' : 'fill',
  'color' : 'red',
  'opacity' : 0.50,
  'weight' : 2,
  'dashArray' : '3, 6'
}

# style change on highlight defining fuction (for the hover effect)
triangles_highlight_function = lambda x: {
  'fillColor': '#555555', 
  'color':'#555555', 
  'fillOpacity': 0.50,
  'opacity' : 0.50,
  'weight': 2,
  'dashArray' : '3, 6'
}

# main function of drawing and displaying the spatial feature 
TRIANGLES_INFO = folium.features.GeoJson(
  triangles,
  name = 'TRIANGLES',
  control = True,
  style_function = triangles_style_function, 
  highlight_function = triangles_highlight_function,
)
m.add_child(TRIANGLES_INFO)

# #### MARKERS features layers
markers_group = folium.FeatureGroup(
  name='Markers',
  overlay=True,
  control=True,
  show=True
).add_to(m)

folium.Marker(
  location=[36.6193, 2.2547],
  popup= None,
  tooltip="<h4>Marker 1.</h4>",
  icon=folium.Icon(
    color='red',
    icon_color='white',
    icon='info-sign'
  )
).add_to(markers_group)



marker_colors = ["red", "orange", "green", "blue"]

MARKERS_INFO = folium.GeoJson(
  markers,
  name="Markers group",
  zoom_on_click=True,
  marker=folium.Marker(
    icon=folium.Icon(icon='star')
    ),
).add_to(m)


#################### LAYER GROUPS ####################
GroupedLayerControl(
    groups={
      '-------------SHAPE LAYERS-------------': [SQUARES_INFO, TRIANGLES_INFO],
      '-----------------MARKERS LAYER-----------------': [MARKERS_INFO],
      # '-----------------GOOLE EARTH ENGINE LAYERS-----------------': [],
    },
    exclusive_groups=False,
    collapsed=False
).add_to(m)


#################### LAYERS ORDER ####################
# adding the satellite image as layer and display it on the map + on layer panel
m.add_ee_layer(image_satellite, image_params, 'Sentinel-2 True Colors')

#################### Layer controller ####################
folium.LayerControl(collapsed=False).add_to(m)

# save map as html file
m.save('map.html')
# Opening the map file in default browser on execution
webbrowser.open('map.html')
