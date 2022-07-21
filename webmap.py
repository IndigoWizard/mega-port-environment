# importing all project related libraries
import ee
from ee import image
import folium
from folium import features
from folium.plugins import MiniMap
from folium import WmsTileLayer
from branca.element import Template, MacroElement
import geemap
import geemap.colormaps as cm
import geojson
import os
import webbrowser

#################### Earth Engine Configuration #################### 
# ########## Earth Engine Setup
# Triggering authentification to earth engine services
# Uncomment then execute only once > auth succecfull > put back as a comment:
#ee.Authenticate()

# initializing the earth engine library
ee.Initialize()

# ##### earth-engine drawing method setup
def add_ee_layer(self, ee_image_object, vis_params, name):
  map_id_dict = ee.Image(ee_image_object).getMapId(vis_params)
  folium.raster_layers.TileLayer(
      tiles = map_id_dict['tile_fetcher'].url_format,
      attr = 'Map Data &copy; <a href="https://earthengine.google.com/">Google Earth Engine</a>',
      name = name,
      overlay = True,
      control = True
  ).add_to(self)

# configuring earth engine display rendering method in folium
folium.Map.add_ee_layer = add_ee_layer

#################### IMAGERY ANALYSIS ####################

# creating delimitation Area Of Interest/Study of the project (AOI/AOS)
#aoi = ee.Geometry.Rectangle([[2.4125581916503958, 36.49689168784115], [2.1626192268066458, 36.653497195420755]])
aoi = ee.Geometry.Rectangle([[2.2149467468261785, 36.63784557196929], [2.2794914245605535, 36.58024660149864]])

# Buffer/Circular AOI
#aoi = ee.Geometry.Point([2.310362, 36.577489]).buffer(10500)

# Passing main Sentinel-2 imagery ID: image1 (date: 2021-10-21)
# 2021-10-19: COPERNICUS/S2/20211019T104051_20211019T104645_T31SDA
# 2021-02-16: COPERNICUS/S2/20210216T104019_20210216T104758_T31SDA
# 2022-02-18: COPERNICUS/S2_SR/20220218T102949_20220218T103126_T31SDA
image = ee.Image('COPERNICUS/S2_SR/20220218T102949_20220218T103126_T31SDA')
image_2 = ee.Image('COPERNICUS/S2/20220218T102949_20220218T103126_T31SDA')

# ########## Visual Displays
# clipping the image to study area borders
image_satellite = image.clip(aoi).divide(10000)

# visual parameters for the satellite imagery natural colors display
image_params = {
  'bands': ['B4',  'B3',  'B2'],
  'min': 0,
  'max': 1,
  'gamma': 2
}

#################### Custom Visual Displays ####################

# ########## Elevation

# ##### NASA DEM (Digital Elevation Model) collection: 30m resolution
dem = ee.Image('CGIAR/SRTM90_V4').clip(aoi)

# visual parameters for the DEM imagery
dem_params = {
  'min': 0,
  'max': 905
}

# ##### Elevation
# deriving elevation from previous DEM
elevation = dem.select('elevation').clip(aoi)

# visual parameters for the elevation imagery
elevation_params = {
  'min' : 0,
  'max' : 905,
  'palette' : ['#440044', '#FF00FF', '#00FFFF'] # color palette for drawing the elevation model on the map
}

# ##### Slopes (30m resolution)
# deriving slopes from previous DEM through Elevation
slopes = ee.Terrain.slope(elevation).clip(aoi)

# visual parameters for the slopes imagery
slopes_params = {
  'min' : 0,
  'max' : 90,
  'palette' : ['#6f0a91','#43d1bf','#86ea50','#ccec5a'] # color palette for drawing the layer based on slope angle on the map
}

# ##### Contour lines
# deriving countour lines from previous DEM through Terrain
contours = geemap.create_contours(dem, 0, 905, 15, region=aoi)

# visual parameters for the contour lines
contours_params = {
    'min': 0,
    'max': 1000,
    'palette': ['#440044', '#00FFFF', '#00FFFF', '#00FFFF']
}

