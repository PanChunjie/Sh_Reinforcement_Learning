# -*- coding: utf-8 -*-
import random
import numpy as np
from collections import deque
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import Adam
from tensorflow.keras import backend as K
import tensorflow as tf

EPISODES = 5000

class DDQNAgent:
    def __init__(self, state_size, action_size):
        self.state_size = state_size
        self.action_size = action_size
        self.experience = deque(maxlen=2000)
        self.gamma = 0.95 # discount rate
        self.epsilon = 1.0 # exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.99
        self.learning_rate = 0.001
        self.model = self._build_model()
        self.target_model = self._build_model()
        self.update_target_model()

    """Huber loss for Q Learning

    References: https://en.wikipedia.org/wiki/Huber_loss
                https://www.tensorflow.org/api_docs/python/tf/losses/huber_loss
    """

    def _huber_loss(self, y_true, y_pred, clip_delta=1.0):
        error = y_true - y_pred
        cond  = K.abs(error) <= clip_delta

        squared_loss = 0.5 * K.square(error)
        quadratic_loss = 0.5 * K.square(clip_delta) + clip_delta * (K.abs(error) - clip_delta)

        return K.mean(tf.where(cond, squared_loss, quadratic_loss))

    def _build_model(self):
        # Neural Net for Deep-Q learning Model
        model = Sequential()
        model.add(Dense(24, input_dim=self.state_size, activation='relu'))
        model.add(Dense(24, activation='relu'))
        model.add(Dense(self.action_size, activation='linear'))
        model.compile(loss=self._huber_loss, optimizer=Adam(lr=self.learning_rate))
        return model

    def update_target_model(self):
        # copy weights from model to target_model
        self.target_model.set_weights(self.model.get_weights())

    def remember(self, state, action, reward):
        self.experience.append((state, action, reward))

    def act(self, state):
        if np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size)
        act_values = self.model.predict(state)
        return np.argmax(act_values[0])  # returns action

    def replay(self, batch_size):
        minibatch = random.sample(self.experience, batch_size)
        for state, action, reward in minibatch:
            target = self.model.predict(state)
            target[0][action] = reward
            self.model.fit(state, target, epochs=1, verbose=0)
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def load(self, name):
        self.model.load_weights(name)

    def save(self, name):
        self.model.save_weights(name)

    def step(self, action):
        reward = 0 # TODO: get discharging rate from C#
        return reward


if __name__ == "__main__":
    # TODO: get connection for being used by c#

    # ---------------------------- customized params
    num_spd_lim = 3
    min_speed = 30
    max_speed = 70
    # ----------------------------

    # set sizes of state & action space
    state_size = 2 # SH_flow_rate & ACC_density
    action_size = ((max_speed - min_speed) / 5 + 1)**num_spd_lim # speed control with bandwidth of 5
    
    agent = DDQNAgent(state_size, action_size)

    # ---------------------------- uncomment for loading previous learned
    #agent.load("./save/sh-ddqn.h5")
    # ----------------------------    

    batch_size = 32

    for e in range(EPISODES):
        state = [0, 0] # TODO: get state from C#
        state = np.reshape(state, [1, state_size])
        action = agent.act(state)

        #--------------------------------------------------------
        reward = agent.step(action)
        agent.remember(state, action, reward)
        agent.update_target_model()
        print("episode: {}/{} ----- e: {:.2}".format(e, EPISODES, agent.epsilon))

        if len(agent.experience) > batch_size:
            agent.replay(batch_size)

        if e % 10 == 0:
            agent.save("./save/sh-ddqn.h5")
