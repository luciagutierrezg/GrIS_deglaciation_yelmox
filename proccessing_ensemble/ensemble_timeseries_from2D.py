import numpy as np
import xarray as xr
from matplotlib import pyplot as plt
import pandas as pd
import glob
import os


# ----------------------------------------------------------------------------
# Paths
# ----------------------------------------------------------------------------
path_ensemble="/p/projects/megarun/luciagu/data/tabone2024/ensemble_reduced/*"
path_output="../output"
sim_paths = sorted(glob.glob(path_ensemble))
file_name = "yelmo2D_temperatures.nc" # Modificar cuando esté todo en un único file (idealmente todo en yelmo2D_reduced.nc)

# ---------------------------------------------
# Calculations
# This script creates a NetCDF file with ensemble timeseries from yelmo2D files
# It includes the following variables:
# - T_ann: Annual Mean Surface Temperature over Ocean
# - T_sum: Summer Mean Surface Temperature over Ocean
# ---------------------------------------------

T_ann_ensemble = []
T_sum_ensemble = []
valid_sim_indices = []   

for i, sim_path in enumerate(sim_paths):

    file_path1 = os.path.join(sim_path, file_name)
    file_path2 = os.path.join(sim_path, "yelmo2D_reduced.nc")

    try:
        yelmo1 = xr.open_dataset(file_path1)
        yelmo2 = xr.open_dataset(file_path2)
    except FileNotFoundError:
        print(f"[ERROR] No se encontró el archivo: {file_path1}. Se omite esta simulación.")
        continue
    except Exception as e:
        print(f"[ERROR] No se pudo abrir {file_path1}: {e}. Se omite esta simulación.")
        continue

    time=yelmo1.time.values
    T_ann=(yelmo1.Ta_ann.where(yelmo2.mask_bed==0)).mean(dim=["xc","yc"])
    T_sum=(yelmo1.Ta_sum.where(yelmo2.mask_bed==0)).mean(dim=["xc","yc"])
    
    T_ann_ensemble.append(T_ann)
    T_sum_ensemble.append(T_sum)
    valid_sim_indices.append(i)

# convertir lista → array (simulación x tiempo)
T_ann_ensemble = np.stack(T_ann_ensemble, axis=0)
T_sum_ensemble = np.stack(T_sum_ensemble, axis=0)

# construir dataset final
ds_ensemble = xr.Dataset(
    data_vars={
        "T_ann": (("sim", "time"), T_ann_ensemble),
        "T_sum": (("sim", "time"), T_sum_ensemble)
    },
    coords={
        "sim": np.array(valid_sim_indices),
        "time": time
    }
)

ds_ensemble.to_netcdf("../output/timeseries_from2D.nc")