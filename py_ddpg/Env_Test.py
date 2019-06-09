import random
import numpy as np 

class Env_Test(object):

    def get_vissim_state(self):
        return [1, 1]

    def get_vissim_reward(self, actions):
    	return 1