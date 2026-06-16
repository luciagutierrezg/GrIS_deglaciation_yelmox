import os
import shutil
import numpy as np
import xarray as xr

# ---------------------------------------------------------------------------------------------
#  paths 
# ---------------------------------------------------------------------------------------------

path_base = "../../ensemble"
path_new = "../../ensemble_reduced/"
vars_new = ["H_ice", "z_srf", "z_bed", "uxy_s", "f_grnd", "mask_bed", "z_sl","Ta_ann", "Ta_sum"]
os.makedirs(path_new, exist_ok=True)
a,b=600,601 # range of folders

# ---------------------------------------------------------------------------------------------
#  procesing: 
# ---------------------------------------------------------------------------------------------
for i in range(a,b):
    folder = os.path.join(path_base, str(i))
    if not os.path.isdir(folder):
        print(f"ERROR The directory does not exist: {folder}")
        continue

    new_folder = os.path.join(path_new, str(i))
    os.makedirs(new_folder, exist_ok=True)

    # Copy .nml and 1D files
    for fname in ["yelmo_Greenland_ngrip_8km_restart.nml", "yelmo1D.nc"]:
        src = os.path.join(folder, fname)
        dst = os.path.join(new_folder, fname)
        if os.path.exists(src):
            shutil.copy2(src, dst)
        else:
            print(f"ERROR File not found: {src}")

    # Process yelmo2D.nc
    src_nc = os.path.join(folder, "yelmo2D.nc")
    dst_nc = os.path.join(new_folder, "yelmo2D_reduced.nc")

    if not os.path.exists(src_nc):
        print(f"ERROR The directory does not exist: {src_nc}")
        continue

    ds = xr.open_dataset(src_nc)

    vars_existentes = [v for v in vars_new if v in ds]
    ds_reducido = ds[vars_existentes]

    # Add the age of the isochrones
    H_ice = ds_reducido.H_ice
    f = ds_reducido.f_grnd
    iso = np.full_like(H_ice[0,:,:], np.nan)

    for t in reversed(H_ice.time.values):
        H_t = H_ice.sel(time=t).values
        f_t = f.sel(time=t).values
        mask = np.isnan(iso) & (H_t > 0) & (f_t == 1)
        iso[mask] = -t / 1000
        
    ds_reducido["isochrone"] = (("yc", "xc"), iso)
    ds_reducido["isochrone"].attrs = {
        "long_name": "Isochrone age",
        "units": "kyr BP"}
    
    # Save the new reduced NetCDF
    ds_reducido.to_netcdf(dst_nc)
    ds.close()
    ds_reducido.close()

    print(f"Processed {i}: saved to {dst_nc}")