####################  INDECES #################### 
# ##### NDVI (Normalized Difference Vegetation Index)
# defining NDVI compue function that normalizes the differences between two bands
def getNDVI(image):
  return image.normalizedDifference(['B8', 'B4'])

# clipping to AOI
ndvi = getNDVI(image.clip(aoi))

# NDVI visual parameters:
# Generating a color palette as visual parameter for NDVI display:
# White/Light Green to Dark Green : No vegetation to High/Healthy vegetation
ndvi_params = {
  'min': 0,
  'max': 1,
  'palette': ['#ffffe5', '#f7fcb9', '#78c679', '#41ab5d', '#238443', '#005a32']
}

# ##### NDWI (Normalized Difference Water Index)
def getNDWI(image_2):
  return image_2.normalizedDifference(['B3', 'B11'])

ndwi = getNDWI(image_2.clip(aoi))

# NDWI visual parameters: (shallow water to deep water)
ndwi_params = {
    'min': 0,
    'max': 1,
    'palette': ['#00FFFF', '#0000FF']
}

# ##### NDMI (Normalized Difference Moisture Index)
ndmi = image.expression(
  '((nir-swir1)/(nir+swir1))', {
    'nir': image.select('B8'),
    'swir1': image.select('B11')
  }
)

# clipping NDMI to area of interest
ndmi = ndmi.clip(aoi)

# NDMI visual parameters
ndmi_params = {
  'min': 1,
  'max': 8,
  'palette': ['#d02f05', '#fb7e21', '#eecf3a', '#a4fc3c', '#32f298', '#28bceb', '#466be3', '#30123b']
}

# ##### EVI (Enhanced Vegetation Index)
# EVI formula: 2.5[(NIR – RED) / (NIR + 6RED – 7.5BLUE +1)]
evi = image.expression(
  '2.5*((nir-red)/(nir+6*red-7.5*blue+1))', {
    'blue': image.select('B2'),
    'red': image.select('B4'),
    'nir': image.select('B8')
  }
)

# clipping EVI to area of interest
evi = evi.clip(aoi)

# EVI visual parameters
evi_params = {
  'min': 0,
  'max': 4,
  'palette': ['#5628a1', '#aaf6a2', '#6bea5d', '#22d33d', '#219733']
}

# ##### NDBI (Normalized Difference Built-up Index)
# NDBI formula: (SWIR1 - NIR) / (SWIR1 + NIR)
ndbi = image.expression(
  '((swir1-nir)/(swir1+nir))', {
    'nir': image.select('B8'),
    'swir1': image.select('B11')
  }
)

ndbi = ndbi.clip(aoi)

# NDBI visual parameters
ndbi_params = {
  'min': -1,
  'max': 1,
  'palette': ['#FF00FF']
}


# ########## IMAGES MASKS
# Mask the non-watery parts of the image, where NDVI ratio value > 0.0
ndvi_masked = ndvi.updateMask(ndvi.gte(0))

# EVI Masking: EVI > 0.0
evi_masked = evi.updateMask(evi.gte(0.1))

# NDMI Masking
#ndmi_masked = ndmi.updateMask(ndmi.gte(0))

# NDBI Masking: NDBI > 0.0
ndbi_masked = ndbi.updateMask(ndbi.gte(0.01))

# NDWI Masking: NDWI > 0.1
ndwi_masked = ndwi.updateMask(ndwi.gte(0.1))


# ########## ANALYSIS RESULTS CLASSIFICATION
# ##### NDVI classification: 7 classes
ndvi_classified = ee.Image(ndvi_masked) \
  .where(ndvi.gte(0).And(ndvi.lt(0.15)), 1) \
  .where(ndvi.gte(0.15).And(ndvi.lt(0.25)), 2) \
  .where(ndvi.gte(0.25).And(ndvi.lt(0.35)), 3) \
  .where(ndvi.gte(0.35).And(ndvi.lt(0.45)), 4) \
  .where(ndvi.gte(0.45).And(ndvi.lt(0.65)), 5) \
  .where(ndvi.gte(0.65).And(ndvi.lt(0.75)), 6) \
  .where(ndvi.gte(0.75), 7) \

