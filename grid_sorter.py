import pandas as pd
import geopandas as gpd
import time as timer
from multiprocessing import Pool
from grid_sorter_support import import_border_gdf, create_calc_input, convert_to_numeric, aggregate_data

'''
Created by Jan Kyle Lewis T. Nolasco
'''

class Grid:
    def __init__(self, grid_file_path, lon_col, lat_col, target_border, threshold_dict):
        #define file_path
        self.file_path = grid_file_path

        #define target border
        self.target_border = target_border

        #ddefine threshold
        self.threshold_dict = threshold_dict

        #define longitude & latitude columns
        self.lon_col = lon_col
        self.lat_col = lat_col

        #import as pandas df
        usecols = [lon_col, lat_col]+list(self.threshold_dict.keys())
        df = pd.read_csv(self.file_path, usecols=usecols)

        #convert to geopandas gdf
        self.gdf = gpd.GeoDataFrame(
            df, geometry=gpd.points_from_xy(df[self.lon_col], df[self.lat_col]), crs=4326)

    def Sort(self, border_gdf):
        temp_grid = gpd.sjoin_nearest(self.gdf.to_crs(crs=3857),
                                        border_gdf.to_crs(crs=3857),
                                        how='left').to_crs(crs=4326)
        #sort by border
        temp_grid = temp_grid.sort_values(by=self.target_border)
        #only get the first matching entry & resort index
        self.sorted_grid = temp_grid[~temp_grid.index.duplicated(keep='first')]

    def Aggregate(self):
        agg_dict = {
            self.target_border: ["count"]
        }

        #create intitial agg_grid based on grid count
        self.agg_grid = aggregate_data(self.sorted_grid.copy(deep=True), self.target_border, agg_dict)
        self.agg_grid = self.agg_grid.rename(columns={self.target_border+" [count]": "Grid [count]"})

        #loop through all the threshold
        for threshold in self.threshold_dict:
            threshold_value = self.threshold_dict[threshold]
            agg_dict = {
                threshold: ["count"]
            }
            #only get those values above the threshold
            temp_grid = self.sorted_grid.drop(
                self.sorted_grid.loc[self.sorted_grid[threshold] <= threshold_value].index)
            #aggregate threshold filtered grid data
            temp_agg_grid = aggregate_data(temp_grid.copy(deep=True), self.target_border, agg_dict)
            #join aggregated threshold filtered data to original grid data
            self.agg_grid = self.agg_grid.join(temp_agg_grid.set_index(self.target_border), on=self.target_border)
            #rename joineded column
            new_col_name = f"{threshold}>{threshold_value} [count]"
            self.agg_grid = self.agg_grid.rename(
                columns={threshold + " [count]": new_col_name})
            #fill blank values with 0
            self.agg_grid[new_col_name] = self.agg_grid[new_col_name].fillna(0)

def grid_sort(grid_sort_input):
    print("Current: ", grid_sort_input[0])

    #parse input
    #create Grid Object
    grid = Grid(grid_sort_input[0], grid_sort_input[1], grid_sort_input[2], grid_sort_input[3], grid_sort_input[4])
    border_gdf = import_border_gdf(grid_sort_input[5])

    #sort grid by border
    grid.Sort(border_gdf)
    #aggregate grid by border
    grid.Aggregate()

    return grid.agg_grid.copy(deep=True)

def pool_calculation(calc_input, target_border, threshold_dict, n_workers):
    #print(calc_input)
    with Pool(processes=n_workers) as pool_handler:
        pool_result = pool_handler.map(grid_sort, calc_input)

    #concat results from multiprocessing
    agg_pool = pd.concat(pool_result)
    agg_pool = agg_pool.reset_index(drop=True)

    print("Aggregating Results . . . ")
    #create agg dict for final aggregation
    agg_dict = {
        "Grid [count]": ["sum"]
    }
    for threshold in threshold_dict:
        col_name = f"{threshold}>{threshold_dict[threshold]} [count]"
        agg_dict[col_name] = ["sum"]

    agg_pool_result = aggregate_data(agg_pool, target_border, agg_dict)

    #agg_pool_result.to_csv("agg_pool_result_test.csv", index=False)

    return agg_pool_result

def loop_calculation(calc_input, target_border, threshold_dict):
    loop_result = []
    for grid_sort_input in calc_input:
        grid_agg = grid_sort(grid_sort_input)
        loop_result.append(grid_agg)

    #concat results from multiprocessing
    agg_loop = pd.concat(loop_result)
    agg_loop = agg_loop.reset_index(drop=True)

    print("Aggregating Results . . . ")
    #create agg dict for final aggregation
    agg_dict = {
        "Grid [count]": ["sum"]
    }
    for threshold in threshold_dict:
        col_name = f"{threshold}>{threshold_dict[threshold]} [count]"
        agg_dict[col_name] = ["sum"]

    agg_loop_result = aggregate_data(agg_loop, target_border, agg_dict)

    #agg_loop_result.to_csv("agg_loop_result_test.csv", index=False)

    return agg_loop_result

def main():
    grid_folder = "grid_results"
    lon_col = "Longitude"
    lat_col = "Latitude"
    target_border = "PSGC"
    threshold_dict = {
        "RSRP": -105,
        "SINR": 10
    }

    shp_file_path = "PH_MUN_MAP\\PH_MUN_MAP.shp"
    calc_input = create_calc_input(grid_folder, lon_col, lat_col, target_border, threshold_dict, shp_file_path)

    calc_output = pool_calculation(calc_input, target_border, threshold_dict, 8)
    #calc_output = loop_calculation(calc_input, target_border, threshold_dict)

    calc_output.to_csv("sorted_grid.csv", index=False)

if __name__ == "__main__":
    start = timer.time()
    main()
    end = timer.time()
    total_time = (end - start) / 60
    print(f"Elapsed Time: {total_time} mins")