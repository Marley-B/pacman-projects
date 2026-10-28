# multi_agents.py
# --------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from util import manhattan_distance
from game import Directions, Actions
from pacman import GhostRules
import random, util
from game import Agent

class ReflexAgent(Agent):
    """
    A reflex agent chooses an action at each choice point by examining
    its alternatives via a state evaluation function.

    The code below is provided as a guide.  You are welcome to change
    it in any way you see fit, so long as you don't touch our method
    headers.
    """


    def get_action(self, game_state):
        """
        You do not need to change this method, but you're welcome to.

        get_action chooses among the best options according to the evaluation function.

        Just like in the previous project, get_action takes a GameState and returns
        some Directions.X for some X in the set {NORTH, SOUTH, WEST, EAST, STOP}
        """
        # Collect legal moves and successor states
        legal_moves = game_state.get_legal_actions()

        # Choose one of the best actions
        scores = [self.evaluation_function(game_state, action) for action in legal_moves]
        best_score = max(scores)
        best_indices = [index for index in range(len(scores)) if scores[index] == best_score]
        chosen_index = random.choice(best_indices) # Pick randomly among the best

        "Add more of your code here if you want to"

        return legal_moves[chosen_index]

    def evaluation_function(self, current_game_state, action):
        """
        Design a better evaluation function here.

        The evaluation function takes in the current and proposed successor
        GameStates (pacman.py) and returns a number, where higher numbers are better.

        The code below extracts some useful information from the state, like the
        remaining food (new_food) and Pacman position after moving (new_pos).
        new_scared_times holds the number of moves that each ghost will remain
        scared because of Pacman having eaten a power pellet.

        Print out these variables to see what you're getting, then combine them
        to create a masterful evaluation function.
        """
        # Useful information you can extract from a GameState (pacman.py)
        successor_game_state = current_game_state.generate_pacman_successor(action)
        new_pos = successor_game_state.get_pacman_position()
        new_food = successor_game_state.get_food()
        new_ghost_states = successor_game_state.get_ghost_states()
        new_scared_times = [ghostState.scared_timer for ghostState in new_ghost_states]
        
        "*** YOUR CODE HERE ***"
        # get the gost's positions and the food's as lists
        ghosts_position = successor_game_state.get_ghost_positions()
        food_position = new_food.as_list()

        ghost_grade = 0
        food_grade = 0
        distance_to_ghost = float('inf')
        ghost_scared = 0
        num_ghost = len(ghosts_position)

        # we look through all the ghosts and add their properties to grade
        for i in range(num_ghost):
            distance_to_ghost = manhattan_distance(new_pos, ghosts_position[i])
            ghost_scared = new_scared_times[i]

            # if we can eat the nearest ghost we reward going to it
            if ghost_scared > 0:
                ghost_grade += 1/(distance_to_ghost+1)
            #if the ghost is agressive and close we discourage approaching it
            elif distance_to_ghost < 5: 
                ghost_grade += (-1/(distance_to_ghost+1))*1.1  #1.1 weight on the ghost so it prioritizes surviving over food
            #if the ghost is far and harmfull, we ignore it


        if not food_position: #if there is no more food
            food_grade = 0
        else:
            distance_to_food = min(manhattan_distance(new_pos, food)for food in food_position)
            food_grade = 1/(distance_to_food+1) # [0,1]

        #print(ghost_grade, food_grade, num_ghost)
        return successor_game_state.get_score() + ghost_grade + food_grade

def score_evaluation_function(current_game_state):
    """
    This default evaluation function just returns the score of the state.
    The score is the same one displayed in the Pacman GUI.

    This evaluation function is meant for use with adversarial search agents
    (not reflex agents).
    """
    return current_game_state.get_score()

class MultiAgentSearchAgent(Agent):
    """
    This class provides some common elements to all of your
    multi-agent searchers.  Any methods defined here will be available
    to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

    You *do not* need to make any changes here, but you can if you want to
    add functionality to all your adversarial search agents.  Please do not
    remove anything, however.

    Note: this is an abstract class: one that should not be instantiated.  It's
    only partially specified, and designed to be extended.  Agent (game.py)
    is another abstract class.
    """

    def __init__(self, eval_fn='score_evaluation_function', depth='2'):
        super().__init__()
        self.index = 0 # Pacman is always agent index 0
        self.evaluation_function = util.lookup(eval_fn, globals())
        self.depth = int(depth) 

