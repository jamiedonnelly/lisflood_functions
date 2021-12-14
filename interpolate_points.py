import numpy as np
import pandas as pd

"""
    Function to create a continous boundary condition by interpolating a series of points. 
"""

def interpolate_coordinates(coords: pd.DataFrame) -> pd.DataFrame: 
    xp=[]
    yp=[]
    for i in range(1,len(coords)):
        x1, y1 = coords.iloc[i-1,0], coords.iloc[i-1,1]
        x2, y2 = coords.iloc[i,0], coords.iloc[i,1]
        if (x2-x1)>(y2-y1):
            num = x2-x1
        else:
            num = y2-y1
        xp.append([int(i) for i in np.linspace(x1,x2,num)])
        yp.append([int(i) for i in np.linspace(y1,y2,num)])
    x = np.concatenate([i for i in xp])
    y = np.concatenate([i for i in yp])
    df = pd.DataFrame(columns=['easting','northing'],index=[i for i in range(len(x))])
    df['easting']=x
    df['northing']=y
    return df