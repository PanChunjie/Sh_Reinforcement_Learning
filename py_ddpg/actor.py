import numpy as np
import tensorflow as tf
import keras.backend as K
"""
from tensorflow.keras.initializers import RandomUniform
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense, Reshape, LSTM, Lambda, BatchNormalization, GaussianNoise, Flatten, concatenate
"""
from keras.initializers import RandomUniform
from keras.models import Model
from keras.layers import Input, Dense, Reshape, LSTM, Lambda, BatchNormalization, GaussianNoise, Flatten, concatenate

"""
from keras.initializations import normal, identity
from keras.models import model_from_json
from keras.models import Sequential, Model
from keras.engine.training import collect_trainable_weights
from keras.layers import Dense, Flatten, Input, merge, Lambda
from keras.optimizers import Adam
"""

# -------------------------------------- set 1

scalar = 7
multiplier = 100
HIDDEN1_UNITS = multiplier * scalar
HIDDEN2_UNITS = multiplier * 2 * scalar

# -------------------------------------- set 2
"""
scalar = 7
multiplier = 1
HIDDEN1_UNITS = multiplier * scalar
HIDDEN2_UNITS = multiplier * 2 * scalar
"""

class Actor:
    """ Actor Network for the DDPG Algorithm
    """
    def __init__(self, inp_dim, out_dim, batch_size, lr, tau):
        self.state_dim = inp_dim
        self.action_dim = out_dim
        self.batch_size = batch_size
        self.tau = tau
        self.lr = lr
        self.model = self.network()
        self.target_model = self.network()
        self.adam_optimizer = self.optimizer()

    def network(self):
        """
        S -> h0 -> h1 -> spd_1 -|
                    | -> spd_2 -|
                    | -> spd_3 -|
                    | -> spd_4 -|
                    | -> spd_5 -|
                    | -> spd_6 -|
                    | -> spd_7 -| => V
        """
        #S = Input(shape =(self.env_dim,))
        S = Input(shape=[self.state_dim])  
        h0 = Dense(HIDDEN1_UNITS, activation='relu')(S)
        h1 = Dense(HIDDEN2_UNITS, activation='relu')(h0)
        spd_1 = Dense(1, activation='tanh', kernel_initializer=RandomUniform())(h1)
        spd_2 = Dense(1, activation='tanh', kernel_initializer=RandomUniform())(h1)
        spd_3 = Dense(1, activation='tanh', kernel_initializer=RandomUniform())(h1)
        spd_4 = Dense(1, activation='tanh', kernel_initializer=RandomUniform())(h1)
        spd_5 = Dense(1, activation='tanh', kernel_initializer=RandomUniform())(h1)
        spd_6 = Dense(1, activation='tanh', kernel_initializer=RandomUniform())(h1)
        spd_7 = Dense(1, activation='tanh', kernel_initializer=RandomUniform())(h1)
        V = concatenate([spd_1, spd_2, spd_3, spd_4, spd_5, spd_6, spd_7])
        model = Model(S, V)
        #
        return model

    def predict(self, state):
        """ Action prediction

        model.predict(state)
        state.shape = (1, state_dim)
        """
        return self.model.predict(np.expand_dims(state, axis=0))

    def target_predict(self, inp):
        """ Action prediction (target network)

        inp.shape = (1, state_dim)
        """
        return self.target_model.predict(inp)

    def transfer_weights(self):
        """ Transfer model weights to target model with a factor of Tau
        """
        W, target_W = self.model.get_weights(), self.target_model.get_weights()
        for i in range(len(W)):
            target_W[i] = self.tau * W[i] + (1 - self.tau)* target_W[i]
        self.target_model.set_weights(target_W)

    def train(self, states, actions, grads):
        """ Actor Training
        """
        self.adam_optimizer([states, grads])

    def optimizer(self):
        """ Actor Optimizer
        """
        action_gdts = K.placeholder(shape=(None, self.action_dim))
        params_grad = tf.gradients(self.model.output, self.model.trainable_weights, -action_gdts)
        grads = zip(params_grad, self.model.trainable_weights)

        inputs = [self.model.input, action_gdts]
        outputs = []
        #outputs = K.placeholder(shape=(None, None))
        updates = [tf.train.AdamOptimizer(self.lr).apply_gradients(grads)]#[1:]
        return K.function(inputs = inputs, outputs = outputs, updates = updates)

    def save(self, path):
        self.model.save_weights(path + '_actor.h5', overwrite=True)

    def load(self, path):
        self.model.load_weights(path)
