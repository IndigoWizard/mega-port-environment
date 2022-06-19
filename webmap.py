# importing all project related libraries
import folium
from folium import features
from folium.plugins import MiniMap
from folium import WmsTileLayer
import geojson
import os
import webbrowser

################### NEXT TASKS
# Imagery analysis with earth-engine api

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
# Here I'll store all spatial features layers data variables despite their categories
#  (all new data of same type should be added here)
wilaya_admin_borders = os.path.join(r'layers/tipaza_admin_borders.geojson')
municipalities_admin_borders = os.path.join(r'layers/municipalities_admin_borders.geojson')
shoreline = os.path.join(r'layers/shoreline.geojson')
forests_affected_zones = os.path.join(r'layers/forests_affected_zones.geojson')
forests_preserved_natural_area = os.path.join(r'layers/forest_preserved_natural_area.geojson')
logistic_zones = os.path.join(r'layers/logistic_zones.geojson')
port_infrastructure = os.path.join(r'layers/port_main_infrastructure.geojson')
construction_zones = os.path.join(r'layers/construction_zones.geojson')
agro_farm_land = os.path.join(r'layers/agro_farm_land.geojson')
waterways = os.path.join(r'layers/waterways.geojson')
roads = os.path.join(r'layers/roads.geojson')

# ########## Administrative features layers
# ##### Wilaya Tipaza administrative borders
# style defining fuction
wilaya_admin_style_function = lambda x: {
  'fillColor' : 'none',
  'color' : 'red',
  'opacity' : 0.50,
  'weight' : 2,
  'dashArray' : '3, 6'
}

# style change on highlight defining fuction (for the hover effect)
wilaya_admin_highlight_function = lambda x: {
  'fillColor': '#555555', 
  'color':'#555555', 
  'fillOpacity': 0.50,
  'opacity' : 0.50,
  'weight': 2,
  'dashArray' : '3, 6'
}

# main function of drawing and displaying the spatial feature 
WILAYA_ADMIN_INFO = folium.features.GeoJson(
  wilaya_admin_borders,
  name = 'Tipaza - Wilaya Administrative Borders',
  control = True,
  style_function = wilaya_admin_style_function, 
  highlight_function = wilaya_admin_highlight_function,
  tooltip=folium.features.GeoJsonTooltip(
    # using fields from the geojson file
    fields=['name', 'area', 'density', 'city_code'],
    aliases=['Wilaya: ', 'Area (km2 ): ', 'Density (popualtion/km2): ', 'City Code: '],
    style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;") # setting style for popup box
  )
)
m.add_child(WILAYA_ADMIN_INFO)

# ##### Tipaza - Municipalities borders
municipalities_admin_style_function = lambda x: {
  'fillColor' : '#555555',
  'color' : '#331D31',
  'fillOpacity': 0.10,
  'opacity' : 0.50,
  'weight' : 3,
  'dashArray' : '2, 6'
}

municipalities_admin_highlight_function = lambda x: {
  'fillColor': '#555555', 
  'color':'#331D31', 
  'fillOpacity': 0.30,
  'opacity' : 0.90,
  'weight': 3,
  'dashArray' : '2, 6'
}

MUNICIPALITIES_ADMIN_INFO = folium.features.GeoJson(
  municipalities_admin_borders,
  name = 'Tipaza - Municipalities Administrative Borders',
  control = True,
  style_function = municipalities_admin_style_function, 
  highlight_function = municipalities_admin_highlight_function,
  tooltip=folium.features.GeoJsonTooltip(
    fields=['name', 'ONS_Code'],
    aliases=['Municipality: ', 'ONS Code: '],
    style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;") 
  )
)
m.add_child(MUNICIPALITIES_ADMIN_INFO)

# ########## Artificial features (Infrastructure) layers
# ##### Logistic industrial zones
logistic_zones_style_function = lambda x: {
  'fillColor' : '#9e57b0',
  'color' : '#9e57b0',
  'fillOpacity': 0.50,
  'opacity' : 0.50,
  'weight' : 2
}

