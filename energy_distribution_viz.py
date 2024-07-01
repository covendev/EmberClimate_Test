import folium
import pandas as pd
import branca.colormap as cm

# Load data (replace with your CSV file path)
data = pd.read_csv('Downloads/yearly_full_release_long_format.csv', encoding='utf-8')

# Filter data for year 2023 and relevant variables, excluding 'ASEAN' and 'World'
clean_variables = ['Clean', 'Wind', 'Hydro', 'Wind and Solar', 'Solar', 'Other Renewables', 'Bioenergy', 'Renewables']
fossil_variables = ['Fossil', 'Other Fossil', 'Coal', 'Gas', 'Gas and Other Fossil']
nuclear_variables = ['Nuclear']

data_2023_clean = data[(data['Year'] == 2023) & (data['Variable'].isin(clean_variables)) & (~data['Area'].isin(['ASEAN', 'World']))]
data_2023_fossil = data[(data['Year'] == 2023) & (data['Variable'].isin(fossil_variables)) & (~data['Area'].isin(['ASEAN', 'World']))]
data_2023_nuclear = data[(data['Year'] == 2023) & (data['Variable'].isin(nuclear_variables)) & (~data['Area'].isin(['ASEAN', 'World']))]

# Aggregate data by Area and sum the counts
clean_areas = data_2023_clean.groupby('Area')['Value'].sum().reset_index()
fossil_areas = data_2023_fossil.groupby('Area')['Value'].sum().reset_index()
nuclear_areas = data_2023_nuclear.groupby('Area')['Value'].sum().reset_index()

# Initialize the map centered on a specific location
m = folium.Map(location=[0, 0], zoom_start=2)

# Function to create a GeoJson layer with color-coded regions
def create_geojson_layer(counts, color_scale, legend_name):
    def style_function(feature):
        area_name = feature['properties']['name']
        if area_name in counts['Area'].values:
            count = counts[counts['Area'] == area_name]['Value'].iloc[0]
            return {
                'fillColor': color_scale(count),
                'color': 'black',
                'weight': 0.2,
                'dashArray': '5, 5',
                'fillOpacity': 0.7,
            }
        else:
            return {
                'fillColor': 'transparent',
                'color': 'black',
                'weight': 0.2,
                'dashArray': '5, 5',
                'fillOpacity': 0.0,
            }

    geojson = folium.GeoJson(
        'https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json',
        style_function=style_function,
        name=legend_name
    )

    return geojson

# Create color scales with more gradient colors
clean_color_scale = cm.LinearColormap(['#edf8fb', '#ccece6', '#99d8c9', '#66c2a4', '#41ae76', '#238b45', '#005824'],
                                      vmin=clean_areas['Value'].min(),
                                      vmax=clean_areas['Value'].max())
fossil_color_scale = cm.LinearColormap(['#feedde', '#fdbe85', '#fd8d3c', '#e6550d', '#a63603'],
                                       vmin=fossil_areas['Value'].min(),
                                       vmax=fossil_areas['Value'].max())
nuclear_color_scale = cm.LinearColormap(['#fff9c4', '#fff176', '#ffeb3b', '#fdd835', '#fbc02d'],
                                       vmin=nuclear_areas['Value'].min(),
                                       vmax=nuclear_areas['Value'].max())

# Create GeoJson layers for clean, fossil, and nuclear energy
clean_layer = create_geojson_layer(clean_areas, clean_color_scale, 'Clean Energy Consumption (2023)')
fossil_layer = create_geojson_layer(fossil_areas, fossil_color_scale, 'Fossil Energy Consumption (2023)')
nuclear_layer = create_geojson_layer(nuclear_areas, nuclear_color_scale, 'Nuclear Energy Consumption (2023)')

# Add GeoJson layers to the map
clean_layer.add_to(m)
fossil_layer.add_to(m)
nuclear_layer.add_to(m)

# Add LayerControl to toggle layers
folium.LayerControl().add_to(m)

# Add color legends
clean_color_scale.caption = 'Clean Energy Consumption (2023)'
fossil_color_scale.caption = 'Fossil Energy Consumption (2023)'
nuclear_color_scale.caption = 'Nuclear Energy Consumption (2023)'
clean_color_scale.add_to(m)
fossil_color_scale.add_to(m)
nuclear_color_scale.add_to(m)

# Save the map
m.save('clean_values_map.html')
