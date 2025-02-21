# grid_sorter
## Setup:
### Download [PH_MUN_MAP](https://github.com/Schwarz08/custom_shp_files.git) and extract
## Input:
### All input variables can be found under main.
### grid_folder: Directory containing grid-level csv files to be sorted.
### lon_col: Longitude Column of the grid-level csv files
### lat_col: Latitude Column of the grid-level csv files
### target_border: The geographic border that the grid-level csv files will be sorted by.
### threshold_dict: Thresholds of the data columns of the grid-level csv files
### shp_file_path: File path of the shp file to be used.
## Output:
### Output file will be named as sorted_grid.csv
## Notes:
### You can change the number of workers multiprocessing will use.
### It is also possible to switch between multiprocessing and standard looping.
### It is recommended to use [csv_splitter](https://github.com/Schwarz08/csv_tools.git) to make the csv files smaller.