logistic_zones_highlight_function = lambda x: {
  'fillColor': '#9e57b0', 
  'color':'#9e57b0', 
  'fillOpacity': 0.90,
  'opacity' : 0.90,
  'weight': 2
}

LOGISTIC_ZONES_INFO = folium.features.GeoJson(
  logistic_zones,
  name = 'Logistic industrial zones',
  control = True,
  style_function = logistic_zones_style_function, 
  highlight_function = logistic_zones_highlight_function,
  tooltip=folium.features.GeoJsonTooltip(
    fields=['name', 'area', 'district-jurisdiction', 'municipal-jurisdiction'],
    aliases=['Name: ', 'Area (Ha)', 'Jurisdiction (District): ', 'Jurisdiction (Municipality): '],
    style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;") 
  )
)
m.add_child(LOGISTIC_ZONES_INFO)

# ##### Port Main Infrastructure
port_infrastructure_style_function = lambda x: {
  'fillColor': '#a80223',
  'color': '#740118',
  'fillOpacity': 0.50,
  'opacity': 0.50,
  'weight': 2
}

port_infrastructure_highlight_function = lambda x: {
  'fillColor': '#a80223',
  'color': '#740118',
  'fillOpacity': 0.90,
  'opacity': 1,
  'weight': 2
}

PORT_INFRASTRUCTURE_INFO = folium.features.GeoJson(
  port_infrastructure,
  name = 'Port Main Infrastructure',
  control = True,
  style_function = port_infrastructure_style_function, 
  highlight_function = port_infrastructure_highlight_function,
  tooltip=folium.features.GeoJsonTooltip(
    fields=['name', 'area'],
    aliases=['Name: ', 'Area (Ha): '],
    style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;") 
  )
)
m.add_child(PORT_INFRASTRUCTURE_INFO)

# ##### Construction zones
construction_zones_style_function = lambda x: {
  'fillColor': '#0000ff',
  'color': '#0b8a03',
  'fillOpacity': 0.50,
  'opacity': 0.50,
  'weight': 4,
  'dashArray' : '3, 6'
}

construction_zones_highlight_function = lambda x: {
  'fillColor': '#0000ff',
  'color': '#0b8a03',
  'fillOpacity': 0.80,
  'opacity': 0.90,
  'weight': 4,
  'dashArray' : '3, 6'
}

CONSTRUCTION_ZONES_INFO = folium.features.GeoJson(
  construction_zones,
  name = 'Construction Zones',
  control = True,
  style_function = construction_zones_style_function, 
  highlight_function = construction_zones_highlight_function,
  tooltip=folium.features.GeoJsonTooltip(
    fields=['zone-designation', 'name'],
    aliases=['Zone designation: ', 'Name: '],
    style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;") 
  )
)
m.add_child(CONSTRUCTION_ZONES_INFO)

# roads / mobility infrastructure
roads_style_function = lambda x: {
  'color' : x['properties']['stroke'],
  'opacity' : 0.50,
  'weight' : x['properties']['stroke-width'],
  'dashArray' : x['properties']['dashArray']
}

roads_highlight_function = lambda x: {
  'color' : x['properties']['stroke'],
  'opacity' : 0.9,
  'weight' : x['properties']['stroke-width'],
  'dashArray' : x['properties']['dashArray-highlight']
}

ROADS_INFO = folium.features.GeoJson(
  roads,
  name = 'roads',
  control = True,
  style_function = roads_style_function, 
  highlight_function = roads_highlight_function,
  tooltip=folium.features.GeoJsonTooltip(
    fields=['Type', 'Name'],
    aliases=['Type: ', 'Name: '],
    style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;") 
  )
)
m.add_child(ROADS_INFO)

# ########## Natural features layers
# ##### Shoreline
folium.GeoJson(
  shoreline,
  name = 'Shoreline',
  tooltip = 'Shoreline',
  style_function = lambda feature : {
    'fillColor' : 'none',
    'color' : '#0070ec',
    'weight' : 8,
    'opacity' : 0.50,
  }
).add_to(m)

# ##### Affected Forests zones
forests_az_style_function = lambda x: {
  'fillColor' : '#145B27',
  'color' : '#145B27',
  'fillOpacity' : 0.50,
  'opacity' : 0.50,
  'weight' : 2
}

