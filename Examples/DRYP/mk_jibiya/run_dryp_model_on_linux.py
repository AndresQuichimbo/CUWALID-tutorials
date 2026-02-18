#cd /user/home/km19051/DRYPv2.0_test/ 
#source /user/home/km19051/miniconda3/bin/activate 
#python /user/home/km19051/WS/aux_WG_MC_Analysis.py

# Import libraries from local repository
import sys
sys.path.append('/home/c1755103/gitremote/CUWALID')
from cuwalid.dryp.main_DRYP import run_DRYP

#import dryp.components.DRYP_watershed as ppbasin
import cuwalid.tools.DRYP_pptools as pptools
import cuwalid.tools.DRYP_rrtools as rrtools

#fname = "../Lake/input/LA_dem.asc"
#fname_out = "../Lake/input/LA_flowdir.asc"
#rrtools.create_raster_flowdirection_dryp(fname, fname_out, transform=False)
#fname = "HAD_IMERGa_Lake_input_sim.dmp"
fname = "/home/c1755103/testcuwalid/mk_jibiya/inputfiles/mk_tlab_model_input_t2a.json"
#fname = "/home/c1755103/testcuwalid/mk_jibiya/inputfiles/mk_tlab_model_input_t1a.json"
run_DRYP(fname)