import random
import numpy as np
import os
import csv

from collections import deque
from .sumtree import SumTree

class MemoryBuffer(object):
    """ Memory Buffer Helper class for Experience Replay
    using a double-ended queue or a Sum Tree (for PER)
    """
    def __init__(self, buffer_size, with_per = False, load_old_buffer = False):
        """ Initialization
        """
        if(with_per):
            # Prioritized Experience Replay
            self.alpha = 0.5
            self.epsilon = 0.01
            self.buffer = SumTree(buffer_size)
        else:
            # Standard Buffer
            self.buffer = deque()
        self.count = 0
        self.with_per = with_per
        self.buffer_size = buffer_size


        # windows path
        self.buffer_path = {
            "state_old": os.getcwd() + r"\memory\state_old.csv",
            "action": os.getcwd() + r"\memory\action.csv",
            "reward": os.getcwd() + r"\memory\reward.csv",
            "done": os.getcwd() + r"\memory\done.csv",
            "state_new": os.getcwd() + r"\memory\state_new.csv",
            }

        """
        # linux & mac path
        self.buffer_path = {
            "state_old": os.getcwd() + "/memory/state_old.csv",
            "action": os.getcwd() + "/memory/action.csv",
            "reward": os.getcwd() + "/memory/reward.csv",
            "done": os.getcwd() + "/memory/done.csv",
            "state_new": os.getcwd() + "/memory/state_new.csv",
            }
        """
        if load_old_buffer:
            self.load_buffer()

    def memorize(self, state_old, action, reward, done, state_new, error=None):
        """ Save an experience to memory, optionally with its TD-Error
        """
        experience = (state_old, action, reward, done, state_new)
        if(self.with_per):
            priority = self.priority(error[0])
            self.buffer.add(priority, experience)
            self.count += 1
        else:
            # Check if buffer is already full
            if self.count < self.buffer_size:
                self.buffer.append(experience)
                self.count += 1
            else:
                self.buffer.popleft()
                self.buffer.append(experience)

        self.save_buffer(experience)

    def priority(self, error):
        """ Compute an experience priority, as per Schaul et al.
        """
        return (error + self.epsilon) ** self.alpha

    def size(self):
        """ Current Buffer Occupation
        """
        return self.count

    def sample_batch(self, batch_size):
        """ Sample a batch, optionally with (PER)
        """
        batch = []

        # Sample using prorities
        if(self.with_per):
            T = self.buffer.total() // batch_size
            for i in range(batch_size):
                a, b = T * i, T * (i + 1)
                s = random.uniform(a, b)
                idx, error, data = self.buffer.get(s)
                batch.append((*data, idx))
            idx = np.array([i[4] for i in batch])
        # Sample randomly from Buffer
        elif self.count < batch_size:
            idx = None
            batch = random.sample(self.buffer, self.count)
        else:
            idx = None
            batch = random.sample(self.buffer, batch_size)

        # Return a batch of experience
        s_o_batch = np.array([i[0] for i in batch])
        a_batch = np.array([i[1] for i in batch])
        r_batch = np.array([i[2] for i in batch])
        d_batch = np.array([i[3] for i in batch])
        s_n_batch = np.array([i[4] for i in batch])
        return s_o_batch, a_batch, r_batch, d_batch, s_n_batch

    def update(self, idx, new_error):
        """ Update priority for idx (PER)
        """
        self.buffer.update(idx, self.priority(new_error))

    def clear(self):
        """ Clear buffer / Sum Tree
        """
        if(self.with_per): self.buffer = SumTree(buffer_size)
        else: self.buffer = deque()
        self.count = 0


    def load_buffer(self):
        empty = False
        n = -1

        old_buffer = {
            "state_old": [],
            "action": [],
            "reward": [],
            "done": [],
            "state_new": [],
        }

        print("")
        print("loading old_buffer...")
        print("")        

        for k in self.buffer_path.keys():
            with open(self.buffer_path[k], 'r') as fileReader:
                if k == "reward":
                    reader = csv.reader(fileReader, quoting=csv.QUOTE_NONNUMERIC)
                    for r in list(reader):
                        old_buffer[k].append(r[0])
                elif k == "done":
                    reader = csv.reader(fileReader)
                    temp = []
                    for r in list(reader):
                        if r[0] == "True":
                            temp.append(True)
                        else:
                            temp.append(False)
                    old_buffer[k] = temp
                elif k == "action":
                    reader = csv.reader(fileReader, quoting=csv.QUOTE_NONNUMERIC)
                    for r in list(reader):
                        old_buffer[k].append(np.array(r))
                else:
                    reader = csv.reader(fileReader, quoting=csv.QUOTE_NONNUMERIC)
                    old_buffer[k] = list(reader)

                n = len(old_buffer[k])

                empty = n < 1
                if empty:
                    break

        if not empty:
            print("")
            print("old_buffer is loaded...")
            print("")

            for i in range(n):
                self.memorize(
                    old_buffer["state_old"][i],
                    old_buffer["action"][i],
                    old_buffer["reward"][i],
                    old_buffer["done"][i],
                    old_buffer["state_new"][i])
        else:
            print("")
            print("old_buffer is empty, quit loading old_buffer...")
            print("")

        fileReader.close()

    def save_buffer(self, experience):
        keys = ["state_old", "action", "reward", "done", "state_new"]

        for k in keys:
            with open(self.buffer_path[k], 'a') as fileWriter:
                writer = csv.writer(fileWriter)
                record = experience[keys.index(k)]
                if type(record) == type(np.array([])):
                    record.tolist()
                elif type(record) != type([]):
                    record = [record]
                writer.writerow(record)

        fileWriter.close()

