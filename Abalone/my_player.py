from player_abalone import PlayerAbalone
from game_state_abalone import GameStateAbalone
from seahorse.game.action import Action
from seahorse.game.game_state import GameState
from seahorse.utils.custom_exceptions import MethodNotImplementedError


class MyPlayer(PlayerAbalone):
    """
    Player class for Abalone game.

    Attributes:
        piece_type (str): piece type of the player
    """

    def __init__(self, piece_type: str, name: str = "bob", time_limit: float=60*15,*args) -> None:
        """
        Initialize the PlayerAbalone instance.

        Args:
            piece_type (str): Type of the player's game piece
            name (str, optional): Name of the player (default is "bob")
            time_limit (float, optional): the time limit in (s)
        """
        super().__init__(piece_type,name,time_limit,*args)


    def compute_action(self, current_state: GameStateAbalone, **kwargs) -> Action:
        """
        Function to implement the logic of the player.

        Args:
            current_state (GameState): Current game state representation
            **kwargs: Additional keyword arguments

        Returns:
            Action: selected feasible action
        """
        possible_actions = list(current_state.get_possible_actions())
        print(current_state)
        self.other_id = possible_actions[0].get_next_game_state().next_player.get_id()
        depth = 2 #at least 1
        action, score = self.miniMax(current_state, depth, True)
        return action
    
    
    def miniMax(self, state: GameStateAbalone, depth, maximizing):
        """miniMax algorithm determine the best action"""
        if depth == 0:
            return None, self.utility(state)
        
        if maximizing:
            # player maximizing
            max_score = -7
            best_action = None
            for action in state.get_possible_actions():
                _, score = self.miniMax(action.get_next_game_state(), depth-1, False)
                if score > max_score:
                    best_action, max_score = action, score
            return best_action, max_score
        else :
            # player minimizing
            min_score = 7
            best_action = None
            for action in state.get_possible_actions():
                _, score = self.miniMax(action.get_next_game_state(), depth-1, True)
                if score < min_score:
                    best_action, min_score = action, score
            return best_action, min_score


    def utility(self, state:GameStateAbalone):
        """Computes the score of a state for the player that is the agent
        Score is calculated as the difference bewteen the score of each player"""
        score = state.scores[self.id] - state.scores[self.other_id]
        return score
