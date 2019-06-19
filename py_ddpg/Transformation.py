import random
import numpy as np 

class Transformation(object):
    def convert_actions(actions):
        action_space = 19 # [30, 120]
        min_speed = 30
        max_speed = 120
        min_output = -1 # tanh        
        #min_output = 0 # sigmoid
        max_output = 1
        output_range = max_output - min_output
        mapping_size = output_range / action_space
        speed_limits = []

        for a in actions:
            action = int((a + 1) / mapping_size) # tanh
            #action = int(a / mapping_size) # sigmoid
            speed = int(30 + action * 5)

            if speed > max_speed:
                speed = max_speed
            if speed < min_speed:
                speed = min_speed
            speed_limits.append(speed)

        return speed_limits