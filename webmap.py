# importing all project related libraries
import ee
from ee import image
import folium
from folium import features
from folium.plugins import GroupedLayerControl
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
  layer = folium.raster_layers.TileLayer(
      tiles = map_id_dict['tile_fetcher'].url_format,
      attr = 'Map Data &copy; <a href="https://earthengine.google.com/">Google Earth Engine</a>',
      name = name,
      overlay = True,
      control = True
  )
  layer.add_to(self)
  return layer

# configuring earth engine display rendering method in folium
folium.Map.add_ee_layer = add_ee_layer

#################### IMAGERY ANALYSIS ####################

# creating delimitation Area Of Interest/Study of the project (AOI/AOS)
#aoi = ee.Geometry.Rectangle([[2.4125581916503958, 36.49689168784115], [2.1626192268066458, 36.653497195420755]])
#aoi = ee.Geometry.Rectangle([[2.2149467468261785, 36.63784557196929], [2.2794914245605535, 36.58024660149864]])

# Buffer/Circular AOI
aoi = ee.Geometry.Point([2.310362, 36.577489]).buffer(10500)

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
  'max': 0.3,
  'gamma': 1
}

#################### Custom Visual Displays ####################

# ########## Elevation

# ##### JAXA ALOS DSM: Global 30m  (Digital Surface Model)
dem = ee.Image('JAXA/ALOS/AW3D30/V2_2').clip(aoi)

# masking the DSM to the surface of the earth only
dem = dem.updateMask(dem.gt(0))

# visual parameters for the DSM imagery
dem_params = {
  'min': 0,
  'max': 905,
  'bands': ['AVE_DSM']
}

# ##### Elevation
# deriving elevation from previous DSM
elevation = dem.select('AVE_DSM').clip(aoi)

# visual parameters for the elevation imagery
elevation_params = {
  'min' : 0,
  'max' : 905,
  'palette' : ['#440044', '#FF00FF', '#00FFFF'],
  'opacity': 0.8 # color palette for drawing the elevation model on the map
}

# ##### Hillshades (30m resolution)
hillshade = ee.Terrain.hillshade(elevation)

# visual parameters for hillshade layer
hillshade_params = {
  'min': 0,
  'max': 270,
  'palette': ['#000000', '#20034c', '#a02561', '#fbad07'],
  'opacity': 1
}

# ##### Slopes (30m resolution)
# deriving slopes from previous DSM through Elevation
slopes = ee.Terrain.slope(elevation).clip(aoi)

# visual parameters for the slopes imagery
slopes_params = {
  'min' : 0,
  'max' : 90,
  'palette' : ['#6f0a91','#43d1bf','#86ea50','#ccec5a'],
  'opacity': 0.8 # color palette for drawing the layer based on slope angle on the map
}

# ##### Contour lines
# deriving countour lines from previous DSM through Terrain
contours = geemap.create_contours(elevation, 0, 905, 20, region=aoi)

# visual parameters for the contour lines
contours_params = {
  'min': 0,
  'max': 1000,
  'palette' : ['#053061', '#2166ac', '#4393c3', '#92c5de', '#d1e5f0', '#f7f7f7', '#fddbc7', '#f4a582', '#d6604d', '#b2182b', '#67001f'],
  'opacity': 0.3
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
  'palette': ['#ffffe5', '#f7fcb9', '#78c679', '#41ab5d', '#238443', '#005a32'],
  'opacity': 0.8
}

# ##### NDWI (Normalized Difference Water Index)
def getNDWI(image_2):
  return image_2.normalizedDifference(['B3', 'B11'])

ndwi = getNDWI(image_2.clip(aoi))

