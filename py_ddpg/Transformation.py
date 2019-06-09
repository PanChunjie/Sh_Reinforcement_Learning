import random
import numpy as np 

class Transformation(object):

    def convert_actions(self, actions):
    	action_space = 19 # [30, 120]
    	min_output = -1
    	max_output = 1
    	output_range = max_output - min_output
    	mapping_size = output_range / action_space
    	speed_limits = []

    	for a in actions:
    		action = int((a+1) / mapping_size)
    		speed_limits.append(int(30 + action * 5))

        return speed_limits