import pandas as pd
import numpy as np
import geohash
import argparse
import os
import re

# Description
description="""
Tags report containing lat/lon values with associated
geohash IDs per input geohash precision level.
Example command: python geohash_pandas_agg.py --ghp 8 --udid 1 --lat 2 --lon 3
"""

# User arguments
parser=argparse.ArgumentParser(description=description)
parser.add_argument('--ghp', type=int, help="Geohash precision level")
parser.add_argument('--udid', type=int, help="Column number with Device ID")
parser.add_argument('--lat', type=int, help="Column number with Latitude coordinate value")
parser.add_argument('--lon', type=int, help="Column number with Longitude coordinate value")
parser.add_argument('--header', action='store_true', help="Use if report has headers")
args=parser.parse_args()



file_dir = os.listdir('.')
files = []
for item in file_dir:
    if item.endswith('tsv.gz'):
        files.append(item)

ghp = args.ghp

for file_ in files:
    filename_pre = file_.replace('tsv.gz', '')
    adm_div = file_.split('_', 1)[0]
    filename_count = adm_div + f'_geohash_device_count_gh{ghp}.tsv'

    if args.header:
        rep = pd.read_csv(file_, sep='\t',
                   compression='gzip',
                   skiprows=1,
                   header=None)

        rep.rename(columns={args.udid-1: 'UDID',
                            args.lat-1: 'Lat',
                            args.lon-1: 'Lon'},
                            inplace=True)

    else:
        rep = pd.read_csv(file_, sep='\t',
                    compression='gzip',
                    header=None)

        rep.rename(columns={args.udid-1: 'UDID',
                            args.lat-1: 'Lat',
                            args.lon-1: 'Lon'},
                            inplace=True)


    rep['geohash'] = rep.apply(lambda row: geohash.encode(row['Lat'],
                                                      row['Lon'],
                                                      precision=ghp),
                                                      axis = 1)

    rep_counts = pd.DataFrame(rep.groupby('geohash')['UDID'].nunique() \
                              .reset_index(name='device_count').sort_values(by='device_count',
                                                                            ascending=False))

    print('Stats on [{0}]:'.format(adm_div))
    print('Raw Grid # of Rows: {0}'.format(rep_counts.shape[0]))
    print('Mean of Device Counts: {0}'.format(rep_counts['device_count'].mean()))
    print('Maximum of Device Counts: {0}'.format(rep_counts['device_count'].max()))
    print('\n')

    rep_counts.to_csv(filename_count,
                       sep='\t',
                       index=False,
                       header=None)
