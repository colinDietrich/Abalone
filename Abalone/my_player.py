from player_abalone import PlayerAbalone
from game_state_abalone import GameStateAbalone
from seahorse.game.action import Action
from seahorse.game.game_state import GameState
from seahorse.utils.custom_exceptions import MethodNotImplementedError
import time
from typing import Union, List

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
        self.time_limit = time_limit
        self.start_time = None
        self.transposition_table = {}
        self.best_action = None
        self.time_per_move = 20


    def compute_action(self, current_state: GameStateAbalone, max_depth: int = 5, **kwargs) -> Action:
        """
        Function to implement the logic of the player.

        Args:
            current_state (GameState): Current game state representation
            **kwargs: Additional keyword arguments

        Returns:
            Action: selected feasible action
        """
        #self.transposition_table.clear()  # Réinitialise la table de transposition pour chaque nouvelle recherche
        self.start_time = time.time()

        nodes = [0, 0]  # Nombre de noeuds visités / skippés pour chaque joueur
        self.start_time = time.time()
        possible_actions = list(current_state.get_possible_actions())
        self.other_id = possible_actions[0].get_next_game_state().next_player.get_id()
        # Effectue une recherche itérative en augmentant progressivement la profondeur de recherche
        for depth in range(1, max_depth + 1):
            print(f"depth = {depth}")
            action, score, nodes = self.miniMax(current_state, depth, alpha=float('-inf'), beta=float('inf'), maximizing=True, nodes=nodes)
            if(action is not None):
                self.best_action = action
            print(f"time = {time.time() - self.start_time}")
            print(f"nodes visités = {nodes[0]}")
            print(f"nodes skippés = {nodes[1]}")
            print(f"transposition table length = {len(self.transposition_table)}")
            if(time.time() - self.start_time > self.time_per_move):
                break

        return action
    
    def generate_state_key(self, state: GameStateAbalone, depth: int) -> int:
        """
        Génère une clé unique pour l'état actuel du jeu en utilisant la méthode __hash__
        de l'objet GameStateAbalone. Cette clé est utilisée pour identifier de manière unique
        l'état dans la table de transposition.

        Args:
            state: L'état actuel du jeu Abalone.

        Returns:
            Un entier représentant la clé unique de l'état actuel basée sur son hash.
        """
        # Utilise le hash de l'état du jeu comme clé
        key = hash(state) + hash(depth)
        return key

    
    def miniMax(self, state: GameStateAbalone, depth: int, alpha, beta, maximizing: bool, nodes: List[int]) -> Union[Action, int]:
        """miniMax algorithm determine the best action with alpah-beta pruning
        
        Args:
            state (GameStateAbalone): The current game state.
            depth (int): The depth of the search from that state.
            alpha (float): The alpha value for alpha-beta pruning.
            beta (float): The beta value for alpha-beta pruning.
            maximizing (bool): Indicates whether the current player is maximizing or minimizing.

        Returns:
            Tuple[Action, int]: The best action and its corresponding score."""

        state_key = self.generate_state_key(state, depth)  # Clé unique de l'état pour la table de transposition

        if state_key in self.transposition_table:  # Recherche dans la table de transposition
            nodes[1] += 1  # Incrémente le nombre de noeuds skipés
            return None, self.transposition_table[state_key], nodes
        
        nodes[0] += 1  # Incrémente le nombre de noeuds visités
        
        if depth == 0:
            return None, self.evaluate_state(state), nodes
        
        if maximizing:
            # player maximizing
            max_score = float('-inf')
            best_action = None
            for action in state.get_possible_actions():
                # Recursively call miniMax for the next possible state with a minimizing player
                _, score, nodes = self.miniMax(action.get_next_game_state(), depth-1, alpha, beta, False, nodes)
                if score > max_score:
                    best_action, max_score = action, score
                # Alpha-beta pruning
                alpha = max(alpha, score)
                if beta <= alpha:
                    break
            self.transposition_table[state_key] = score  # Mise à jour de la table de transposition
            return best_action, max_score, nodes
        else :
            # player minimizing
            min_score = float('inf')
            best_action = None
            for action in state.get_possible_actions():
                # Recursively call miniMax for the next possible state with a maximizing player
                _, score, nodes = self.miniMax(action.get_next_game_state(), depth-1, alpha, beta, True, nodes)
                if score < min_score:
                    best_action, min_score = action, score
                # Alpha-beta pruning
                beta = min(beta, score)
                if beta <= alpha:
                    break
            self.transposition_table[state_key] = score  # Mise à jour de la table de transposition
            return best_action, min_score, nodes


    def evaluate_state(self, state:GameStateAbalone):
        """Computes the score of a state for the player that is the agent
        Score is calculated as the difference bewteen the score of each player"""
        score = state.scores[self.id] - state.scores[self.other_id]
        return score
