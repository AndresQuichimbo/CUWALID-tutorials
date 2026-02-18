#!/usr/bin/env python
# -*- coding: utf-8 -*- 

# Import libraries from local repository
import sys
sys.path.append('/home/c1755103/testcuwalid')

from cuwalid.tests.dryp.scripts.test_water_bodies import test_water_bodies
from cuwalid.tests.dryp.scripts.test_zone_parameters import test_zone_parameters_no_mask, test_zone_parameters_with_mask_and_scale_and_core_nodes

#test_water_bodies()
test_zone_parameters_no_mask()
test_zone_parameters_with_mask_and_scale_and_core_nodes()