# NDWI visual parameters: (shallow water to deep water)
ndwi_params = {
  'min': 0,
  'max': 1,
  'palette': ['#00FFFF', '#0000FF'],
  'opacity': 0.8
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
  'palette': ['#d02f05', '#fb7e21', '#eecf3a', '#a4fc3c', '#32f298', '#28bceb', '#466be3', '#30123b'],
  'opacity': 0.8
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
  'palette': ['#5628a1', '#aaf6a2', '#6bea5d', '#22d33d', '#219733'],
  'opacity': 0.8
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
  'palette': ['#B50044'],
  'opacity': 0.8
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
  'palette': ['#a50026', '#ed5e3d', '#f9f7ae', '#fec978', '#9ed569', '#229b51', '#006837'],
  'opacity': 0.8
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
m = folium.Map(location = [36.5711, 2.2834], tiles=None, zoom_start = 12, control_scale = True)

# setting up a minimap for general orientation when on zoom
miniMap = MiniMap(
  toggle_display = True,
  zoom_level_offset = -5,
  tile_layer='cartodbdark_matter',
  width=140,
  height=100,
  minimized=True
)

m.add_child(miniMap)


#################### BASEMAPS ####################
# Adding different types of basemaps helps better visualize the different map features.

# ########## Primary basemaps (victor data):
basemap1 = folium.TileLayer('cartodbdark_matter', name='Dark Matter Basemap')
basemap1.add_to(m)

basemap2 = folium.TileLayer('openstreetmap', name='Open Street Map', show=False)
basemap2.add_to(m)

# # ########## Secondary basemaps (raster data):
# ##### CyclOSM
basemap3 = WmsTileLayer(
  url=('https://{s}.tile-cyclosm.openstreetmap.fr/cyclosm/{z}/{x}/{y}.png'),
  layers=None,
  name='Topography Map',
  attr='Topography Map',
  show=False
).add_to(m)

# ##### ESRI sattelite imagery service
basemap4 = WmsTileLayer(
  url=('http://services.arcgisonline.com/arcgis/rest/services/World_Imagery' + '/MapServer/tile/{z}/{y}/{x}'),
  layers=None,
  name='ESRI Sattelite Imagery',
  attr='ESRI World Imagery',
  show=False
).add_to(m)

# ##### Google sattelite imagery service
basemap5 = WmsTileLayer(
  url=('https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}'),
  layers=None,
  name='Google Sattelite Imagery',
  attr='Google',
  show=False
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
  name = 'Wilaya Borders',
  control = True,
  style_function = wilaya_admin_style_function, 
  highlight_function = wilaya_admin_highlight_function,
  tooltip=folium.features.GeoJsonTooltip(
    # using fields from the geojson file
    fields=['name', 'area', 'density', 'city_code'],
    aliases=['Wilaya: ', 'Area (km2 ): ', 'Density (popualtion/km2): ', 'City Code: '],
    style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;") # setting style for popup box
  ),
  show=False
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
  name = 'Municipalities Borders',
  control = True,
  style_function = municipalities_admin_style_function, 
  highlight_function = municipalities_admin_highlight_function,
  tooltip=folium.features.GeoJsonTooltip(
    fields=['name', 'ONS_Code'],
    aliases=['Municipality: ', 'ONS Code: '],
    style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;") 
  ),
  show=False
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
  ),
  show=False
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
  ),
  show=False
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
  ),
  show=False
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
  ),
  show=False
)
m.add_child(ROADS_INFO)

# ########## Natural features layers
# ##### Shoreline
SHORELINE = folium.GeoJson(
  shoreline,
  name = 'Shoreline',
  tooltip = 'Shoreline',
  style_function = lambda feature : {
    'fillColor' : 'none',
    'color' : '#0070ec',
    'weight' : 4,
    'opacity' : 0.50,
  },
  show=False
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
  ),
  show=False
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
  ),
  show=False
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
  ),
  show=False
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
  ),
  show=False
)
m.add_child(WATERWAYS_INFO)

############################################################
#################### COMPUTED RASTER LAYERS ####################

# adding main satellite image as layer
TCI = m.add_ee_layer(image_satellite, image_params, 'Sentinel-2 True Colors')

# ##### SRTM elevation & slopes
# adding DSM layer
#m.add_ee_layer(dem, dem_params, 'NASA DSM 30m')

# adding Hillshades
HILLSHADE = m.add_ee_layer(hillshade, hillshade_params, "Hillshade")

# adding SRTM elevation layer
ELEVATION = m.add_ee_layer(elevation, elevation_params, 'Elevation')

# adding slopes layer
SLOPES = m.add_ee_layer(slopes, slopes_params, 'Slopes')

# adding EVI layer to the map
EVI = m.add_ee_layer(evi_masked, evi_params, 'EVI')

# adding NDMI layer
NDMI_CLASSIFIED = m.add_ee_layer(ndmi_classified, ndmi_params, 'NDMI - Classified')

# adding NDVI layer to the map
NDVI = m.add_ee_layer(ndvi_masked, ndvi_params, 'NDVI')

# adding Classified NDVI layer to the map
NDVI_CLASSIFIED = m.add_ee_layer(ndvi_classified, ndvi_classified_params, 'NDVI - Classified')

# adding NDBI layer
NDBI = m.add_ee_layer(ndbi_masked, ndbi_params, 'NDBI')

# adding NDWI layer to the map
NDWI = m.add_ee_layer(ndwi_masked, ndwi_params, 'NDWI')

# adding contour lines to the map
CONTOURS = m.add_ee_layer(contours, contours_params, 'Contour lines')

