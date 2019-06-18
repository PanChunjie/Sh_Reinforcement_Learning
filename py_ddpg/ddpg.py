import sys
import numpy as np
import datetime
import os
import glob
import gc

from actor import Actor
from critic import Critic
from utils.networks import tfSummary
from utils.memory_buffer import MemoryBuffer
from utils.report import Report
from utils.noise import OrnsteinUhlenbeckActionNoise

from Transformation import Transformation

class DDPG(object):
    """ Deep Deterministic Policy Gradient (DDPG) Helper Class
    """

    def __init__(self, action_dim, state_dim, batch_size, step, buffer_size, train_indicator, episode, gamma, lra, lrc, tau, reward_threshold, load_weight=True):
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
        self.reward_threshold = reward_threshold
        # Create actor and critic networks
        self.actor = Actor(state_dim, action_dim, batch_size, lra, tau)
        self.critic = Critic(state_dim, action_dim, batch_size, lrc, tau)
        #-----------------------------------------------------------------*
        """
        using previous buffer, set True.
        not using previous buffer, set False
        """
        self.buffer = MemoryBuffer(buffer_size, False, True)
        #self.buffer = MemoryBuffer(buffer_size, False, False)
        #-----------------------------------------------------------------*        

        # !: weights folder need to be specified & ensure only one set of A&C weights are in this folder
        self.weights_dir_path = os.getcwd() + r"\saved_model\*.h5"

        if load_weight:
            try:
                weights_actor_path = ""
                weights_critic_path = ""
                weights_file_path = glob.glob(self.weights_dir_path)

                for file_path in weights_file_path:
                    if file_path.find("actor") < 0:
                        weights_critic_path = file_path
                    if file_path.find("critic") < 0:
                        weights_actor_path = file_path

                self.load_weights(weights_actor_path, weights_critic_path)

                print("")
                print("Actor-Critic Models are loaded with weights...")
                print("")
            except:
                print("")
                print("Weights are failed to be loaded, please check weights loading path...")
                print("")

    def policy_action(self, s):
        """ Use the actor to predict value
        """
        return self.actor.predict(s)[0]

    def bellman(self, rewards, q_values, dones):
        """ Use the Bellman Equation to compute the critic target (one action only)
        """
        critic_target = np.asarray(q_values)
        for i in range(q_values.shape[0]):
            if dones[i]:
                critic_target[i] = rewards[i]
            else:
                critic_target[i] = rewards[i] + self.gamma * q_values[i]
        return critic_target

    def memorize(self, state_old, action, reward, done, state_new):
        """ Store experience in memory buffer
        """
        self.buffer.memorize(state_old, action, reward, done, state_new)

    def sample_batch(self, batch_size):
        return self.buffer.sample_batch(batch_size)

    def update_models(self, states, actions, critic_target):
        """ Update actor and critic networks from sampled experience
        """
        # Train critic
        loss = self.critic.train_on_batch(states, actions, critic_target)
        # Q-Value Gradients under Current Policy
        actions = self.actor.model.predict(states)
        grads = self.critic.gradients(states, actions)
        # Train actor
        self.actor.train(states, actions, np.array(grads).reshape((-1, self.action_dim)))
        # Transfer weights to target networks at rate Tau
        self.actor.transfer_weights()
        self.critic.transfer_weights()
        return loss

    def run(self, env):
        report = Report()
        # add line spliter
        report.updateReport(r"\report\report.csv", ["===========================================" + str(datetime.datetime.now())])
        report.updateReport(r"\report\episode_report.csv", ["===========================================" + str(datetime.datetime.now())])

        # First, gather experience
        for e in range(self.episode):
            # Reset episode
            #env.reset()
            # set initial state
            loss, cumul_reward, cumul_loss = 0, 0, 0
            done = False
            state_old = env.get_vissim_state(1, 180*5, [45, 55, 60, 65, 70, 75, 80]) #TODO: make sure states are recieved correctly
            actions, states, rewards = [], [], []

            print("Episode: ", e, " ========================:")

            #for t in range(self.step):
            t = 0

            while not done:
                t += 1
                action_original = self.policy_action(state_old)
                
                #TODO: OU function params?
                # 1st OU test
                #noise = OrnsteinUhlenbeckProcess(x0=action_original, size=self.action_dim)
                # 2nd OU test
                noise = OrnsteinUhlenbeckActionNoise(action_dim=self.action_dim)

                action_original += noise.ou_noise()
                action = np.clip(action_original, 0, 1)

                #action_mapping function
                transformed_action = Transformation.convert_actions(action)

                reward, state_new = env.get_vissim_reward(180*5, transformed_action)

                # TODO: if we know what the optimal discharging rate, then we set that as done
                # if t == self.step - 1:
                if reward < self.reward_threshold: #we consider the manually setted last step as done
                    done = True

                # ======================================================================================= Training section
                if (self.train_indicator):
                    # Add outputs to memory buffer
                    self.memorize(state_old, action, reward, done, state_new)
                    # Sample experience from buffer
                    states_old, actions, rewards, dones, states_new = self.sample_batch(self.batch_size)
                    # Predict target q-values using target networks
                    q_values = self.critic.target_predict([states_new, self.actor.target_predict(states_new)])
                    # Compute critic target
                    critic_target = self.bellman(rewards, q_values, dones)
                    # Train both networks on sampled batch, update target networks
                    loss = self.update_models(states_old, actions, critic_target)

                    state_old = state_new
                    cumul_reward += reward
                    cumul_loss += loss
                # =======================================================================================                     

                # ======================================================================================= report
                print("|---> Step: ", t, " | Action: ", transformed_action, " | Reward: ", reward, " | Loss: ", loss)
                report.updateReport(r"\report\report.csv", [str(e), str(t), str(reward), str(loss)])
                # =======================================================================================                 

            # ======================================================================================= save model
            if np.mod(e, 10) == 0:
                print("====================> Saving model...")
                self.save_weights("./saved_model/")
                """
                with open("actormodel.json", "w") as outfile:
                    json.dump(actor.model.to_json(), outfile)
                with open("criticmodel.json", "w") as outfile:
                    json.dump(critic.model.to_json(), outfile)
                """
            # ======================================================================================= save model

            print("")
            print("*-------------------------------------------------*")
            t = datetime.datetime.now()
            time = str(t.date()) + "_" + str(t.hour) + "h-" + str(t.minute) + "m"
            print("Average Accumulated Reward: " + str(cumul_reward / self.step) )
            print("Average Accumulated Loss: " + str(cumul_loss / self.step) )
            report.updateReport(r"\report\episode_report.csv", [str(e), time, str(cumul_reward / self.step), str(cumul_loss / self.step)])
            print("*-------------------------------------------------*")
            print("")

            # garbage recycling
            gc.collect()

    def save_weights(self, path):
        t = datetime.datetime.now()
        time = "_" + str(t.date()) + "_" + str(t.hour) + "h-" + str(t.minute) + "m"
        path_actor = path + '_LR_{}'.format(self.lra) + time
        path_critic = path + '_LR_{}'.format(self.lrc) + time
        self.actor.save(path_actor)
        self.critic.save(path_critic)

    def load_weights(self, path_actor, path_critic):
        self.actor.load(path_actor)
        self.critic.load(path_critic)