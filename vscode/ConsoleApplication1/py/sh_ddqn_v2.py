import sys
import random
import numpy as np
from collections import deque
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.models import Sequential

EPISODES = 300


# Double DQN Agent for the Cartpole
# it uses Neural Network to approximate q function
# and replay memory & target q network
class DoubleDQNAgent:
    def __init__(self, state_size, action_size):
        # if you want to see Cartpole learning, then change to True
        self.render = False
        self.load_model = False
        # get size of state and action
        self.state_size = state_size
        self.action_size = action_size

        # these is hyper parameters for the Double DQN
        self.discount_factor = 0.99
        self.learning_rate = 0.001
        self.epsilon = 1.0
        self.epsilon_decay = 0.999
        self.epsilon_min = 0.01
        self.batch_size = 64
        self.train_start = 1000
        # create replay memory using deque
        self.memory = deque(maxlen=2000)

        # create main model and target model
        self.model = self.build_model()
        self.target_model = self.build_model()

        # initialize target model
        self.update_target_model()

        if self.load_model:
            self.model.load_weights("./save/sh-ddnq.h5")

    # approximate Q function using Neural Network
    # state is input and Q Value of each action is output of network
    def build_model(self):
        model = Sequential()
        model.add(Dense(24, input_dim=self.state_size, activation='relu', kernel_initializer='he_uniform'))
        model.add(Dense(24, activation='relu', kernel_initializer='he_uniform'))
        model.add(Dense(self.action_size, activation='linear', kernel_initializer='he_uniform'))
        model.summary()
        model.compile(loss='mse', optimizer=Adam(lr=self.learning_rate))
        return model

    # after some time interval update the target model to be same with model
    def update_target_model(self):
        self.target_model.set_weights(self.model.get_weights())

    # get action from model using epsilon-greedy policy
    def get_action(self, state):
        if np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size)
        else:
            q_value = self.model.predict(state)
            return np.argmax(q_value[0])

    # save sample <s,a,r,s'> to the replay memory
    def append_sample(self, state, action, reward):
        self.memory.append((state, action, reward))
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def step(self, action):
        reward = 0 # TODO: get discharging rate from C#
        return reward

    # pick samples randomly from replay memory (with batch_size)
    def train_model(self):
        if len(self.memory) < self.train_start:
            return
        batch_size = min(self.batch_size, len(self.memory))
        mini_batch = random.sample(self.memory, batch_size)

        update_input = np.zeros((batch_size, self.state_size))
        update_target = np.zeros((batch_size, self.state_size))
        action, reward = [], []

        for i in range(batch_size):
            update_input[i] = mini_batch[i][0]
            action.append(mini_batch[i][1])
            reward.append(mini_batch[i][2])
            update_target[i] = mini_batch[i][3]

        target = self.model.predict(update_input)
        target_next = self.model.predict(update_target)
        target_val = self.target_model.predict(update_target)

        for i in range(self.batch_size):
            target[i][action[i]] = reward[i]

        # make minibatch which includes target q value and predicted q value
        # and do the model fit!
        self.model.fit(update_input, target, batch_size=self.batch_size, epochs=1, verbose=0)


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

    agent = DoubleDQNAgent(state_size, action_size)

    for e in range(EPISODES):
        print(e)
        state = [0, 0] # TODO: get state from C#
        state = np.reshape(state, [1, state_size])

        # get action for the current state and go one step in environment
        action = agent.get_action(state)
        reward = agent.step(action)

        # save the sample <s, a, r, s'> to the replay memory
        agent.append_sample(state, action, reward)
        # every time step do the training
        agent.train_model()
        agent.update_target_model()
        print("episode: {}/{} ----- e: {:.2}".format(e, EPISODES, agent.epsilon))

        # save the model
        if e % 50 == 0:
            agent.model.save_weights("./save/sh-ddnq.h5")