#################### Layer controller ####################


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
        <title>Port Centre de Cherchell - Environmental Analysis</title>
        <link rel="stylesheet" href="//code.jquery.com/ui/1.12.1/themes/base/jquery-ui.css">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.1/css/all.min.css" integrity="sha512-MV7K8+y+gLIBoVD59lQIYicR65iaqukzvf/nwasF0nqhPay5w/9lJmVM2hMDcnK1OnMGCdVK+iQrJ7lzPJQd1w==" crossorigin="anonymous" referrerpolicy="no-referrer"/>
        <link rel="stylesheet" href="src/ui.css">
        <link rel="stylesheet" href="src/layers.css">
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
      <p>Cherchell Center Port - Environmental Study</p>
    </div>
  </div>
  
  <div id="ui-container" class="ui-container">

    <div class="project-source">
      <div class="project-logo">
          <a href="https://github.com/IndigoWizard/mega-port-environment/tree/develop" title="Go to repository" target="_blank">
            <i class="fa-brands fa-github" aria-hidden="true" id="icons"></i>
          </a>
      </div>

      <div class="project-info">
        <a href="https://github.com/IndigoWizard/mega-port-environment" title="Go to repository" target="_blank"><p  class="project-link"  id="icons">IndigoWizard/mega-port-environment</p></a>
        <div class="project-stats">
          <a href="https://github.com/IndigoWizard/mega-port-environment/releases/" target="_blank"><i class="fa-solid fa-tag" aria-hidden="true" id="icons"><span class="ghtext">  0.2.1</span></i></a>
          <a href="https://github.com/IndigoWizard/mega-port-environment/stargazers" target="_blank"><i class="fa-solid fa-star" aria-hidden="true" id="icons"><span class="ghtext"> Star it!</span></i></a>
          <a href="https://github.com/IndigoWizard/mega-port-environment/network/members" target="_blank"><i class="fa-solid fa-code-fork" aria-hidden="true" id="icons"><span class="ghtext"> Fork it!</span></i></a>
        </div>
      </div>
    </div>

    <div class="leaflet-control-layers-separator"></div>

      <div class='legend-title'>Legend</div>
      
      <div class="index-container">

        <div class='legend-scale' id="VECTOR">
          <ul class='legend-labels'>
            <li><span style="background:#3333330d;opacity:0.8;border: 2px dashed #f90000;"></span>Wilaya Administrative Borders.</li>
            <li><span style="background:#5555552e;opacity:0.8;border: 2px dashed #331D31;"></span>Municipalities Administrative Borders.</li>
            <li><span style='background:#9e57b0;opacity:0.8;'></span>Logistic industrial zones.</li>
            <li><span style='background:#0000ff;opacity:0.8;border: 4px #1a9a00 dotted;'></span>Construction sites.</li>
            <li><span style='background:#740118;opacity:0.8;'></span>Port main infrastructure.</li>
            <li><span style="border:3px dashed #1d1f2b;height:0;opacity:0.8;margin-top: 8px;"></span>Port futur highway.</li>
            <li><span style="border:3px dashed #ff0;height:0;opacity:0.8;background: #b8cee299;margin-top: 8px;"></span>Port futur highway - Suggested deviation.</li>
            <li><span style="border:2px solid #0070ec;height:0;opacity:0.8;margin-top: 8px;"></span>Shoreline.</li>
            <li><span style='background:#145B27;opacity:0.8;'></span>Forests - Affected Zones.</li>
            <li><span style='background:#0b8a03;opacity:0.8;'></span>Forests - Preserved Natural Zones.</li>
            <li><span style='background:#00c632;opacity:0.8;'></span>Farms and Aggricultural lands.</li>
            <li><span style="border:2px solid #75cff0;height:0;opacity:0.8;margin-top: 8px;"></span>Shoreline.</li>
            <li><span style="background:#75cff0eb;opacity:0.8;border: 2px solid #64aeca;"></span>Water bodies.</li>
          </ul>
        </div>

        <div class="leaflet-control-layers-separator"></div>

        <div class='legend-scale' id="NDVI">
            <h4>NDVI</h4>
            <ul class='legend-labels'>
                <li><span style='background:#a50026;opacity:0.8;'></span>0.0 - 0.15 : Built-up / rocky surface</li>
                <li><span style='background:#ed5e3d;opacity:0.8;'></span>0.15 - 0.25 : Bare soil</li>
                <li><span style='background:#f9f7ae;opacity:0.8;'></span>0.25 - 0.35 : Low vegeation</li>
                <li><span style='background:#fec978;opacity:0.8;'></span>0.35 - 0.45 : Crops</li>
                <li><span style='background:#9ed569;opacity:0.8;'></span>0.45 - 0.65 : High vegetation</li>
                <li><span style='background:#229b51;opacity:0.8;'></span>0.65 - 0.75 : Dense vegetation</li>
                <li><span style='background:#006837;opacity:0.8;'></span>> 0.75 : Forest</li>
            </ul>
        </div>

        <div class="leaflet-control-layers-separator"></div>

        <div class='legend-scale' id="NDMI">
            <h4>NDMI</h4>
            <ul class='legend-labels'>
                <li><span style='background:#d02f05;opacity:0.8;'></span>-1.0 - -0.1 : No vegetation/Bare soil/Water.</li>
                <li><span style='background:#fb7e21;opacity:0.8;'></span>-0.1 - 0 : Absent canopy cover</li>
                <li><span style='background:#eecf3a;opacity:0.8;'></span>0 - 0.1 : Low dry canopy cover</li>
                <li><span style='background:#a4fc3c;opacity:0.8;'></span>0.1 - 0.2 : Average canopy. High water stress</li>
                <li><span style='background:#32f298;opacity:0.8;'></span>0.2 - 0.3 : Mid-low canopy. Low water stress</li>
                <li><span style='background:#28bceb;opacity:0.8;'></span>0.3 - 0.4 : Mid-high canopy. Low water stress</li>
                <li><span style='background:#466be3;opacity:0.8;'></span> 0.4 - 0.5: High canopy. No water stress</li>
                <li><span style='background:#30123b;opacity:0.8;'></span>> 0.5 : Very high canopy. No water stress</li>
            </ul>
        </div>

        <div class="leaflet-control-layers-separator"></div>

        <div class='legend-scale' id="EVI">
            <h4>EVI</h4>
            <ul class='legend-labels'>
                <li><span style='background:#5628a1;opacity:0.8;'></span>Built-up area</li>
                <li><span style='background:#aaf6a2;opacity:0.8;'></span>Low vegetation over</li>
                <li><span style='background:#6bea5d;opacity:0.8;'></span>Medium vegetation cover</li>
                <li><span style='background:#22d33d;opacity:0.8;'></span>High vegetation cover</li>
                <li><span style='background:#219733;opacity:0.8;'></span>Dense vegetation cover</li>
            </ul>
        </div>

        <div class="leaflet-control-layers-separator"></div>

        <div class='legend-scale' id="NDBI">
            <h4>NDBI</h4>
            <ul class='legend-labels'>
                <li><span style='background:#B50044;opacity:0.8;'></span>Built-up area / Baren surface</li>
            </ul>
        </div>

        <div class="leaflet-control-layers-separator"></div>

        <div class="index-gradient">

          <div class="index-gradient-container">
            <div class='legend-scale' id="NDWI">
              <h4>NDWI</h4>
              <div class="inside-container">
                <div class="gradient-block">
                  <span id="ndwi-gradient"></span>
                </div>
                <div class="gradient-text">
                  <p>1</p>
                  <p>-1</p>
                </div>
              </div>
            </div>
          </div>

          <div class="index-gradient-container">
            <div class='legend-scale' id="DSM">
              <h4>DSM</h4>
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

