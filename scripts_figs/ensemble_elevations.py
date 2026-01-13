import numpy as np
import xarray as xr
from matplotlib import pyplot as plt
import pandas as pd
from fonts_config import set_computer_modern, truncate_colormap
set_computer_modern()
import matplotlib as mpl
mpl.rcParams['axes.unicode_minus'] = False

import glob
import os

# ------------------------------------------------------------
# paths
# ------------------------------------------------------------
n_best=2440
ele = xr.open_dataset("../../FesmData/Vinther2009_elevations/vinther2009.nc")

ds_ensemble = xr.open_dataset("../output/ensemble_elevations.nc")
valid_sim_indices = ds_ensemble.sim

best = ds_ensemble.sel(sim=n_best)
time = best["time"].values * 1e-3  # kyr BP
z_ngri = best.z_srf.sel(ice_core="ngrip").values
z_grip = best.z_srf.sel(ice_core="grip").values
z_camp = best.z_srf.sel(ice_core="camp_century").values
z_dye3 = best.z_srf.sel(ice_core="dye3").values


fig, axes = plt.subplots(4, 1, figsize=(6, 14), sharex=True)

# ================================
# PANEL 1 - NGRIP
# ================================
ax = axes[0]
icec="ngrip"
for sim_idx in valid_sim_indices:
    ax.plot(
    ds_ensemble.time* 1e-3, 
    ds_ensemble.z_srf.sel(sim=sim_idx, ice_core=icec), 
    "-", color="#b6b6b6", alpha=0.3,zorder=0)
    
ax.plot(time, z_ngri, color="black")

a = 2650
vint=ele.sel(ice_core=icec)
ax.fill_between(vint.time*1e-3, vint.z_srf - vint.error, vint.z_srf + vint.error, color="blue", alpha=0.2)
ax.plot(vint.time*1e-3, vint.z_srf, color="blue")

ax.text(-11.5, a, "NGRIP", ha="left", va="top")
ax.set_ylabel("Elevation (m)")
ax.set_xlim(-12, 0.1)

# ================================
# PANEL 2 - GRIP
# ================================
ax = axes[1]

icec="grip"
for sim_idx in valid_sim_indices:
    ax.plot(
    ds_ensemble.time* 1e-3, 
    ds_ensemble.z_srf.sel(sim=sim_idx, ice_core=icec), 
    "-", color="#b6b6b6", alpha=0.3,zorder=0)


ax.plot(time, z_grip, color="black")

a = 3050
vint=ele.sel(ice_core=icec)
ax.fill_between(vint.time*1e-3, vint.z_srf - vint.error, vint.z_srf + vint.error, color="blue", alpha=0.2)
ax.plot(vint.time*1e-3, vint.z_srf, color="blue")

ax.text(-11.5, a, "GRIP", ha="left", va="top")
ax.set_ylabel("Elevation (m)")

# ================================
# PANEL 3 - Camp Century
# ================================
ax = axes[2]
icec="camp_century"

for sim_idx in valid_sim_indices:
    ax.plot(
    ds_ensemble.time* 1e-3, 
    ds_ensemble.z_srf.sel(sim=sim_idx, ice_core=icec), 
    "-", color="#b6b6b6", alpha=0.3,zorder=0)

ax.plot(time, z_camp, color="black")

a = 1850
vint=ele.sel(ice_core=icec)
ax.fill_between(vint.time*1e-3, vint.z_srf - vint.error, vint.z_srf + vint.error, color="blue", alpha=0.2)
ax.plot(vint.time*1e-3, vint.z_srf, color="blue")

ax.text(-11.5, a, "Camp Century", ha="left", va="top")
ax.set_ylabel("Elevation (m)")

# ================================
# PANEL 4 - DYE3
# ================================
ax = axes[3]
icec="dye3"

j=0
for sim_idx in valid_sim_indices:
    if j==0:
        ax.plot(
        ds_ensemble.time* 1e-3, 
        ds_ensemble.z_srf.sel(sim=sim_idx, ice_core=icec), 
        "-", color="#b6b6b6", alpha=0.3, label="Yelmo Ensemble",zorder=0)
    else:
        ax.plot(
        ds_ensemble.time* 1e-3, 
        ds_ensemble.z_srf.sel(sim=sim_idx, ice_core="dye3"), 
        "-", color="#b6b6b6", alpha=0.3,zorder=0)
    j=j+1

ax.plot(time, z_dye3, color="black", label="Yelmo best, #"+str(n_best))

a=1800
vint=ele.sel(ice_core=icec)
ax.fill_between(vint.time*1e-3, vint.z_srf - vint.error, vint.z_srf + vint.error, color="blue", alpha=0.2, label="Vinther et al. (2009)")
ax.plot(vint.time*1e-3, vint.z_srf, color="blue")

ax.text(-11.5, a, "DYE3", ha="left", va="top")
ax.set_xlabel("Time (kyr BP)")
ax.set_ylabel("Elevation (m)")

axes[0].set_title('(a)',loc='right')
axes[1].set_title('(b)',loc='right')
axes[2].set_title('(c)',loc='right')
axes[3].set_title('(d)',loc='right')

handles, labels = axes[-1].get_legend_handles_labels()
fig.legend(handles, labels, loc="upper center", ncol=1, frameon=False)
plt.subplots_adjust(top=0.90,bottom=0.05,left=0.15,right=0.99)
plt.savefig(f"../figs/elevations_ensemble_{n_best}.png", dpi=200)
plt.close()
