import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import glob
import os

# ------------------------------------------------------------
# paths 
# ------------------------------------------------------------

data = xr.open_dataset("../..//FesmData/GAPSLIP_Gowan2023_GrIS/output/rsl_dataset_reduced.nc")
sim_paths = sorted(glob.glob("../../data/tabone2024/ensemble_reduced/*"))

def rsl_point(x, y, ds):
    dist = np.sqrt((ds.xc - x)**2 + (ds.yc - y)**2)
    idx = dist.argmin(dim=("yc", "xc"))
    iy = idx["yc"].item()
    ix = idx["xc"].item()
    sim = ds.isel(yc=iy, xc=ix)
    rsl=sim.z_sl-sim.z_bed
    rsl=rsl-rsl.sel(time=0)
    return rsl

rsl_ensemble = []   
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

    rsl_all = []

    for lab_reg in data.region:
        point=data.sel(region=lab_reg)
        xc=point.xc
        yc=point.yc
        rsl = rsl_point(xc, yc, yelmo)
        rsl_all.append(rsl)

    #  list → array (time x regions)
    rsl_all = np.stack(rsl_all, axis=1)

    rsl_ensemble.append(rsl_all)
    valid_sim_indices.append(n_sim)   

# list → array (sim x time x region)
rsl_ensemble = np.stack(rsl_ensemble, axis=0)


# final dataset
ds_ensemble = xr.Dataset(
    data_vars={
        "rsl": (("sim", "time", "region"), rsl_ensemble)
    },
    coords={
        "sim": np.array(valid_sim_indices),
        "time": yelmo.time.values,
        "region": data.region.values
    }
)
ds_ensemble = ds_ensemble.sortby("sim")
ds_ensemble.to_netcdf("../output/ensemble_rsl.nc")