# Classified NDVI visual parameters
ndvi_classified_params = {
  'min': 1,
  'max': 7,
  'palette': ['#a50026', '#ed5e3d', '#f9f7ae', '#fec978', '#9ed569', '#229b51', '#006837'] 
  # each color corresponds to an NDVI class.
}

# ##### NDMI classification: 8 classes
ndmi_classified = ee.Image(ndmi) \
  .where(ndmi.gte(-1).And(ndmi.lt(-0.1)), 1) \
  .where(ndmi.gte(-0.1).And(ndmi.lt(0)), 2) \
  .where(ndmi.gte(0).And(ndmi.lt(0.1)), 3) \
  .where(ndmi.gte(0.1).And(ndmi.lt(0.2)), 4) \
  .where(ndmi.gte(0.2).And(ndmi.lt(0.3)), 5) \
  .where(ndmi.gte(0.3).And(ndmi.lt(0.4)), 6) \
  .where(ndmi.gte(0.4).And(ndmi.lt(0.5)), 7) \
  .where(ndmi.gte(0.5), 8) \

# NDMI visual parameters are set to use the unclassified NDMI style (ndmi_params)

###########################################################
#################### MAIN PROJECT MAP ####################
# setting up the main map for the project
m = folium.Map(location = [36.6193, 2.2450], tiles='OpenStreetMap', zoom_start = 12, control_scale = True)

# setting up a minimap for general orientation when on zoom
miniMap = MiniMap(
  toggle_display = True,
  zoom_level_offset = -5,
  tile_layer='cartodbdark_matter',
  width=140,
  height=100
).add_to(m)

m.add_child(miniMap)


#################### BASEMAPS ####################
# Adding different types of basemaps helps better visualize the different map features.

# ########## Primary basemaps (victor data):
basemap1 = folium.TileLayer('stamenterrain', name='Stamen Terrain')
# basemap1.add_to(m)

basemap2 = folium.TileLayer('cartodbdark_matter', name='Dark Matter')
basemap2.add_to(m)

# # ########## Secondary basemaps (raster data):
# ##### CyclOSM
basemap3 = (
  'https://{s}.tile-cyclosm.openstreetmap.fr/cyclosm/{z}/{x}/{y}.png'
)
WmsTileLayer(
  url=basemap3,
  layers=None,
  name='Topography Map',
  attr='Topography Map'
).add_to(m)

# ##### ESRI sattelite imagery service
basemap4 = (
    'http://services.arcgisonline.com/arcgis/rest/services/World_Imagery' + '/MapServer/tile/{z}/{y}/{x}'
)
WmsTileLayer(
  url=basemap4,
  layers=None,
  name='ESRI Sattelite Imagery',
  attr='ESRI World Imagery'
).add_to(m)

