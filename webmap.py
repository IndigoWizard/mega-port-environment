# importing all project related libraries
import folium
import webbrowser

# setting up the main map for the project
m = folium.Map(location = [36.6193, 2.2547], zoom_start = 15, control_scale = True)

# generating a file for the map and setting it to open on default browser
m.save('web-map.html')
webbrowser.open('web-map.html')