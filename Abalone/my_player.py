from player_abalone import PlayerAbalone
from game_state_abalone import GameStateAbalone
from seahorse.game.action import Action
from seahorse.game.game_state import GameState
from seahorse.utils.custom_exceptions import MethodNotImplementedError
import time
import pickle

class MyPlayer(PlayerAbalone):
    """
    Classe de joueur pour le jeu Abalone.

    Attributs :
        piece_type (str): Type de pièce du joueur.
    """

    # Variable de classe pour stocker le dictionnaire qui contient toutes les distances entre 2 cases.
    all_distances = None

    def __init__(self, piece_type: str, name: str = "bob", time_limit: float = 60*15, *args) -> None:
        """
        Initialise une instance de PlayerAbalone.

        Args:
            piece_type (str): Type de pièce du joueur.
            name (str, optionnel): Nom du joueur (par défaut "bob").
            time_limit (float, optionnel): Limite de temps en secondes.
        """
        super().__init__(piece_type, name, time_limit, *args)
        self.max_time = time_limit
        self.turn = 0
        # Chargement du dictionnaire s'il n'a pas encore été chargé.
        if MyPlayer.all_distances is None:
            with open('src/abalone_distances.pkl', 'rb') as f:
                MyPlayer.all_distances = pickle.load(f)

    def compute_action(self, current_state: GameStateAbalone, **kwargs) -> Action:
        """
        Implémente la logique du joueur pour calculer l'action à effectuer.

        Args:
            current_state (GameStateAbalone): État actuel du jeu.
            **kwargs: Arguments supplémentaires sous forme de mots-clés.

        Returns:
            Action: Action sélectionnée par le joueur.
        """
        # measure time of the action
        possible_actions = list(current_state.get_possible_actions())
        self.other_id = possible_actions[0].get_next_game_state().next_player.get_id()
        depth = self.adjust_depth()  # Ajustement dynamique de la profondeur de l'algorithme MiniMax.
        action, score = self.miniMax(current_state, depth, alpha=float('-inf'), beta=float('inf'), maximizing=True)
        # measure time and nbr of turns played
        self.turn += 1
        return action

    def adjust_depth(self):
        """
        Ajuste la profondeur de l'algorithme MiniMax en fonction de l'état actuel du jeu.

        Args:
            current_state (GameStateAbalone): État actuel du jeu.

        Returns:
            int: Profondeur ajustée pour l'algorithme MiniMax.
        """
        turn_left = 25 - self.turn
        # Début du jeu : Profondeur plus faible (Le jeu commence avec 14 pièces).
        if turn_left > 10:  
            return 3
        else:
            if(self.get_remaining_time() - turn_left * 60 > 0):
                return 4
            else:
                return 3

    def miniMax(self, state: GameStateAbalone, depth: int, alpha, beta, maximizing: bool):
        """
        Algorithme MiniMax avec élagage alpha-bêta pour déterminer la meilleure action.

        Args:
            state (GameStateAbalone): État actuel du jeu.
            depth (int): Profondeur de recherche à partir de cet état.
            alpha (float): Valeur alpha pour alpha-beta pruning.
            beta (float): Valeur bêta pour alpha-beta pruning.
            maximizing (bool): Indique si le joueur actuel maximise ou minimise.

        Returns:
            Tuple[Action, int]: Meilleure action et son score correspondant.
        """
        if depth == 0 or state.is_done():
            return None, self.evaluate_state(state)
        
        # joueur maximisant
        if maximizing:
            max_score = float('-inf')
            best_action = None
            for action in state.get_possible_actions():
                _, score = self.miniMax(action.get_next_game_state(), depth-1, alpha, beta, False)
                if score > max_score:
                    best_action, max_score = action, score
                alpha = max(alpha, score)
                if beta <= alpha:
                    break
            return best_action, max_score
        
        # joueur minimisant
        else:
            min_score = float('inf')
            best_action = None
            for action in state.get_possible_actions():
                _, score = self.miniMax(action.get_next_game_state(), depth-1, alpha, beta, True)
                if score < min_score:
                    best_action, min_score = action, score
                beta = min(beta, score)
                if beta <= alpha:
                    break
            return best_action, min_score

    def evaluate_state(self, state:GameStateAbalone, debug=False):
        """
        Évalue l'état actuel du jeu pour déterminer son avantage pour le joueur.

        Stratégies :
            1. Dominance Centrale : Prioriser le contrôle du centre pour la sécurité et la mobilité. Les pièces centrales ont plus de pression.
            2. Diviser pour Régner : Fragmenter les pièces de l'adversaire pour les manipuler plus facilement et les pousser hors du plateau.
            3. Technique du Blob : Regrouper les pièces en une formation compacte pour résister aux poussées. Cela force l'adversaire à disperser ses pièces, les rendant vulnérables.
            4. Aggression Progressive : Commencer de manière conservatrice en se concentrant sur le contrôle du centre. À mesure que le contrôle est établi, adopter une stratégie plus agressive pour éjecter les billes de l'adversaire.
        """
        # Calcul de l'évaluation
        ball_score = state.scores[self.id] - state.scores[self.other_id]
        player_pieces, other_player_pieces, empty_spaces = self.get_pieces(state)
        central_score = self.distance_to_center(player_pieces)
        connectedness_score = self.degree_of_connectedness(player_pieces)
        connectedness_score_other_player = self.degree_of_connectedness(other_player_pieces)

        if debug:
            print("Ball Score:", ball_score)
            print("Central Score:", central_score)
            print("Connectedness Score:", connectedness_score)
            print("Connectedness Score (Other Player):", connectedness_score_other_player)
            print("remaining time:",self.get_remaining_time())

        # Détermination de la phase de jeu
        ejected_pieces = 14 - len(other_player_pieces) # Nombre de pièces éjectées de l'adversaire
        
        score_pieces = len(player_pieces) / 14

        # Phase 1 : Dominance Centrale
        if central_score > 0.5:
            if debug:
                print("Phase 1: Dominance Centrale")
            a, b, c, d = 2, 1, 0.1, 0.01  # Poids initiaux
                
        # Phase 2 : Groupe Compact + Dominance Centrale
        elif connectedness_score < 0.5:
            if debug:
                print("Phase 2 : Groupe Compact + Dominance Centrale")
            a, b, c, d = 2, 1, 1, 0.01  # Poids ajustés pour la compacité et le contrôle central
            
        # Phase 3 : Jeu Agressif
        else:
            if debug:
                print("Phase 3 : Jeu Agressif")
            a, b, c, d = 3, 1, 1, 0.5  # Changement de focus vers un jeu plus agressif
            if ejected_pieces >= 3:  # Aggression accrue après l'éjection de 5 pièces
                a, c = 3, 1  # Augmentation des poids pour l'agression

        score = a * ball_score - b * central_score + c * connectedness_score - d * connectedness_score_other_player + 10 * score_pieces
        return score

    def get_pieces(self, state:GameStateAbalone):
        """
        Récupère les pièces des joueurs et les espaces vides à partir de l'état actuel du jeu.

        Args:
            state (GameStateAbalone): État actuel du jeu.

        Returns:
            tuple: Listes des pièces du joueur, des pièces de l'adversaire et des espaces vides.
        """
        grid = state.get_rep().get_env()
        player_pieces = []
        other_player_pieces = []
        empty_spaces = []
        for coord in grid:
            if grid[coord].get_owner_id() == self.id:
                player_pieces.append(coord)
            elif grid[coord].get_owner_id() == self.other_id:
                other_player_pieces.append(coord)
            else:
                empty_spaces.append(coord)
        return player_pieces, other_player_pieces, empty_spaces

    def distance_to_center(self, player_pieces):
        """
        Calcule la distance totale des pièces du joueur par rapport au centre.

        Args:
            player_pieces (list): Liste des coordonnées des pièces du joueur.

        Returns:
            float: Distance normalisée par rapport au centre.
        """
        central_position = (8, 4)
        length_to_center = sum(self.all_distances[(coord, central_position)] if coord != central_position else 0 for coord in player_pieces)
        max_distance = 4 * len(player_pieces)
        return length_to_center / max_distance

    def degree_of_connectedness(self, piece_coordinates):
        """
        Calcule le degré de connectivité des pièces du joueur en fonction de la distance de Manhattan entre elles.

        Args:
            piece_coordinates (list of tuples): Liste des coordonnées (x, y) des pièces du joueur.

        Returns:
            float: Degré de connectivité, variant de 0 à 1.
        """
        total_distance = 0
        total_possible_distance = len(piece_coordinates) * (len(piece_coordinates) - 1) / 2  # Combinaisons possibles

        for i in range(len(piece_coordinates)):
            for j in range(i + 1, len(piece_coordinates)):
                distance = self.all_distances[(piece_coordinates[i], piece_coordinates[j])]
                total_distance += distance

        # Calcul du degré de connectivité comme l'inverse de la distance moyenne normalisée
        if total_possible_distance > 0:
            return 1 - (total_distance / (total_possible_distance * 6))  # Normalisation de la distance à l'intervalle [0, 1]
        else:
            return 0
