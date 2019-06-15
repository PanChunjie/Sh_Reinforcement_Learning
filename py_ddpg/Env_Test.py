import random
import numpy as np 

class Env_Test(object):

    def get_vissim_state(self, a, b, c):
        return [1000, 1000, 1000, 1000, 1000, 1000, 1000]
    
    def get_vissim_reward(self, a, b):
    	return 100, [2000, 2000, 2000, 2000, 2000, 2000, 2000]