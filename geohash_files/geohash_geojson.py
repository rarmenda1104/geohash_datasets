"""
example run: python geohash_geojson.py file.tsv

    1. Make sure agg count file is 2 columns
    2. Agg count file should not have headers
"""

import pandas as pd
import geojson
import sys
from geojson import Polygon, FeatureCollection, Feature
import geohash

file_name = sys.argv[1]
# set precision
precision = 7

def is_geohash_in_bounding_box(current_geohash, bbox_coordinates):
    """Checks if the box of a geohash is inside the bounding box

    :param current_geohash: a geohash
    :param bbox_coordinates: bounding box coordinates
    :return: true if the the center of the geohash is in the bounding box
    """

    coordinates = geohash.decode(current_geohash)
    geohash_in_bounding_box = (bbox_coordinates[0] < coordinates[0] < bbox_coordinates[2]) and (
        bbox_coordinates[1] < coordinates[1] < bbox_coordinates[3])
    return geohash_in_bounding_box


def build_geohash_box(gh, ghc):
    """Returns a GeoJSON Polygon for a given geohash

    :param current_geohash: a geohash
    :return: a list representation of th polygon
    """

    b = geohash.bbox(gh)
    feature = Feature(geometry=Polygon([[(b['w'], b['s']),
                                         (b['w'], b['n']),
                                         (b['e'], b['n']),
                                         (b['e'], b['s'],),
                                         (b['w'], b['s'])]]),
                      properties={'name': gh, 'Device Count': ghc})
    return feature


def write_geohash_layer(geohashes, output_name):
    """Writes a grid layer based on the geohashes

    :param geohashes: a list of geohashes
    """

    layer = FeatureCollection([build_geohash_box(gh, ghc)
                               for (gh, ghc) in geohashes['new_col']])
    with open('{}.geojson'.format(output_name), 'wb') as f:
        f.write(geojson.dumps(layer, sort_keys=True).encode('utf-8'))

print("reading table...")
counts = pd.read_table(file_name, header=None)
print("zipping...")
counts['new_col'] = list(zip(counts[0], counts[1]))
output_name = file_name.replace('.tsv', '_grid')

# For Nike Processing
#output_name = (file_name.split('_', 1)[1].replace('.tsv', '') + '_{0}'.format(file_name.split('_')[0])).replace('-', '_')
print('writing geojson...')
write_geohash_layer(counts, output_name)
print('Done!')
