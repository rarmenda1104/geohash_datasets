from h3 import h3
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point, LineString, Polygon

def add_geometry(row):
    points = h3.h3_to_geo_boundary(
      row['h3'],True)
    return Polygon(points)

def lat_lng_to_h3(row):
    return h3.geo_to_h3(
      row.geometry.y, row.geometry.x, h3_level)

# Read in csv and convert dataset into geodataframe to process data
cel_data = pd.read_csv('study_tsv.tsv.gz',sep = '\t')
cel_gdf = gpd.GeoDataFrame(
    cel_data, geometry=[Point(xy) for xy in zip(cel_data['Common Evening Long'], cel_data['Common Evening Lat'])])

# Convert lat-long to h3 code
h3_level = 8
cel_gdf['h3'] = cel_gdf.apply(lat_lng_to_h3, axis=1)

# Aggregate counts of UDIDs per h3 code
counts = cel_gdf.groupby(['h3'])['Hashed Ubermedia Id'].agg('count').to_frame('count').reset_index()

# Convert h3 code to polygon
counts['geometry'] = counts.apply(add_geometry,axis = 1)

# Cast counts pandas df to geodataframe for output
gdf = gpd.GeoDataFrame(counts,geometry = 'geometry',crs = "EPSG:4326")

# Output data as geojson
output_filename = 'grid_counts_test_raw.json'
gdf.to_file(driver='GeoJSON', filename=output_filename)