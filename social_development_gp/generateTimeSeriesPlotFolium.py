# script to be run periodically to generate map data of the fraction of tweets containing covid related info

import sys,folium,os
from folium import plugins
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def map_points(df, lat_col='latitude', lon_col='longitude', zoom_start=6, \
                plot_points=False, pt_radius=0.0000000001, \
                draw_heatmap=False, heat_map_weights_col=None, \
                heat_map_weights_normalize=True, heat_map_radius=10):
    """Creates a map given a dataframe of points. Can also produce a heatmap overlay

    Arg:
        df: dataframe containing points to maps
        lat_col: Column containing latitude (string)
        lon_col: Column containing longitude (string)
        zoom_start: Integer representing the initial zoom of the map
        plot_points: Add points to map (boolean)
        pt_radius: Size of each point
        draw_heatmap: Add heatmap to map (boolean)
        heat_map_weights_col: Column containing heatmap weights
        heat_map_weights_normalize: Normalize heatmap weights (boolean)
        heat_map_radius: Size of heatmap point

    Returns:
        folium map object
    """

    ## center map in the middle of points center in
    middle_lat = df[lat_col].median()
    middle_lon = df[lon_col].median()

    curr_map = folium.Map(location=[middle_lat, middle_lon],
                          zoom_start=zoom_start)

    # add points to map
    if plot_points:
        for _, row in df.iterrows():
            folium.CircleMarker([row[lat_col], row[lon_col]],
                                radius=pt_radius,
#                                popup=row['name'],
                                fill_color="#3db7e4", # divvy color
                               ).add_to(curr_map)

    # add heatmap
    if draw_heatmap:
        # convert to (n, 2) or (n, 3) matrix format
        if heat_map_weights_col is None:
            cols_to_pull = [lat_col, lon_col]
        else:
            # if we have to normalize
            if heat_map_weights_normalize:
                df[heat_map_weights_col] = \
                    df[heat_map_weights_col] / df[heat_map_weights_col].sum()

            cols_to_pull = [lat_col, lon_col, heat_map_weights_col]

        stations = df[cols_to_pull].as_matrix()
        curr_map.add_children(plugins.HeatMap(stations, radius=heat_map_radius))

    return curr_map

def generateBaseMap(default_location=[-6.393944, 106.802129], default_zoom_start=6):
    base_map = folium.Map(location=default_location, control_scale=True, zoom_start=default_zoom_start)
    return base_map


data_df = pd.read_csv("locations_over_time1.txt",sep="\t")
data_df['frac_corona'] = 100*data_df['frac_corona']
base_map = generateBaseMap()
data_df.date = pd.to_datetime(data_df.date, format='%Y/%m/%d %H:%M:%S')
data_df['day'] = data_df['date'].dt.date;#.apply(lambda x: x.day)
df_day_list = []; date_index = [];
for day in data_df.day.sort_values().unique():
    date_index.append(str(day));
    df_day_list.append(data_df.loc[data_df.day == day, ['latitude', 'longitude', 'frac_corona']]
                       .groupby(['latitude', 'longitude']).sum().reset_index().values.tolist())

from folium.plugins import HeatMapWithTime

x = HeatMapWithTime(df_day_list, radius=5, index=date_index, auto_play=True,
                    gradient={0.2: 'blue', 0.4: 'lime', 0.6: 'orange', 1: 'red'}, 
                    min_opacity=0.5, max_opacity=0.8, use_local_extrema=True);

x.add_to(base_map)

base_map.save('indonesia_over_time.html')
#os.system("scp -i ~/.ssh/wb_indonesia_data_instance.pem indonesia_over_time.html ubuntu@ec2-13-57-55-178.us-west-1.compute.amazonaws.com:/var/www/html/");
os.system('mv indonesia_over_time.html /var/www/html/');