## print downloadable link you can download image by click link in the console
#print (path)
folium.LayerControl(collapsed=False).add_to(m)

#################### LAYER GROUPS ####################
GroupedLayerControl(
    groups={
      'BASEMAPS LAYER': [basemap2, basemap3, basemap4, basemap5],
      'ADMINISTRATIVE LAYER': [WILAYA_ADMIN_INFO, MUNICIPALITIES_ADMIN_INFO],
      'NATURAL LAYER': [FORESTS_AFFECTED_INFO, FORESTS_PRESERVED_INFO, AGRO_FARM_LAND_INFO, SHORELINE, WATERWAYS_INFO],
      'INFRASTRUCTURE LAYER': [LOGISTIC_ZONES_INFO, PORT_INFRASTRUCTURE_INFO, CONSTRUCTION_ZONES_INFO, ROADS_INFO],
      'ENVIRONEMENTAL INDICIES': [TCI, HILLSHADE, ELEVATION, SLOPES, EVI, NDMI_CLASSIFIED, NDVI, NDVI_CLASSIFIED, NDBI, NDWI, CONTOURS],
    },
    exclusive_groups=False,
    collapsed=False
).add_to(m)


# Generating a file for the map and setting it to open on default browser
m.save('webmap.html')

# Opening the map file in default browser on execution
webbrowser.open('webmap.html')