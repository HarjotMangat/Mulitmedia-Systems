#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Harjot Mangat
# Environment for RL streaming adaptive chunk size

import numpy as np
import random
from tf_agents.environments import py_environment
from tf_agents.specs import array_spec
from tf_agents.trajectories import time_step as ts


"""
A class representing a streaming environment. An abstract buffer that
can fill up or empty out, a throughput amount for determining what packet size(chunk) to download
"""
class StreamingEnvironment(py_environment.PyEnvironment):
    
    Last_packet = 0
    Last_action = 0

    # creates and instance of the video stream; no parameters needed
    def __init__(self):        
        
        # action is choosing what chunk size to download ( sizes range from 0(low) to 4(high) )
        self._action_spec = array_spec.BoundedArraySpec(
            shape=(), dtype=np.int32, minimum=0, maximum=4, name='action') 
        # state is the current amount in the buffer(0-10), the current throughput(1-4), and the throughput(1-4) of the next step.
        self._observation_spec = array_spec.BoundedArraySpec(
            shape=(3,), dtype=np.int32, minimum=0, maximum = 10, name='state')
        self._state = np.array([[2],[2],[np.random.choice([1,2,3,4])]])
        self._episode_ended = False

    # standard PyEnvironment methods
    def action_spec(self):
        return self._action_spec

    def observation_spec(self):
        return self._observation_spec

    # when reset, the agent always goes back to beginning of a video
    # buffer has two packets, current throughput is 2, future throughput is random
    def _reset(self):
        self._state[0] = 2
        self._state[1] = 2
        self._state[2] = np.random.choice([1,2,3,4])
        StreamingEnvironment.Last_packet = 0
        StreamingEnvironment.Last_action = 0
        self._episode_ended = False
        return ts.restart(self._state)

    # computes transition and rewards 
    def _step(self, action):
        
        
        # overall idea of this environment:
        # we start with [2,2,random_future_throughput]
        # at each step, the buffer naturally decreases by 1
        # agent has to try to continue to get more packets based on the current and future throughput
        # if the agent requests a packet larger than the throughput, the packet will take too long to download and the buffer will reduce
        # goal is to get the agent to download just the right packet size to keep the buffer full, 
        # and keep packet size under the throughput limit.

        if self._episode_ended:
            # The last action ended the episode, so reset the env and start
            # a new episode.
            return self.reset()

        # buffer reduces by 1 at each step
        self._state[0] -= 1
        
        # determine reward
        
        # if buffer is empty, -1 reward and end episode
        if self._state[0] == 0:
            reward = -1
            self._episode_ended = True
            
        # if agent chose the best packet size for the throughput, reward it
        elif self._state[1] == action:
            reward = 1
        else:
            reward = 0
            
        # update state for next step
        
        # updating buffer based on action
        if action <= self._state[1] and StreamingEnvironment.Last_packet == 0: # if last action is <= current throughput and not waiting on last packet
            print("Action ", action, " fits within throughput ", self._state[1])
            if action + self._state[0] > 10: # check to see that action overflows the buffer
                self._state[0] = 10
            else:
                self._state[0] += action # update buffer with action
                print("Buffer size is now ", self._state[0])
        elif StreamingEnvironment.Last_packet != 0:
            if StreamingEnvironment.Last_packet > self._state[1]: # packet is still too large
                StreamingEnvironment.Last_packet = StreamingEnvironment.Last_packet - self._state[1]
                print("Still downloading packet ", StreamingEnvironment.Last_packet, " more bytes for this packet")
            else:
                if StreamingEnvironment.Last_action + self._state[0] > 10: # check to see that packet overflows the buffer
                    self._state[0] = 10
                else:
                    self._state[0] += StreamingEnvironment.Last_action # update buffer with last_packet
                    print("The chosen packet ", StreamingEnvironment.Last_action, " was finally downloaded")
                    print("The buffer is now ", self._state[0])
                    StreamingEnvironment.Last_packet = 0
        else: # this means the action/packet was too large for the current throughput. Need to carry it on to the next step.
            print("the chosen action ", action, "is too large for the available throughput ", self._state[1])
            StreamingEnvironment.Last_action = action
            StreamingEnvironment.Last_packet = action - self._state[1]
            print("Waiting for ", StreamingEnvironment.Last_packet, " more bytes for this packet")
        
        # updating the throughputs
        self._state[1] = self._state[2]
        self._state[2] = np.random.choice([1,2,3,4])
                                             
        
        if self._episode_ended:  # returns time_step of the appropriate type depending on whether episode ended or not
             return ts.termination(self._state, reward)
        else:
             return ts.transition(self._state, reward)
            
    def sample_new_state(self,state,action):
        
        new_state = np.array(state)
        
        new_state[0] -= 1
        
        if action <= new_state[1]:
            if action + new_state[0] >= 10:
                new_state[0] = 10
            else:
                new_state[0] += action
        elif action > new_state[1]:
            temp = action - new_state[1]
            if temp <= new_state[2]:
                new_state[0] -= 1
                if action + new_state[0] >= 10:
                    new_state[0] = 10
                else:
                    new_state[0] += action
            else:
                temp -= new_state[2]
                new_state[0] -= 2
        
        # now compute reward
        if new_state[0] <= 0:
            reward = -1
        elif action == new_state[1]:
            reward = 1
        else:
            reward = 0
            
        new_state[1] = new_state[2]
        new_state[2] = np.random.choice([1,2,3,4])
        
        return new_state,reward


# simple main function to test things out... 
if __name__ == "__main__":
    env = StreamingEnvironment()  # create an instance of the environemnt 
    
    done = False
    state = env.reset().observation
    print("Starting random policy...")
    while not done:
        print("Current state:",state)
        #actionset = env.valid_actions(state)
        if env.Last_packet != 0:
            action = 0
            print("waiting on last packet: ", env.Last_action)
        else:
            action = 2
        print("Executing action:", action)
        timestep = env.step(action)
        state = timestep.observation
        if timestep.is_last():
            print("Crashed!")
            done = True
        elif state[0] == 10:
            print("Finished one lap! Quitting now")
            done = True
        
    