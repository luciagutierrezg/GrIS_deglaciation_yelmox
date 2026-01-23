import numpy as np
import xarray as xr
from matplotlib import pyplot as plt
import pandas as pd
import glob
import os


# ----------------------------------------------------------------------------
# Paths
# ----------------------------------------------------------------------------
path_ensemble="../../ensemble_reduced/*"
path_output="../output"
sim_paths = sorted(glob.glob(path_ensemble))
file_name = "yelmo2D_reduced.nc" # Modificar cuando esté todo en un único file (idealmente todo en yelmo2D_reduced.nc)
regs=xr.open_dataset("/p/projects/megarun/luciagu/data/lauritzen2025/Greenland_Basins_PS_v1.4.2_8km.nc")

# ---------------------------------------------
# Calculations
# This script creates a NetCDF file with ensemble timeseries from yelmo2D files
# It includes the following variables:
# - T_ann: Annual Mean Surface Temperature over Ocean
# - T_sum: Summer Mean Surface Temperature over Ocean
# - A: Ice Area in 7 Greenland regions
# ---------------------------------------------

def variables(sim,mask,basin):

    time_fun = sim.time * 1e-3
    if basin=="all":
        h=xr.where((sim.f_grnd>0)&(sim.H_ice>0),sim.H_ice,0)
    else:
        h=xr.where((sim.f_grnd>0)&(sim.H_ice>0)&(mask==basin),sim.H_ice,0)

    A = (h != 0).sum(dim=("yc", "xc")) * 8 * 8 * 1e-6 
    V = h.sum(dim=("yc", "xc")) * 1e-3 * 8 * 8 * 1e-6
    return time_fun, A, V

region_ids = np.unique(regs.mask)

T_ann_ensemble = []
T_sum_ensemble = []
A_ensemble = []   
valid_sim_indices = []   

for i, sim_path in enumerate(sim_paths):

    file_path = os.path.join(sim_path, file_name)
    n_sim = int(os.path.basename(sim_path))
    try:
        yelmo = xr.open_dataset(file_path)
    except FileNotFoundError:
        print(f"[ERROR] No se encontró el archivo: {file_path}. Se omite esta simulación.")
        continue
    except Exception as e:
        print(f"[ERROR] No se pudo abrir {file_path}: {e}. Se omite esta simulación.")
        continue

    time=yelmo.time.values
    T_ann=(yelmo.Ta_ann.where(yelmo.mask_bed==0)).mean(dim=["xc","yc"])
    T_sum=(yelmo.Ta_sum.where(yelmo.mask_bed==0)).mean(dim=["xc","yc"])
    time=yelmo.time.values
    T_ann=(yelmo.Ta_ann.where(yelmo.mask_bed==0)).mean(dim=["xc","yc"])
    T_sum=(yelmo.Ta_sum.where(yelmo.mask_bed==0)).mean(dim=["xc","yc"])
    
    T_ann_ensemble.append(T_ann)
    T_sum_ensemble.append(T_sum)
    
    A_all = []
    for r in region_ids:
        _, A, _ = variables(yelmo, regs.mask, r)
        A_all.append(A.values)

    # convertir lista → array (tiempo x regiones)
    A_all = np.stack(A_all, axis=1)
    A_ensemble.append(A_all)
    valid_sim_indices.append(n_sim)   


# convertir lista → array (simulación x tiempo)
T_ann_ensemble = np.stack(T_ann_ensemble, axis=0)
T_sum_ensemble = np.stack(T_sum_ensemble, axis=0)
A_ensemble = np.stack(A_ensemble, axis=0)

# construir dataset final
ds_ensemble = xr.Dataset(
    data_vars={
        "T_ann": (("sim", "time"), T_ann_ensemble),
        "T_sum": (("sim", "time"), T_sum_ensemble),
        "A": (("sim", "time", "region"), A_ensemble)
    },
    coords={
        "sim": np.array(valid_sim_indices),
        "time": time,
        "region": region_ids
    }
)

ds_ensemble = ds_ensemble.sortby("sim")
ds_ensemble.to_netcdf(f"{path_output}/timeseries_from2D.nc")