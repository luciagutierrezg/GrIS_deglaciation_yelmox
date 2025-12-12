from matplotlib import rcParams, font_manager
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.colors as mcolors
import numpy as np

def set_computer_modern():
    font_path = "/home/luciagu/tools/fonts/cmunrm.ttf"
    font_manager.fontManager.addfont(font_path)  
    font_prop = font_manager.FontProperties(fname=font_path)
    rcParams['font.family'] = font_prop.get_name()
    rcParams['font.size'] = 15

def truncate_colormap(cmap, minval, maxval):

    new_cmap = mcolors.LinearSegmentedColormap.from_list(
        'truncated', cmap(np.linspace(minval, maxval, 200))
    )
    return new_cmap