import numpy as np
import xarray as xr
from matplotlib import pyplot as plt
import matplotlib as mpl
import glob
import os

# ----------------------------------------------------------------------------
# Paths
# ----------------------------------------------------------------------------
path_ensemble="path/ensemble_reduced/*"
path_output="../output"

# ---------------------------------------------
# Calculo elevaciones en ensemble
# ---------------------------------------------
def z_ice_core(ds, ice_core):
    if ice_core == "ngrip":
        lat, lon = 75.0166666,-42.5333312
    elif ice_core == "grip":
        lat, lon = 72.5833,-37.6333
    elif ice_core == "camp_century":
        lat, lon = 77.1667,-61.1333
    elif ice_core == "dye3":
        lat, lon = 65.1833326,-43.8166634
    else:
        print("Error: no valid location")
    
    dist = np.sqrt((ds.lat2D - lat)**2 + (ds.lon2D - lon)**2)
    iy, ix = np.unravel_index(dist.argmin(), dist.shape)
    z = ds["z_srf"].isel(yc=iy, xc=ix)

    return z.values


z_ens = []
valid_sim_indices = []

ice_core_ids = ["grip", "ngrip", "camp_century", "dye3"]

sim_paths = sorted(glob.glob(path_ensemble))

for i, sim_path in enumerate(sim_paths):

    file_path = os.path.join(sim_path, "yelmo2D_reduced.nc")

    try:
        yelmo = xr.open_dataset(file_path)
    except FileNotFoundError:
        print(f"[ERROR] Archivo no encontrado: {file_path}. Se omite esta simulación.")
        continue
    except Exception as e:
        print(f"[ERROR] No se pudo abrir {file_path}: {e}. Se omite esta simulación.")
        continue
    
    z_grip_i = z_ice_core(yelmo, "grip")
    z_ngri_i = z_ice_core(yelmo, "ngrip")
    z_camp_i = z_ice_core(yelmo, "camp_century")
    z_dye3_i = z_ice_core(yelmo, "dye3")

    z = np.vstack([
        z_grip_i,
        z_ngri_i,
        z_camp_i,
        z_dye3_i
    ]).T 
    
    if i==0: 
        time = yelmo["time"].values

    z_ens.append(z)
    valid_sim_indices.append(i)

z_ens = np.stack(z_ens, axis=0)

ds_ensemble = xr.Dataset(
    data_vars={
        "z_srf": (("sim", "time", "ice_core"), z_ens)
    },
    coords={
        "sim": np.array(valid_sim_indices),
        "time": time,
        "ice_core": ice_core_ids
    })

ds_ensemble.to_netcdf(f"{path_output}/ensemble_elevations.nc")