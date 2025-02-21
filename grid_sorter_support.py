import os
import geopandas as gpd
import pandas as pd

'''
Created by Jan Kyle Lewis T. Nolasco
'''

def import_border_gdf(shp_file_path):
    border_gdf = gpd.read_file(shp_file_path)

    #set crs
    border_gdf = border_gdf.set_crs(crs=4326)

    return border_gdf

def create_calc_input(grid_folder, lon_col, lat_col, target_border, threshold_dict, shp_file_path):
    #create empty list to store calc inputs
    calc_input = []

    #create Grid object for each grid_file
    for grid_file_name in os.listdir(grid_folder):
        grid_file_path = os.path.join(grid_folder, grid_file_name)
        #append to calc input
        calc_input.append([grid_file_path, lon_col, lat_col, target_border, threshold_dict, shp_file_path])

    return calc_input

def convert_to_numeric(data, numeric_dic):
    #loop through col_list to convert to numeric
    for col in numeric_dic:
        precision = numeric_dic[col]
        #print(col, precision)
        #check if there is a downcast precision specified
        if precision is None:
            data[col] = pd.to_numeric(data[col], errors='coerce')

        else:
            data[col] = pd.to_numeric(data[col], errors='coerce', downcast=precision)

    return data

def aggregate_data(data, agg_lvl_col, agg_dict):
    #set up new dataframe for output
    data_agg=pd.DataFrame(data=data[agg_lvl_col].unique(), columns=[agg_lvl_col])

    #loop through columns to aggregate
    for col in agg_dict:
        #loop through aggfuncs
        for agg_func in agg_dict[col]:

            # special process for "count", "nunique", "list" aggregation, these need a new column to work
            if agg_func == "count":
                new_col = col + " [count]"
                data[new_col] = data[col]
                agg_calc = pd.pivot_table(data, values=new_col, index=agg_lvl_col,  aggfunc=agg_func)
            elif agg_func == "nunique":
                new_col = col + " [nunique]"
                data[new_col] = data[col]
                agg_calc = pd.pivot_table(data, values=new_col, index=agg_lvl_col, aggfunc=agg_func)
            elif agg_func == "list":
                new_col = col + " [list]"
                data[new_col] = data[col]
                agg_calc = pd.pivot_table(data.dropna(subset=[col]), values=new_col, index=agg_lvl_col,
                                      aggfunc=pd.unique)
            else:
                agg_calc = pd.pivot_table(data, values=col, index=agg_lvl_col,
                                               aggfunc=agg_func)
                agg_calc.rename(columns={col: col+" ["+agg_func+"]"}, inplace=True)

            #add calculated aggregation to output dataframe
            data_agg = data_agg.join(agg_calc, on=agg_lvl_col)

    return data_agg