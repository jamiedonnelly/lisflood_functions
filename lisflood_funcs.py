from numpy.lib.arraysetops import isin
import pandas as pd
import numpy as np 
import os 
import rasterio as rio 

## Create boundary conditions 

def create_bdy(fname: str, locations: list, series: list, unit: str, interval: int) -> None: 
    """
        Function to take a collection of data and produce a .bdy file to parameterise lislfood-fp 
        simulation boundary conditions 
    Args:
        fname (str): Name of .bdy file to be created 
        locations (list): List of locations corresponding to values in the .bci file i.e., ['bc1','bc2',...]
        data_series (list): List of lists representing time-varying boundary conditions i.e., 
                            specifying time-varying water elevation values or flow discharge. Must be a nested list even if only one bci.                           
        unit (str): String specifying time unit i.e., 'seconds' or 'minutes' 
        interval (int): Int specifying time interval to be combined with the units. A unit of 'seconds' 
                        and an interval of '60' means each value in the series is recorded 60 seconds apart.
                        The value specified will be applied in the simulation for 60 seconds.
    """
    assert len(locations) == len(series)
    file_name = fname+".bdy"
    with open(file_name,"w") as f:
        f.write("first line to be ignored.")
        for i in range(len(series)):
            f.write("\n"+locations[i])
            f.write("\n\t"+str(len(series[i]))+"\t"+unit)
            for j in range(len(series[i])):
                f.write("\n"+str(series[i][j])+"\t\t"+str(interval*j))
                               
## run simulations 

def run_sim(directory: str) -> None:
    """
        Function to run each lisflood-fp simulation from collection of folders in a 
        directory containing all data. 

    Args:
        directory (str): String specifying the full directory path where simulation files can be found. 
                         i.e., C:/Users/user/base/simulations
    """
    folders = [os.path.join(directory, _) for _ in os.listdir(directory)]
    for folder in folders:
        par_file = "".join([_ for _ in os.listdir(folder) if ".par" in _])
        try:
            os.system("cd "+folder+" & "+"lisflood.exe -v "+par_file)
        except:
            print("Failed to run .par file in directory "+folder)

## Collect depths 

def collect_depths(directory: str, resname: str, initialisation_steps: int = None, depth_threshold: float = None) -> np.array: 
    """
        Function to collect all water depths from .wd files generated from a sample of simulations. 

    Args:
        directory (str): String specifying the full directory path where simulation files can be found. 
                         i.e., C:/Users/user/base/simulations
        resname (str): String specifying the name of the subdirectory in each simulation folder where results are stored.
                       This is specified in the .par file as 'dirroot'. 
        initialisation_steps (int): Integer stating how many .wd files to ignore to allow for model initialisation i.e., initialisation_steps = 5 discards the first
                                    5 .wd files in collecting the results. 
        depth_threshold (float): Float value specifying a threshold to be applied to discard water depth values below. 
        
    Returns:
        np.array: 2D Numpy array representing the water depths at each time step for all simulations. Array of shape (N x M) where N is total time steps across 
        simulations and M is flattened size of the 2D array representing study output size. 
    """
    files = [os.path.join(directory, _) for _ in os.listdir(directory)]
    depths = []
    for f in files:
        res_path = os.path.join(f, resname)
        results = [os.path.join(res_path,i) for i in os.listdir(res_path) if ".wd" in i][initialisation_steps:]
        for res in results:
            data = rio.open(res).read(1)
            dt = data.flatten()
            dt[dt<=depth_threshold]=0
            depths.append(dt)
    return np.array(depths)    
    
# read raster files and conver to numpy arrays 

def read_raster(fname: str) -> np.array:
    """
        Function to convert raster in .ascii format into numpy 2D nump arrays. 

    Args:
        fname (str): Full path for any file with a .ascii extension 

    Returns:
        np.array: Returns an numpy array representing the data of the raster file. 
    """
    data=[]
    with open(fname,"r") as f:
        lines = f.readlines()
        for line in lines[6:]:
            dt = [round(float(_),3) for _ in line.split()]
            data.append(dt)
    return np.array(data)


def write_raster(data: np.array, fname: str, cellsize: int, xllcorner: int, yllcorner: int, NODATA_value: int) -> None:
    """
       Function to write 2D numpy arrays to raster files in .ascii format. 

    Args:
        data (np.array): 2D numpy array containing raster data. 
        fname (str): Filename to be appended with a '.ascii' file extension.
        cellsize (int): Integer denoting 
        xllcorner (int): Integer denoting Esri grid data parameter denoting the western (left) x-coordinate i.e., easting coordinate
        yllcorner (int): Integer denoting Esri grid data parameter denoting the southern (bottom) y-coordinate i.e., northing coordinate
        NODATA_value (int): Integer value that is to be regarded as 'missing' or 'not applicable' and will not be read in GIS software.
    """
    assert isinstance(data, (np.ndarray))
    with open(fname+".ascii", "w") as f:
        f.write("ncols\t\t"+str(data.shape[1])+"\n")
        f.write("nrows\t\t"+str(data.shape[0])+"\n")   
        f.write("xllcorner\t"+str(xllcorner)+"\n")
        f.write("yllcorner\t"+str(yllcorner)+"\n")
        f.write("cellsize\t"+str(cellsize)+"\n")
        f.write("NODATA_value\t"+str(NODATA_value)+"\n")
        for i in range(data.shape[0]):
            f.write(" "+" ".join([str(i) for i in data[i,:]])+"\n")
    print(fname+".ascii successfully created")
    
