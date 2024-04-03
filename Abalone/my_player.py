from player_abalone import PlayerAbalone
from game_state_abalone import GameStateAbalone
from seahorse.game.action import Action
from seahorse.game.game_state import GameState
from seahorse.utils.custom_exceptions import MethodNotImplementedError
import time  # Import time module to keep track of elapsed time


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

    def compute_action(self, current_state: GameStateAbalone, max_depth: int = 20, **kwargs) -> Action:
        """
        Détermine la meilleure action à effectuer en utilisant l'algorithme MiniMax avec Alpha-Beta pruning,
        combiné à l'Iterative Deepening et une Transposition Table jusqu'à une profondeur maximale spécifiée.

        Args:
            current_state (GameStateAbalone): L'état actuel du jeu.
            max_depth (int): La profondeur maximale de recherche pour l'approfondissement itératif.

        Returns:
            Action: La meilleure action déterminée pour le joueur actuel.
        """
        self.transposition_table.clear()  # Réinitialise la table de transposition pour chaque nouvelle recherche
        self.start_time = time.time()
        best_action = None

        # Effectue une recherche itérative en augmentant progressivement la profondeur de recherche
        for depth in range(1, max_depth + 1):
            best_action = self.depth_limited_search(current_state, depth)
            # Interrompt la recherche si le temps alloué est dépassé
            if (time.time() - self.start_time) > self.time_limit/10:
                break

        return best_action
    
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
        return sorted(actions, key=lambda a: a.get_next_game_state().scores[self.id] - a.get_next_game_state().scores[a.get_next_game_state().next_player.get_id()], reverse=True)

    

    def depth_limited_search(self, current_state: GameStateAbalone, depth: int) -> Action:
        """
        Effectue une recherche limitée en profondeur en utilisant l'algorithme MiniMax avec Alpha-Beta pruning.

        Args:
            current_state (GameStateAbalone): L'état actuel du jeu.
            depth (int): La profondeur limite pour la recherche.

        Returns:
            Action: La meilleure action trouvée à la profondeur spécifiée.
        """
        best_score = float('-inf')
        best_action = None

        # Trie les actions possibles pour maximiser l'Alpha-Beta pruning
        possible_actions = current_state.get_possible_actions()
        ordered_actions = self.order_moves(possible_actions)
        # Parcourt toutes les actions possibles pour trouver celle qui maximise le score
        for action in ordered_actions:
            score = self.minimax_with_alpha_beta(action.get_next_game_state(), depth - 1, float('-inf'), float('inf'), False)
            if score > best_score:
                best_score = score
                best_action = action

        return best_action

    def minimax_with_alpha_beta(self, state: GameStateAbalone, depth: int, alpha: float, beta: float, maximizing_player: bool) -> int:
        """
        Implémente l'algorithme MiniMax avec Alpha-Beta pruning pour évaluer les états de jeu.

        Args:
            state (GameStateAbalone): L'état du jeu à évaluer.
            depth (int): La profondeur actuelle de la recherche.
            alpha (float): La valeur Alpha pour l'Alpha-Beta pruning.
            beta (float): La valeur Beta pour l'Alpha-Beta pruning.
            maximizing_player (bool): Indique si le joueur actuel est en train de maximiser ou minimiser le score.

        Returns:
            int: La valeur évaluée de l'état du jeu.
        """
        state_key = self.generate_state_key(state)  # Clé unique de l'état pour la table de transposition

        if state_key in self.transposition_table:  # Recherche dans la table de transposition
            return self.transposition_table[state_key]

        if depth == 0 or state.is_done():
            score = self.evaluate(state)  # Évaluation de l'état terminal ou à profondeur nulle
        else:
            # Initialisation du score selon le type de joueur (maximiseur ou minimiseur)
            score = float('-inf') if maximizing_player else float('inf')
            # Trie les actions possibles pour maximiser l'Alpha-Beta pruning
            possible_actions = state.get_possible_actions()
            ordered_actions = self.order_moves(possible_actions)
            # Exploration des actions possibles
            for action in ordered_actions:
                eval = self.minimax_with_alpha_beta(action.get_next_game_state(), depth - 1, alpha, beta, not maximizing_player)
                if maximizing_player:
                    score = max(score, eval)
                    alpha = max(alpha, eval)  # Mise à jour d'Alpha
                else:
                    score = min(score, eval)
                    beta = min(beta, eval)  # Mise à jour de Beta
                if beta <= alpha:
                    break  # Élagage Alpha-Beta

        self.transposition_table[state_key] = score  # Mise à jour de la table de transposition
        return score


    def generate_state_key(self, state: GameStateAbalone) -> int:
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
        key = hash(state)
        return key


    def evaluate(self, state: GameStateAbalone) -> int:
        # Note : l'heuristique peut encore encore être énormément améliorée, je l'ai faite un peu à la va vite, 
        #        je voulais surtout que le squelette soit fait pour l'algorithme MiniMax
        """
        Évalue un état donné du jeu Abalone et retourne un score basé sur le score, l'avantage de placement et la mobilité.

        Args:
            state: L'état du jeu à évaluer.

        Returns:
            Le score évalué de l'état pour le joueur.
        """
        # Avantage du score : différence entre le nombre de pièces du joueur et celui de l'adversaire
        material_score = state.scores[self.id] - state.scores[state.next_player.get_id()]

        # Avantage de placement : contrôle du centre du plateau
        grid = state.get_rep().get_env()
        center_positions = [(7, 3), (6, 4), (7, 5), (9, 5), (10, 4), (9, 3), (8, 4), (5,3), (4,4), (5,5), (6,6), (8,6), (10,6), (11,5)]
        center_pieces = sum(1 for pos in center_positions if grid.get(pos, None) and grid[pos].get_owner_id() == self.id)
        opponent_center_pieces = sum(1 for pos in center_positions if grid.get(pos, None) and grid[pos].get_owner_id() == state.next_player.get_id())
        positional_score = center_pieces - opponent_center_pieces

        # Mobilité : nombre d'actions possibles
        mobility_score = len(state.get_possible_actions())

        # Poids pour chaque composant du score
        material_weight = 10
        positional_weight = 5
        mobility_weight = 0

        # Score pondéré combiné
        score = (material_weight * material_score +
                positional_weight * positional_score +
                mobility_weight * mobility_score)

        return score