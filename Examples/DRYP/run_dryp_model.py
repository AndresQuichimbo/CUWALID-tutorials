#import sys
#sys.path.append("C:/Users/Edisson/Documents/GitHub/CUWALID")
#sys.path.append("C:/Users/km19051/OneDrive - University of Bristol/Documents/GitHub/ilrt/CUWALID")
#sys.path.append("/home/c1755103/CUWALID")
#import cuwalid.dryp.components.DRYP_watershed as ppbasin
#import cuwalid.tools.DRYP_pptools as pptools
#import cuwalid.tools.DRYP_rrtools as rrtools
from cuwalid.dryp.main_DRYP import run_DRYP
"""
#fname = "ponds/PND_input_riv.json"
#fname = "DynaVeg/DV_input.json"
#fname = "DynaVeg/DV_input_kc.json"
#fname = "DynaVeg/DV_input_kc_gridded.json"
#fname = "Tanzania/dodoma_tlab_model_input_d19.json"
#fname = "abstraction/ABS_input_riv.json"
#fname = "/home/c1755103/HAD/HAD_IMERGcv_input_sim85_test.json"
#fname = "Lake/LA_input.json"
#fname = "reservoir/LA_input_riv.json"
#fname = "mlakes/mLA_input.json"
#fname = "Dams/LA_input_riv.json"
#fname = "GW_1D/GW_1D_input.json"
#fname = "multiaq/MA_input.json"
"""

# list of models to run
fname = [
#"ponds/PND_input_riv.json",
"DynaVeg/DV_input.json",
#"DynaVeg/DV_input_kc.json",
#"DynaVeg/DV_input_kc_gridded.json",
#"Tanzania/dodoma_tlab_model_input_d19.json",
#"abstraction/ABS_input_riv.json",
#"/home/c1755103/HAD/HAD_IMERGcv_input_sim85_test.json",
#"Lake/LA_input.json",
#"reservoir/LA_input_riv.json",
#"mlakes/mLA_input.json",
#"Dams/LA_input_riv.json",
#"GW_1D/GW_1D_input.json",
#"multiaq/MA_input.json",
#"multiaq/MA_input1.json",
]
for ifname in fname:
	run_DRYP(ifname)
	