class MinimaxAgent(MultiAgentSearchAgent):
    """
    Your minimax agent (question 2)
    """
    def get_action(self, game_state):
        """
        Returns the minimax action from the current game_state using self.depth
        and self.evaluation_function.

        Here are some method calls that might be useful when implementing minimax.

        game_state.get_legal_actions(agent_index):
        Returns a list of legal actions for an agent
        agent_index=0 means Pacman, ghosts are >= 1

        game_state.generate_successor(agent_index, action):
        Returns the successor game state after an agent takes an action

        game_state.get_num_agents():
        Returns the total number of agents in the game

        game_state.is_win():
        Returns whether or not the game state is a winning state

        game_state.is_lose():
        Returns whether or not the game state is a losing state
        """
        "*** YOUR CODE HERE ***"
        def minimax(state, index, depth):
            if depth == 0 or state.is_win() or state.is_lose(): #Base case
                return self.evaluation_function(state)
            else:
                actions = state.get_legal_actions(index)
                num_agents = state.get_num_agents()
                next_agent = (index + 1) % num_agents
                new_depth = depth - 1 if  next_agent == 0 else depth
                if index == 0:
                    return max(minimax(state.generate_successor(index, action), next_agent, new_depth)for action in actions) #Recursive case for Pacman
                else:
                    return min(minimax(state.generate_successor(index, action), next_agent, new_depth)for action in actions) #Recursive case for ghosts
        
        actions = game_state.get_legal_actions(0) #We start with Pacman
        best_value = float('-inf')
        best_action = None
        for action in actions:
            value = minimax(game_state.generate_successor(0, action), 1, self.depth) #We start the call with Pacman and its actions, but it will be the turn of the ghost
            if best_value < value:
                best_value = value
                best_action = action
        return best_action
        


class AlphaBetaAgent(MultiAgentSearchAgent):
    """
    Your minimax agent with alpha-beta pruning (question 3)
    """

    def get_action(self, game_state):
        """
        Returns the minimax action using self.depth and self.evaluation_function
        """
        "*** YOUR CODE HERE ***"
        def max_value(state, alpha, beta, index, depth):
            if depth == 0 or state.is_win() or state.is_lose(): #Base case
                return self.evaluation_function(state)
            else: 
                v = float('-inf')
                actions = state.get_legal_actions(index)
                num_agents = state.get_num_agents()
                next_agent = (index + 1) % num_agents
                new_depth = depth - 1 if  next_agent == 0 else depth
                for action in actions:
                    v = max(v, min_value(state.generate_successor(index, action), alpha, beta, next_agent, new_depth))
                    if v > beta: # if we have found a beta smaller than the current max in the branch, we prune
                        return v
                    alpha = max(v, alpha) #Update alpha for the next child
                return v

        def min_value(state, alpha, beta, index, depth):
            if depth == 0 or state.is_win() or state.is_lose(): #Base case
                return self.evaluation_function(state)
            else:
                v = float('inf')
                actions = state.get_legal_actions(index)
                num_agents = state.get_num_agents()
                next_agent = (index + 1) % num_agents
                new_depth = depth - 1 if  next_agent == 0 else depth
                for action in actions:
                    if next_agent == 0:
                        v_child = max_value(state.generate_successor(index, action), alpha, beta, next_agent, new_depth) #In case Pacman is the next_agent
                    else:
                        v_child = min_value(state.generate_successor(index, action), alpha, beta, next_agent, new_depth) #In case a ghost is the next_agent
                    v = min(v_child, v) #In both cases the ghost will minimize
                    if v < alpha: # if we have found an alpha biger than the current min in the branch, we prune
                        return v
                    beta = min(v, beta) #Update beta for the next child
                return v
        
        alpha = float('-inf')
        beta = float('inf')
        best_action = None
        best_value = float('-inf')
        actions = game_state.get_legal_actions(0)
        for action in actions:
            value = min_value(game_state.generate_successor(0, action), alpha, beta, 1, self.depth) #We start with Pacman aka the max player, but since the next agent will be a ghost we use min_value
            if best_value < value:
                best_value = value
                best_action = action
            alpha = max(best_value, alpha) #Since we're Pacman we maximize
        return best_action


class ExpectimaxAgent(MultiAgentSearchAgent):
    """
      Your expectimax agent (question 4)
    """

    def get_action(self, game_state):
        """
        Returns the expectimax action using self.depth and self.evaluation_function

        All ghosts should be modeled as choosing uniformly at random from their
        legal moves.
        """
        "*** YOUR CODE HERE ***"
        util.raise_not_defined()

def better_evaluation_function(current_game_state):
    """
    Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
    evaluation function (question 5).

    DESCRIPTION: <write something here so we know what you did>
    """
    "*** YOUR CODE HERE ***"
    util.raise_not_defined()
    


# Abbreviation
better = better_evaluation_function
