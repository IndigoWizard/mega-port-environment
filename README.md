#  Mega port project - Environmental study (imagery and data analysis)
##### TL;DR:
> This serves as the main repo for the satellite imagery analysis and cartography project for the Algerian mega port project in *El-Hamdania, Cherchell, Tipaza*.

Open for contribution! (I see you, hacktoberfest enthousiasts 👀)

Project website: [CHERCHELL CENTER PORT - ENVIRONEMENTAL STUDY](https://indigowizard.github.io/mega-port-environment/webmap.html)

**IMPORTANT NOTE:** ⚠️

The Earth Engine token expires every 48H, so after that the layers won't show up and the webapp may seem like not working, it's not, it's just that I don't update the token from my personal google earth engine account unless you need a live demo, otherwise check the preview section.

# [Table of Content](#table-of-content)
- [Introduction](#introduction)
- [Features](#features)
- [Preview](#preview)
- [User and installation guide](#user-and-installation-guide)
- [Contribution](#contribution)
- [Credit](#credit)

## Introduction:
This project is meant to create a script(s) that help analyse different satellite imagery layers to calculate various environmental indices and generate land-surface data that can help study the environmental impact in the mega port project's area.

## Features:
A breif list of features supported in this webapp (see [release note](https://github.com/IndigoWizard/mega-port-environment/releases) for further details):
- Various vector-based thematic basemaps (OSM, topography, terrain... etc.).
- Various raster-based high-resolution basemaps from different services for better comparision between app results and real life on-site data (ESRI, Google).
- Vector based layers in GeoJSON format representing the various spatial features of the port project, both natural and artificial. E.g: 
  - Artificial: infrastructure, current construction zones, future and planned logistical and industrial zones... etc.
  - Natural: Forests affected by the project plans, forests preserved in the project plan, farms and agricultural lands affected, waterways and water bodies... etc.
- Interactive vector layers: Various data on every single entity of the different vector layers as pop-ups on hover (including highlight hover effect for better visibility), e.g: (surface area, administrative jurisdiction, project status, species availble whithin the area... etc).
- Computed raster-based geographical data from satellite imagery (Sentinel-2, Landsat... etc).
- Various calculated topography data (elevation, slopes, DEM... etc). 
- Imagery analysis of computed environmental indices: NDVI, NDWI, classified computed raster data... (more indicies can be added).
- A collapsible layer panel for optimal view.
- A draggable legend window.
- Adraggable project stats and links.
- A mini map

More features will be added in the future (contribution is welcome!).
## Preview
![demo-preview](https://www.pixenli.com/image/gKY-A2Fd)

A layered static preview of the multiple availble layers within the map currently.

## User and installation guide
**For end users:**

You can simply access the website of the project as it is here: [Project website](https://indigowizard.github.io/mega-port-environment/webmap.html)

**For devs:**

The project uses various technologies to help generate and analyse geographical data, using **GIS** and related tech.
Main tech used in the project:
- Folium (data visualization)
- Earth Engine (geospatial processing service)

If you want to develop this project or or contribute to it, you can fork it and clone it then follow configuration steps:

Google Earth Engine:
1. To use this script, you must first [sign up](https://earthengine.google.com/signup/) for a [Google Earth Engine](https://earthengine.google.com/) account.
2. Install [gcloud CLI](https://cloud.google.com/cli) for the Google Earth Engine account authentication.
3. Install the rest of project dependency from this file: `requirement.txt`

### Using Anaconda (recomanded):
#### Method 1: The fastest and cleanest method:
The project folder contains two following files, use one of the two:
- `environment.yml` Use this file to recreate the the very same developement environement (with it's dependencies) I used for this project called "geospatial":

From console: `conda env create -f environment.yml`

Or use Anaconda Navigator (UI) and select path to the `environment.yml` file, anaconda does the rest.

That's it, you're good to go!

#### Method 2: If you prefer to start a new anaconda environement:

1. Make a conda virtual environment, call it "geospatial":

`conda create --name geospatial`

2. Activate geospatial environement:

`conda activate geospatial`

3. Install folium:

`conda install -c conda-forge folium `

4. Install [earthengine-api](https://github.com/google/earthengine-api) from conda forge within geospatial env:

`conda install -c conda-forge earthengine-api` 

That's it, you're good to go!

### Using pip: 
- Install folium: `pip install folium`
- Install [earthengine-api](https://github.com/google/earthengine-api): `pip install earthengine-api`


## Contribution:
The project is open for contribution where you can help improve, fix or add features. Please 
refer to [CONTRIBUTING.md](./.github/CONTRIBUTING.md) for more details and guidelines.

It's important that you check the **issues** section before:
- **Reporting a bug**
- **Fixing a bug**
- **Requesting features**
- **Implementing features**
- **Writing documentation**

If no issue alrady exists regarding your contribution subject you may open a new issue and get to work.

#### Credit
Project by Ahmed I. Mokhtari.