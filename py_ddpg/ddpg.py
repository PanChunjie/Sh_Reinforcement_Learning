import numpy as np
import random
import argparse
from keras.models import model_from_json, Model
from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation, Flatten
from keras.optimizers import Adam
import tensorflow as tf
#from keras.engine.training import collect_trainable_weights
import json

#------------------------------------------------------------------
from Vissim import Vissim
from ReplayBuffer import ReplayBuffer
from ActorNetwork import ActorNetwork
from CriticNetwork import CriticNetwork
from OU import OU
from Transformation import Transformation
import timeit

#Ornstein-Uhlenbeck Process
OU = OU()
Transformation = Transformation()

#1 means Train, 0 means simply Run
def ddpg(train_indicator=0):
    BUFFER_SIZE = 100000
    BATCH_SIZE = 32
    GAMMA = 0.99
    TAU = 0.001     #Target Network HyperParameters
    LRA = 0.0001    #Learning rate for Actor
    LRC = 0.001     #Lerning rate for Critic

    action_dim = 7  #7 speed limit control actions
    state_dim = 2  #TODO: currently 2, later will be 8, 1 for SH_flowrate, 7 for ACC_local_densities

    np.random.seed(1337)

    vision = False

    EXPLORE = 100000.
    episode_count = 2000
    reward = 0
    step = 0
    epsilon = 1
    indicator = 0

    actor = ActorNetwork(sess, state_dim, action_dim, BATCH_SIZE, TAU, LRA)
    critic = CriticNetwork(sess, state_dim, action_dim, BATCH_SIZE, TAU, LRC)
    buff = ReplayBuffer(BUFFER_SIZE) #Create replay buffer

    # Generate a Vissim environment
    env = Vissim()

    #Now load the weight
    print("====================> Load weights...")
    try:
        actor.model.load_weights("actormodel.h5")
        critic.model.load_weights("criticmodel.h5")
        actor.target_model.load_weights("actormodel.h5")
        critic.target_model.load_weights("criticmodel.h5")
        print("====================> Weight load successfully")
    except:
        print("====================> Cannot find the weight")

    print("")
    print("====================> Speed Harmonization Start...")
    print("")

    for i in range(episode_count):
        s_t = np.hstack((env.get_vissim_state())) #TODO: make sure states are recieved correctly

        loss = 0
        epsilon -= 1.0 / EXPLORE
        a_t = np.zeros([1,action_dim])
        noise_t = np.zeros([1,action_dim])

        a_t_original = actor.model.predict(s_t.reshape(1, s_t.shape[0]))
        #TODO: OU function params?

        for i in range(0,7):
            noise_t[0][i] = train_indicator * max(epsilon, 0) * OU.function(a_t_original[0][i], 0.5, 0.20, 0.30)
            a_t[0][i] = a_t_original[0][i] + noise_t[0][i]

        #action_mapping function
        trans_a_t = Transformation.convert_actions(a_t[0])

        r_t = env.get_vissim_reward(trans_a_t) 

        #Add replay buffer
        buff.add(s_t, a_t[0], r_t)

        #Do the batch update
        batch = buff.getBatch(BATCH_SIZE)
        states = np.asarray([e[0] for e in batch])
        actions = np.asarray([e[1] for e in batch])
        rewards = np.asarray([e[2] for e in batch])
        y_t = np.asarray([e[1] for e in batch])

        for k in range(len(batch)):
            y_t[k] = rewards[k]

        if (train_indicator):
            loss += critic.model.train_on_batch([states,actions], y_t)
            a_for_grad = actor.model.predict(states)
            grads = critic.gradients(states, a_for_grad)
            actor.train(states, grads)
            actor.target_train()
            critic.target_train()

        print("Episode", i, "Step", step, "Action", a_t, "Reward", r_t, "Loss", loss)

        if np.mod(i, 10) == 0:
            if (train_indicator):
                print("====================> Saving model...")
                actor.model.save_weights("actormodel.h5", overwrite=True)
                with open("actormodel.json", "w") as outfile:
                    json.dump(actor.model.to_json(), outfile)

                critic.model.save_weights("criticmodel.h5", overwrite=True)
                with open("criticmodel.json", "w") as outfile:
                    json.dump(critic.model.to_json(), outfile)

    env.end()  # Shutting down Vissim
    print("====================> Finish.")

if __name__ == "__main__":
    ddpg()