# ##### Google sattelite imagery service
basemap5 = (
    'https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}'
)
WmsTileLayer(
  url=basemap5,
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
    fields=['name', 'zone-designation', 'area'],
    aliases=['Name: ', 'Zone designation: ', 'Area: '],
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
  name = 'Roads - Port access infrastructure',
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
    fields=['name', 'type', 'status', 'section', 'ilot', 'area'],
    aliases=['Name: ', 'Type: ', 'Project status: ', 'Section: ', 'Ilot: ', 'Superficie Touchee (Ha): '],
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
    fields=['name', 'type', 'status', 'area'],
    aliases=['Name: ', 'Type: ', 'Project status: ', 'Superficie (Ha): '],
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
    fields=['designation', 'status'],
    aliases=['Land designation: ', 'Project status: '],
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

############################################################
#################### COMPUTED RASTER LAYERS ####################

# adding main satellite image as layer
m.add_ee_layer(image_satellite, image_params, 'Sentinel-2 True Colors')

# ##### SRTM elevation & slopes
# adding DEM layer
#m.add_ee_layer(dem, dem_params, 'NASA DEM 30m')

# adding SRTM elevation layer
m.add_ee_layer(elevation, elevation_params, 'Elevation')

# adding slopes layer
m.add_ee_layer(slopes, slopes_params, 'Slopes')

# adding EVI layer to the map
m.add_ee_layer(evi_masked, evi_params, 'EVI')

# adding NDMI layer
m.add_ee_layer(ndmi_classified, ndmi_params, 'NDMI - Classified')

# adding NDVI layer to the map
m.add_ee_layer(ndvi_masked, ndvi_params, 'NDVI')

# adding Classified NDVI layer to the map
m.add_ee_layer(ndvi_classified, ndvi_classified_params, 'NDVI - Classified')

# adding NDBI layer
m.add_ee_layer(ndbi_masked, ndbi_params, 'NDBI')

# adding NDWI layer to the map
m.add_ee_layer(ndwi_masked, ndwi_params, 'NDWI')

# adding contour lines to the map
m.add_ee_layer(contours, contours_params, 'Contour lines')

#################### Layer controller ####################

folium.LayerControl(collapsed=True).add_to(m)

#################### MAP LEGEND ####################
#<link rel="stylesheet" href="style.css">
#<div class="leaflet-control-layers-separator"></div>

legend_setup = """
{% macro html(this, kwargs) %}
<!doctype html>
<html lang="en">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>PORT CENTRE DE CHERCHELL - IMAGERY ANALYSIS</title>
        <link rel="stylesheet" href="//code.jquery.com/ui/1.12.1/themes/base/jquery-ui.css">
        <link rel="stylesheet" href="src/ui.css">
        <script src="https://code.jquery.com/jquery-1.12.4.js"></script>
        <script src="https://code.jquery.com/ui/1.12.1/jquery-ui.js"></script>

        <script>
            $(function() {
                $("#ui-container, #title-container, #project-container").draggable({
                    start: function(event, ui) {
                        $(this).css({
                            right: "auto",
                            top: "auto",
                            bottom: "auto"
                        });
                    }
                });
            });
        </script>
    </head>

  <body>
  <div class="ui-container" id="title-container">
    <div class="map-title">
      <p>CHERCHELL CENTER PORT - ENVIRONEMENTAL STUDY</p>
    </div>
  </div>
  
  <div class="ui-container" id="project-container">
      <div class="project-source">
          <div class="project-logo">
              <a href="https://github.com/IndigoWizard/mega-port-environment/tree/develop" title="Go to repository" target="_blank">
                <i class="fa fa-github" aria-hidden="true"></i>
              </a>
          </div>
          
          <div class="project-info">
            <a href="https://github.com/IndigoWizard/mega-port-environment/tree/develop" title="Go to repository" target="_blank"><p  class="project-link">IndigoWizard/mega-port-environment</p></a>
            <div class="project-stats">
              <a href="https://github.com/IndigoWizard/mega-port-environment/releases/tag/0.1.1" target="_blank"><i class="fa fa-tag" aria-hidden="true"> 0.2.0</i></a>
              <a href="https://github.com/IndigoWizard/mega-port-environment/stargazers" target="_blank"><i class="fa fa-star" aria-hidden="true"> Star it!</i></a>
              <a href="https://github.com/IndigoWizard/mega-port-environment/network/members" target="_blank"><i class="fa fa-code-fork" aria-hidden="true"> Fork it!</i></a>
            </div>
          </div>
      </div>
  </div>

  <div id="ui-container" class="ui-container">
      <div class='legend-title'>Legend</div>
      
      <div class="index-container">

        <div class='legend-scale' id="VECTOR">
          <ul class='legend-labels'>
            <li><span style='background:#9e57b0;opacity:0.8;'></span>Logistic industrial zones.</li>
            <li><span style='background:#0000ff;opacity:0.8;border: 4px #1a9a00 dotted;'></span>Construction sites.</li>
            <li><span style='background:#740118;opacity:0.8;'></span>Port main infrastructure.</li>
            <li><span style="border:3px dashed #1d1f2b;height:0;opacity:0.8;margin-top: 8px;"></span>Port futur highway.</li>
            <li><span style="border:3px dashed #ff0;height:0;opacity:0.8;background: #b8cee299;margin-top: 8px;"></span>Port futur highway - Suggested deviation.</li>
            <li><span style='background:#145B27;opacity:0.8;'></span>Forests - Affected Zones.</li>
            <li><span style='background:#0b8a03;opacity:0.8;'></span>Forests - Preserved Natural Zones.</li>
            <li><span style='background:#00c632;opacity:0.8;'></span>Farms and Aggricultural lands.</li>
            <li><span style='background:#0070ec;opacity:0.8;'></span>Shoreline.</li>
            <li><span style='background:#75cff0;opacity:0.8;'></span>Waterways.</li>
          </ul>
        </div>

        <div class='legend-scale' id="NDVI">
            <h4>NDVI</h4>
            <ul class='legend-labels'>
                <li><span style='background:#ed5e3d;opacity:0.8;'></span>0.0 - 0.1 : Bareland / Settlements</li>
                <li><span style='background:#fec978;opacity:0.8;'></span>0.1 - 0.25 : Low vegeation</li>
                <li><span style='background:#f9f7ae;opacity:0.8;'></span>0.25 - 0.35 : Crops</li>
                <li><span style='background:#9ed569;opacity:0.8;'></span>0.35 - 0.55 : Low vegetation</li>
                <li><span style='background:#229b51;opacity:0.8;'></span>0.55 - 0.75 : High vegetation</li>
                <li><span style='background:#006837;opacity:0.8;'></span>> 0.75 : Forest</li>
            </ul>
        </div>

        <div class="index-gradient">

          <div class="index-gradient-container">
            <div class='legend-scale' id="NDWI">
              <h4>NDWI</h4>
              <div class="inside-container">
                <div class="gradient-block">
                  <span id="ndwi-gradient"></span>
                </div>
                <div class="gradient-text">
                  <p>Shallow<br>waters</p>
                  <p>Deep<br>waters</p>
                </div>
              </div>
            </div>
          </div>

          <div class="index-gradient-container">
            <div class='legend-scale' id="DEM">
              <h4>DEM</h4>
              <div class="inside-container">
                <div class="gradient-block">
                  <span id="dem-gradient"></span>
                </div>
                <div class="gradient-text">
                  <p>1000m</p>
                  <p>500m</p>
                  <p>0m</p>
                </div>
              </div>
            </div>
          </div>
          
          <div class="index-gradient-container" id="far-right">
            <div class='legend-scale' id="Slopes">
              <h4>Slopes</h4>
              <div class="inside-container">
                <div class="gradient-block">
                  <span id="slopes-gradient"></span>
                </div>
                <div class="gradient-text">
                  <p>90°</p>
                  <p>60°</p>
                  <p>30°</p>
                  <p>0°</p>
                </div>
              </div>
            </div>
          </div>

        </div>

      </div>

  </div>

  </body>
</html>
{% endmacro %}
"""

# configuring the legend
legend = MacroElement()
legend._template = Template(legend_setup)

# adding legend to the map
m.get_root().add_child(legend)

#################### Creating the map file #################### 
#### Export image

# path = image.getDownloadUrl({
#   'image': image_satellite,
#   'bands': ['B2', 'B3', 'B4', 'B8'],
#   'description': 'Sentinel-2',
#   'scale': 8, # for resolution of image
#   'crs': 'EPSG:4326', # which crs-transformation should apply
#   'region': aoi,
#   'maxPixels': 1e9,
#   })

# print downloadable link you can download image by click link printed by program
#print (path)

# Generating a file for the map and setting it to open on default browser
m.save('webmap.html')

# Opening the map file in default browser on execution
webbrowser.open('webmap.html')