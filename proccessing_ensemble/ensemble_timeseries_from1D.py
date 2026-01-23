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

# ---------------------------------------------
# Calculations
# This script creates a NetCDF file with ensemble timeseries from yelmo1D files
# It includes the following variables:
# - V_sle: Sea Level Equivalent Volume
# - A_ice: Ice Area
# - A_ice_g: Grounded Ice Area
# - T_srf: Surface Temperature (annual mean over the domain)
# ---------------------------------------------
V_ensemble = []
A_ensemble = []
A_g_ensemble = []
T_ensemble = []
valid_sim_indices = []   

for i, sim_path in enumerate(sim_paths):

    file_path = os.path.join(sim_path, "yelmo1D.nc")
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
    A_ice=yelmo.A_ice.values
    A_ice_g=yelmo.A_ice_g.values
    V_sle=yelmo.V_sle.values
    T=yelmo.T_srf.values
    
    V_ensemble.append(V_sle)
    A_ensemble.append(A_ice)
    A_g_ensemble.append(A_ice_g)
    T_ensemble.append(T)
    valid_sim_indices.append(n_sim)

V_ensemble = np.stack(V_ensemble, axis=0)
A_ensemble = np.stack(A_ensemble, axis=0)
A_g_ensemble = np.stack(A_g_ensemble, axis=0)
T_ensemble = np.stack(T_ensemble, axis=0)

# final dataset
ds_ensemble = xr.Dataset(
    data_vars={
        "A_ice": (("sim", "time"), A_ensemble),
        "A_ice_g": (("sim", "time"), A_g_ensemble),
        "V_sle": (("sim", "time"), V_ensemble),
        "T_srf": (("sim", "time"), T_ensemble)
    },
    coords={
        "sim": np.array(valid_sim_indices),
        "time": time
    }
)
ds_ensemble = ds_ensemble.sortby("sim")
ds_ensemble.to_netcdf(f"{path_output}/timeseries_from1D.nc")
