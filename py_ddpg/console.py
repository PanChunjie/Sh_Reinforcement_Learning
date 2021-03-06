from ddpg import DDPG
from Vissim import Vissim
#from Env_Test import Env_Test


env = Vissim()
BUFFER_SIZE = 20000
BATCH_SIZE = 32
GAMMA = 0.99
TAU = 0.001

LRA = 0.0001 #Learning rate for Actor
LRC = 0.001  #Lerning rate for Critic

action_dim = 7  #7 speed limit control actions
state_dim = 2   #TODO: currently 2, later will be 8, 1 for SH_flowrate, 7 for ACC_local_densities
indicator = 1
step_size = 10
episode = 2000

ddpg = DDPG(action_dim, state_dim, BATCH_SIZE, step_size, BUFFER_SIZE, indicator, episode, GAMMA, LRA, LRC, TAU)

ddpg.run(env)
