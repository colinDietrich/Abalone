from player_abalone import PlayerAbalone
from game_state_abalone import GameStateAbalone
from seahorse.game.action import Action
from seahorse.game.game_state import GameState
from seahorse.utils.custom_exceptions import MethodNotImplementedError
import time


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
        self.other_id = possible_actions[0].get_next_game_state().next_player.get_id()
        depth = 3 # Depth of the minimax search (>1)
        action, score = self.miniMax(current_state, depth, alpha=float('-inf'), beta=float('inf'), maximizing=True)
        return action
    
    
    def miniMax(self, state: GameStateAbalone, depth: int, alpha, beta, maximizing: bool):
        """miniMax algorithm determine the best action with alpah-beta pruning
        
        Args:
            state (GameStateAbalone): The current game state.
            depth (int): The depth of the search from that state.
            alpha (float): The alpha value for alpha-beta pruning.
            beta (float): The beta value for alpha-beta pruning.
            maximizing (bool): Indicates whether the current player is maximizing or minimizing.

        Returns:
            Tuple[Action, int]: The best action and its corresponding score."""
        if depth == 0:
            return None, self.evaluate_state(state)
        
        if maximizing:
            # player maximizing
            max_score = float('-inf')
            best_action = None
            for action in state.get_possible_actions():
                # Recursively call miniMax for the next possible state with a minimizing player
                _, score = self.miniMax(action.get_next_game_state(), depth-1, alpha, beta, False)
                if score > max_score:
                    best_action, max_score = action, score
                # Alpha-beta pruning
                alpha = max(alpha, score)
                if beta <= alpha:
                    break
            return best_action, max_score
        else :
            # player minimizing
            min_score = float('inf')
            best_action = None
            for action in state.get_possible_actions():
                # Recursively call miniMax for the next possible state with a maximizing player
                _, score = self.miniMax(action.get_next_game_state(), depth-1, alpha, beta, True)
                if score < min_score:
                    best_action, min_score = action, score
                # Alpha-beta pruning
                beta = min(beta, score)
                if beta <= alpha:
                    break
            return best_action, min_score


    def evaluate_state(self, state:GameStateAbalone):
        """Computes the score of a state for the player that is the agent
        Score is calculated as the difference bewteen the score of each player"""
        # Avantage du nombre de billes
        ball_score = state.scores[self.id] - state.scores[self.other_id]
        # Avantage de placement : distance totale des pièces par rapport au centre du plateau
        grid = state.get_rep().get_env()
        central_position = (8, 4)
        player_pieces = []
        length_to_center = 0
        for coord in grid:
            if (grid[coord].get_owner_id() == self.id):
                player_pieces.append(coord)
                distance = self.manhattanDist(coord,central_position)
                length_to_center += distance
        
        # legnth to center used only to discriminate states with equal ball_score
        score = ball_score - length_to_center/1000
        return score
    
    def manhattanDist(self, A, B):
        # Note : la fonctionne pour une distance au centre ( A ou B = (8; 4))
        mask1 = [(0,2),(1,3),(2,4)]
        mask2 = [(0,4)]
        diff = (abs(B[0] - A[0]),abs(B[1] - A[1]))
        dist = (abs(B[0] - A[0]) + abs(B[1] - A[1]))/2
        if diff in mask1:
            dist += 1
        if diff in mask2:
            dist += 2
        return dist
    
    def degree_of_connectedness(self, piece_coordinates):
        """Calculate the degree of connectedness of pieces based on Manhattan distance between their coordinates.

        Args:
            piece_coordinates (list of tuples): List of coordinates (x, y) of the player's pieces.
        
        Returns:
            float: Degree of connectedness, ranging from 0 to 1."""
        total_distance = 0
        total_possible_distance = len(piece_coordinates) * (len(piece_coordinates) - 1) / 2  # Total possible combinations

        for i in range(len(piece_coordinates)):
            for j in range(i + 1, len(piece_coordinates)):
                # Calculate Manhattan distance between two coordinates
                distance = self.manhattanDist(piece_coordinates[i], piece_coordinates[j])
                total_distance += distance

        # Calculate degree of connectedness as the inverse of average normalized distance
        if total_possible_distance > 0:
            return 1 - (total_distance / (total_possible_distance * 6))  # Normalize distance to [0, 1] range
        else:
            return 0
    
    def order_moves(self, actions) -> list[Action]:
        """
        Trie les actions possibles selon la différence de score résultant de l'état qui
        découle de chaque action, dans le but de prioriser les actions les plus prometteuses.

        Args:
            actions (list[Action]): Une liste d'actions possibles à partir de l'état actuel du jeu.

        Returns:
            list[Action]: La liste des actions triées de manière décroissante selon la différence
            de score, favorisant les actions qui augmentent le plus le score du joueur par rapport
            à celui de l'adversaire.
        """
        # Trie les actions en fonction de la différence de score entre le score du joueur
        # après avoir effectué l'action et le score de l'adversaire dans l'état résultant.
        # 'reverse=True' assure que le tri est fait dans l'ordre décroissant, donc les actions
        # avec la plus grande différence de score (les plus avantageuses) sont placées en premier.
        return sorted(actions, key=lambda a: a.get_next_game_state().scores[self.id] - a.get_next_game_state().scores[self.other_id], reverse=True)
