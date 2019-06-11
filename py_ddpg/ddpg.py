import sys
import numpy as np

from actor import Actor
from critic import Critic
from utils.networks import tfSummary, OrnsteinUhlenbeckProcess
from utils.memory_buffer import MemoryBuffer

from Transformation import Transformation

class DDPG(object):
    """ Deep Deterministic Policy Gradient (DDPG) Helper Class
    """

    def __init__(self, action_dim, state_dim, batch_size, step, buffer_size, train_indicator, episode, gamma, lra, lrc, tau, load_weight=True):
        """ Initialization
        """
        # Environment and A2C parameters
        self.action_dim = action_dim
        self.state_dim = state_dim
        self.batch_size = batch_size
        self.step = step
        self.gamma = gamma
        self.lra = lra
        self.lrc = lrc
        self.tau = tau
        self.episode = episode
        self.train_indicator = train_indicator
        # Create actor and critic networks
        self.actor = Actor(state_dim, action_dim, batch_size, lra, tau)
        self.critic = Critic(state_dim, action_dim, batch_size, lrc, tau)
        self.buffer = MemoryBuffer(buffer_size)

        if load_weight:
            try:
                self.load_weights(
                    "C:\\Users\\KRATOS\\Desktop\\workplace\\Sh_Reinforcement_Learning\\py_ddpg\\saved_model\\_LR_0.0001_actor.h5", 
                    "C:\\Users\\KRATOS\\Desktop\\workplace\\Sh_Reinforcement_Learning\\py_ddpg\\saved_model\\_LR_0.001_critic.h5"
                    )
                print("Actor-Critic Models are loaded with weights...")
            except:
                print("Weights are failed to be loaded, please check weights loading path...")

    def policy_action(self, s):
        """ Use the actor to predict value
        """
        return self.actor.predict(s)[0]

    def bellman(self, rewards, q_values):
        """ Use the Bellman Equation to compute the critic target (one action only)
        """
        critic_target = np.asarray(q_values)
        for i in range(q_values.shape[0]):
            critic_target[i] = rewards[i]
        return critic_target

    def memorize(self, state_old, action, reward, state_new):
        """ Store experience in memory buffer
        """
        self.buffer.memorize(state_old, action, reward, state_new)

    def sample_batch(self, batch_size):
        return self.buffer.sample_batch(batch_size)

    def update_models(self, states, actions, critic_target):
        """ Update actor and critic networks from sampled experience
        """
        # Train critic
        self.critic.train_on_batch(states, actions, critic_target)
        # Q-Value Gradients under Current Policy
        actions = self.actor.model.predict(states)
        grads = self.critic.gradients(states, actions)
        # Train actor
        self.actor.train(states, actions, np.array(grads).reshape((-1, self.act_dim)))
        # Transfer weights to target networks at rate Tau
        self.actor.transfer_weights()
        self.critic.transfer_weights()

    def run(self, env):
        # First, gather experience
        for e in range(self.episode):
            # Reset episode
            loss = 0
            time = 0
            # set initial state
            cumul_reward = 0
            state_old = env.get_vissim_state(1, 180*5, [45, 55, 60, 65, 70, 75, 80]) #TODO: make sure states are recieved correctly
            actions, states, rewards = [], [], []
            noise = OrnsteinUhlenbeckProcess(size=self.action_dim)

            print("Episode: ", e, " ========================:")

            for t in range(self.step):
                action = np.zeros([self.action_dim])

                action_original = self.policy_action(state_old)
                #TODO: OU function params?

                noises = noise.generate(time)

                for i in range(0,7):
                    action[i] = action_original[i] + self.train_indicator * noises[i]

                #action_mapping function
                transformed_action = Transformation.convert_actions(action)

                reward, state_new = env.get_vissim_reward(180*5, transformed_action) 

                if (self.train_indicator):
                    # Add outputs to memory buffer
                    self.memorize(state_old, action, reward, state_new)
                    # Sample experience from buffer
                    states_old, actions, rewards, states_new = self.sample_batch(args.batch_size)
                    # Predict target q-values using target networks
                    q_values = self.critic.target_predict([states_new, self.actor.target_predict(states_new)])
                    # Compute critic target
                    critic_target = self.bellman(rewards, q_values)
                    # Train both networks on sampled batch, update target networks
                    self.update_models(states_old, actions, critic_target)
                    # calculate loss
                    loss += self.critic.train_on_batch(states_old, actions, critic_target)
                    state_old = state_new
                    cumul_reward += reward
                    time += 1

                print("|---> Step: ", t, " | Action: ", transformed_action, " | Reward: ", reward, " | Loss: ", loss)

                if np.mod(e, 10) == 0:
                    print("====================> Saving model...")
                    self.save_weights("./saved_model/")
                    """
                    with open("actormodel.json", "w") as outfile:
                        json.dump(actor.model.to_json(), outfile)
                    with open("criticmodel.json", "w") as outfile:
                        json.dump(critic.model.to_json(), outfile)
                    """

    def save_weights(self, path):
        path_actor = path + '_LR_{}'.format(self.lra)
        path_critic = path + '_LR_{}'.format(self.lrc)
        self.actor.save(path_actor)
        self.critic.save(path_critic)

    def load_weights(self, path_actor, path_critic):
        self.actor.load(path_actor)
        self.critic.load(path_critic)