forests_az_highlight_function = lambda x: {
  'fillColor': '#177A31', 
  'color':'#145B27', 
  'fillOpacity': 0.80,
  'opacity' : 0.50,
  'weight': 2
}

FORESTS_AFFECTED_INFO = folium.features.GeoJson(
  forests_affected_zones,
  name = 'Forests - Affected Zones',
  control = True,
  style_function = forests_az_style_function, 
  highlight_function = forests_az_highlight_function,
  tooltip=folium.features.GeoJsonTooltip(
    fields=['name', 'section', 'ilot', 'area'],
    aliases=['Name: ', 'Section: ', 'Ilot: ', 'Superficie Touchee (Ha): '],
    style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;") 
  )
)
m.add_child(FORESTS_AFFECTED_INFO)

# ##### Preserved Natural Forest Area
forests_pz_style_function = lambda x: {
  'fillColor' : '#0b8a03',
  'color' : '#0b8a03',
  'fillOpacity' : 0.50,
  'opacity' : 0.50,
  'weight' : 2,
  'dashArray' : '3, 6'
}

forests_pz_highlight_function = lambda x: {
  'fillColor': '#0b8a03', 
  'color':'#0b8a03', 
  'fillOpacity': 0.80,
  'opacity' : 0.50,
  'weight': 2,
  'dashArray' : '3, 6'
}

FORESTS_PRESERVED_INFO = folium.features.GeoJson(
  forests_preserved_natural_area,
  name = 'Forests - Preserved Natural Zones',
  control = True,
  style_function = forests_pz_style_function, 
  highlight_function = forests_pz_highlight_function,
  tooltip=folium.features.GeoJsonTooltip(
    fields=['name', 'area'],
    aliases=['Name: ', 'Superficie (Ha): '],
    style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;") 
  )
)
m.add_child(FORESTS_PRESERVED_INFO)

# ##### Agricultural and Farm lands
agro_farm_land_style_function = lambda x: {
  'fillColor' : '#00c632',
  'color' : '#607254',
  'fillOpacity' : 0.50,
  'opacity' : 0.50,
  'weight' : 2,
  'dashArray' : '3, 6'
}

agro_farm_land_highlight_function = lambda x: {
  'fillColor': '#00c632', 
  'color':'#607254', 
  'fillOpacity': 0.80,
  'opacity' : 0.50,
  'weight': 2,
  'dashArray' : '3, 6'
}

AGRO_FARM_LAND_INFO = folium.features.GeoJson(
  agro_farm_land,
  name = 'Agricultural and Farm lands',
  control = True,
  style_function = agro_farm_land_style_function, 
  highlight_function = agro_farm_land_highlight_function,
  tooltip=folium.features.GeoJsonTooltip(
    fields=['designation'],
    aliases=['Land designation: '],
    style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;") 
  )
)
m.add_child(AGRO_FARM_LAND_INFO)

# ##### Waterways
waterways_style_function = lambda x: {
  'fillColor' : '#75cff0',
  'color' :  '#75cff0',
  'fillOpacity' : 0.50,
  'opacity' : 0.50,
  'weight' : 2,
}

waterways_highlight_function = lambda x: {
  'fillColor': '#75cff0', 
  'color': '#75cff0', 
  'fillOpacity': 0.80,
  'opacity' : 0.9,
  'weight': 4,
}

WATERWAYS_INFO = folium.features.GeoJson(
  waterways,
  name = 'Waterways',
  control = True,
  style_function = waterways_style_function, 
  highlight_function = waterways_highlight_function,
  tooltip=folium.features.GeoJsonTooltip(
    fields=['name', 'type'],
    aliases=['Name: ', 'Type: '],
    style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;") 
  )
)
m.add_child(WATERWAYS_INFO)


#################### Layer controller ####################

folium.LayerControl(collapsed=False).add_to(m)

#################### Creating the map file #################### 

# Generating a file for the map and setting it to open on default browser
m.save('web-map.html')

# Opening the map file in default browser on execution
webbrowser.open('web-map.html')