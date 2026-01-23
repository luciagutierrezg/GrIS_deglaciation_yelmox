import xarray as xr
import numpy as np
import pandas as pd
import glob
import os

# ----------------------------------------------------------------------------
# Paths
# ----------------------------------------------------------------------------
path_ensemble="../../ensemble_reduced/*"
path_schumacher="../../FesmData/Schumacher2018_GIA_GrIS/data/schumacher2018_GR.nc"
path_output="../output"

# ----------------------------------------------------------------------------
# processing ensemble (uplift rates in the Schumacher stations)
# ----------------------------------------------------------------------------
schu=xr.open_dataset(path_schumacher)
sim_paths = sorted(glob.glob(path_ensemble))
def gia(x,y,sim):
    sim=sim.sel(xc=x,yc=y,method='nearest')
    sim0=sim.sel(time=0)
    sim1=sim.sel(time=-200)
    v_vert=((sim1.z_bed-sim0.z_bed)/200)*1e3 # mm/year
    return sim.xc.values,sim.yc.values,v_vert.values

v_ensamble = []   
valid_sim_indices = []   

for i, sim_path in enumerate(sim_paths):

    file_path = os.path.join(sim_path, "yelmo2D_reduced.nc")
    n_sim = int(os.path.basename(sim_path))
    try:
        yelmo = xr.open_dataset(file_path)
    except FileNotFoundError:
        print(f"[ERROR] No se encontró el archivo: {file_path}. Se omite esta simulación.")
        continue
    except Exception as e:
        print(f"[ERROR] No se pudo abrir {file_path}: {e}. Se omite esta simulación.")
        continue
    
    v_all = []

    for sta in schu.station.values: 
        location = schu.sel(station=sta)
        x = float(location.xc)
        y = float(location.yc)
        _,_,v = gia(x, y, yelmo)  
        v_all.append(v)
    
    v_all = np.array(v_all, dtype=float)
    
    v_ensamble.append(v_all)
    valid_sim_indices.append(n_sim)

x_all = []
y_all = []

for sta in schu.station.values: 
    location = schu.sel(station=sta)
    x = float(location.xc)
    y = float(location.yc)
    x1,y1,_ = gia(x, y, yelmo)  
    x_all.append(x1)
    y_all.append(y1)

x_all = np.array(x_all, dtype=float)
y_all = np.array(y_all, dtype=float)

v_ensamble = np.stack(v_ensamble, axis=0)

ds_ensemble = xr.Dataset(
    data_vars={
        "v_vert": (("sim", "station"), v_ensamble)
    },
    coords={
        "sim": np.array(valid_sim_indices),
        "station": schu.station.values,
        "xc": (("station"), x_all),
        "yc": (("station"), y_all),
    }
)
ds_ensemble = ds_ensemble.sortby("sim")
ds_ensemble.to_netcdf(f"{path_output}/ensemble_gia.nc")