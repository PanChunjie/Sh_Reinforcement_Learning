import numpy as np
import tensorflow as tf
import keras.backend as K

"""
from tensorflow.keras.initializers import RandomUniform
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.layers import Input, Dense, concatenate, LSTM, Reshape, BatchNormalization, Lambda, Flatten, add
"""

from keras.initializers import RandomUniform
from keras.models import Model
from keras.optimizers import Adam
from keras.layers import Input, Dense, concatenate, LSTM, Reshape, BatchNormalization, Lambda, Flatten, add

"""
# -------------------------------------- set 1
scalar = 7
multiplier = 100
HIDDEN1_UNITS = multiplier * scalar
HIDDEN2_UNITS = multiplier * 2 * scalar
# --------------------------------------
"""
# -------------------------------------- set 2
scalar = 7
multiplier = 1
HIDDEN1_UNITS = multiplier * scalar
HIDDEN2_UNITS = multiplier * 2 * scalar
# --------------------------------------

class Critic:
    """ Critic for the DDPG Algorithm, Q-Value function approximator
    """

    def __init__(self, inp_dim, out_dim, batch_size, lr, tau):
        # Dimensions and Hyperparams
        self.state_dim = inp_dim
        self.action_dim = out_dim
        self.batch_size = batch_size
        self.lr = lr
        self.tau = tau
        # Build models and target models
        self.model = self.network()
        self.target_model = self.network()
        self.model.compile(Adam(self.lr), 'mse')
        self.target_model.compile(Adam(self.lr), 'mse')
        # Function to compute Q-value gradients (Actor Optimization)
        self.action_grads = K.function([self.model.input[0], self.model.input[1]], K.gradients(self.model.output, [self.model.input[1]]))

    def network(self):
        """
        S -> w1 -> h1 -\
        A -> a1 -------- => h2 -> h3 -> V
        """
        S = Input(shape=[self.state_dim])
        A = Input(shape=[self.action_dim])
        w1 = Dense(HIDDEN1_UNITS, activation='relu')(S)
        a1 = Dense(HIDDEN2_UNITS, activation='linear')(A) 
        h1 = Dense(HIDDEN2_UNITS, activation='linear')(w1)
        h2 = add([h1,a1])    
        h3 = Dense(HIDDEN2_UNITS, activation='relu')(h2)
        V = Dense(self.action_dim, activation='linear')(h3)   
        model = Model([S,A], V)
        adam = Adam(lr=self.lr)
        model.compile(loss='mse', optimizer=adam)
        return model

    def gradients(self, states, actions):
        """ Compute Q-value gradients w.r.t. states and policy-actions
        """
        return self.action_grads([states, actions])

    def target_predict(self, inp):
        """ Predict Q-Values using the target network

        inp = [state, actions]
        state.shape = (1, state_dim)
        actions.shape = (1, action_dim)
        """
        return self.target_model.predict(inp)

    def train_on_batch(self, states, actions, critic_target):
        """ Train the critic network on batch of sampled experience

        states.shape = (batch_size, state_dim)
        actions.shape = (batch_size, action_dim)
        critic_target.shape = (batch_size, action_dim) # q_values
        """
        return self.model.train_on_batch([states, actions], critic_target)

    def transfer_weights(self):
        """ Transfer model weights to target model with a factor of Tau
        """
        W, target_W = self.model.get_weights(), self.target_model.get_weights()
        for i in range(len(W)):
            target_W[i] = self.tau * W[i] + (1 - self.tau)* target_W[i]
        self.target_model.set_weights(target_W)

    def save(self, path):
        self.model.save_weights(path + '_critic.h5', overwrite=True)

    def load(self, path):
        self.model.load_weights(path)
