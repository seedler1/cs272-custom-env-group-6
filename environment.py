import gymnasium as gym
import random
from gymnasium import spaces

class PokerWorldEnv(gym.Env):
    def __init__(self):
        # We have 2 actions, corresponding to "Raise", "Fold"
        self.action_space = spaces.Discrete(3)
        
       
        self.observation_space = spaces.Dict(
            {
                "agent": spaces.Tuple(spaces.Discrete(52), spaces.Discrete(52)),
                "villain": spaces.Tuple(spaces.Discrete(52), spaces.Discrete(52)),
                "cards": spaces.Tuple(spaces.Discrete(52), 
                                      spaces.Discrete(52),
                                      spaces.Discrete(52),
                                      spaces.Discrete(52), 
                                      spaces.Discrete(52)),
                "pot": spaces.Discrete(200),
                "agent_stack": spaces.Discrete(100),
                "villain_stack": spaces.Discrete(100),
            }
        )
        
        self._actions = {
            1: 100, # Raise
            2: 0 # Fold
        }
        
# %%
# Dealing the cards
# Parameters:
#   num_of_cards : The number of cards dealt
# Returns:
#   A tuple of number representing the cards
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Author: Jennifer Chun
        
    def _deal(self, num_of_cards):
        pass

# %%
# Getting the kind of hands (ranking) that either play has given their hole cards
# and what's on the board.
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Author: Jennifer Chun
        
    def _hands(self, hole_cards):
        pass
    
# %%
# If the villain "has something" (in our case, means the villain has 
# something greater than just "high card") 
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Author: Jennifer Chun

    def _has_something(self, hole_cards):
       pass 
        
# %%
# Constructing Observations From Environment States
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# Since we will need to compute observations both in ``reset`` and
# ``step``, it is often convenient to have a (private) method ``_get_obs``
# that translates the environment’s state into an observation. However,
# this is not mandatory and you may as well compute observations in
# ``reset`` and ``step`` separately:

    def _get_obs(self):
        return {"agent": self._agent_cards, "villain": self._villain_cards,
                "cards": self._cards, "pot": self._pot, "agent_stack": self._agent_stack, 
                "vilain_stack": self._villain_stack}

# %%
# We can also implement a similar method for the auxiliary information
# that is returned by ``step`` and ``reset``. In our case, we would like
# to provide what kind of hand the hero has:

    def _get_info(self):
        return {
            "hands": self._hands(self._agent_cards)
        }
        
# %%
# Oftentimes, info will also contain some data that is only available
# inside the ``step`` method (e.g. individual reward terms). In that case,
# we would have to update the dictionary that is returned by ``_get_info``
# in ``step``.

# %%
# Reset
# ~~~~~
#
# The ``reset`` method will be called to initiate a new episode. You may
# assume that the ``step`` method will not be called before ``reset`` has
# been called. Moreover, ``reset`` should be called whenever a done signal
# has been issued. Users may pass the ``seed`` keyword to ``reset`` to
# initialize any random number generator that is used by the environment
# to a deterministic state. It is recommended to use the random number
# generator ``self.np_random`` that is provided by the environment’s base
# class, ``gymnasium.Env``. If you only use this RNG, you do not need to
# worry much about seeding, *but you need to remember to call
# ``super().reset(seed=seed)``* to make sure that ``gymnasium.Env``
# correctly seeds the RNG. Once this is done, we can randomly set the
# state of our environment. In our case, we randomly choose the agent’s
# location and the random sample target positions, until it does not
# coincide with the agent’s position.
#
# The ``reset`` method should return a tuple of the initial observation
# and some auxiliary information. We can use the methods ``_get_obs`` and
# ``_get_info`` that we implemented earlier for that:

    def reset(self, seed=None, options=None):
        
        self._villain_cards = self._deal(2)
        self._agent_cards = self._deal(2)
        self._cards = self._deal(5)
        
        self._villain_stack = 100
        self._hero_stack = 100

        observation = self._get_obs()
        info = self._get_info()


        return observation, info

# %%
# Step
# ~~~~
# In our simplified game version, the agent will always go first postflop.
# This does not occur in a real game, where players will alternate going first
# postflop. 
#
# The ``step`` method usually contains most of the logic of your
# environment. It accepts an ``action``, computes the state of the
# environment after applying that action and returns the 5-tuple
# ``(observation, reward, terminated, truncated, info)``. See
# :meth:`gymnasium.Env.step`. Once the new state of the environment has
# been computed, we can check whether it is a terminal state and we set
# ``done`` accordingly. Since we are using sparse binary rewards in
# ``GridWorldEnv``, computing ``reward`` is trivial once we know
# ``done``.To gather ``observation`` and ``info``, we can again make
# use of ``_get_obs`` and ``_get_info``:

    def step(self, action):
        tied = False # If the hero and villain has the same hand. 
        villain_folded = False # If the villain decides to fold
        villain_raised = False # If the villain decides to raise.
        
        if action == 1: # If the agent decides to Raise
            if (self._has_something(self._villain_cards)):
                if random.random() <= 0.75: 
                    villain_raised = True
                    if self._hands(self._villain_cards) > self._hands(self._hero_cards):
                        self._villain_stack = 200
                        self._hero_stack = 0
                    elif self._hands(self._hero_cards) > self._hands(self._villain_cards):
                        self._villain_stack = 0
                        self._hero_stack = 200
                    else:
                        self._villain_stack = 100
                        self._hero_stack = 100
                else:
                    villain_folded = True
            else:
                if random.random() <= 0.10: 
                    villain_raised = True 
                    if self._hands(self._villain_cards) > self._hands(self._hero_cards):
                        self._villain_stack = 200
                        self._hero_stack = 0
                    elif self._hands(self._hero_cards) > self._hands(self._villain_cards):
                        self._villain_stack = 0
                        self._hero_stack = 200
                    else:
                        self._villain_stack = 100
                        self._hero_stack = 100
                else:
                    villain_folded = True
        elif action == 2: # Agent decides to fold
            self._villain_stack = 100
            self._hero_stack = 100
        
        
        # An episode is done iff the agent has reached the target
        terminated = self._villain_stack == 200 or self._hero_stack == 200 or action == 2 or tied or villain_folded
        if (terminated and self._hero_stack == 200 and self._villain_stack == 0) or (terminated and villain_folded):
            reward = 1
        elif terminated and action == 2:
            reward = 0
        elif terminated and tied:
            reward = 0
        elif terminated and self._villain_stack == 200 and self._hero_stack == 0:
            reward = -1
        
        observation = self._get_obs()
        info = self._get_info()


        return observation, reward, terminated, False, info        
    
# %%
# Close
# ~~~~~
#
# The ``close`` method should close any open resources that were used by
# the environment. In many cases, you don’t actually have to bother to
# implement this method. However, in our example ``render_mode`` may be
# ``"human"`` and we might need to close the window that has been opened:

    def close(self):
        pass