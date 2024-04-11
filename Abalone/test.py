import subprocess
import os
import json
import shutil
import pickle

# Chargement du dictionnaire s'il n'a pas encore été chargé.
with open('src_2226611_2225992/abalone_distances.pkl', 'rb') as f:
    all_distances = pickle.load(f)

def run_command(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, error = process.communicate()
    return output.decode("utf-8"), error.decode("utf-8")

def open_json_files_in_folder():
    all_files = []
    current_directory = os.getcwd()
    json_files = [f for f in os.listdir(current_directory) if f.endswith('.json')]
    if not json_files:
        print("No JSON files found in the current directory.")
        return
    
    # Create a subfolder for processed JSON files
    processed_folder = os.path.join(current_directory, "processed")
    os.makedirs(processed_folder, exist_ok=True)
    
    for json_file in json_files:
        with open(json_file, 'r') as file:
            json_content = json.load(file)
            all_files.append(json_content)
            
        # Move the processed JSON file to the subfolder
        destination_path = os.path.join(processed_folder, json_file)
        shutil.move(json_file, destination_path)
    return all_files

def distance_to_center(player_pieces):
    """
    Calcule la distance totale des pièces du joueur par rapport au centre.

    Args:
        player_pieces (list): Liste des coordonnées des pièces du joueur.

    Returns:
        float: Distance normalisée par rapport au centre.
    """
    central_position = (8, 4)
    length_to_center = sum(all_distances[(coord, central_position)] if coord != central_position else 0 for coord in player_pieces)
    max_distance = 4 * len(player_pieces)
    return length_to_center

def get_players_pieces(last_turn):
    player_1_pieces = []
    player_2_pieces = []
    board = last_turn["rep"]["env"]
    for coord in board:
        if board[coord]["piece_type"] == 'W':
            player_1_pieces.append(eval(coord))
        elif board[coord]["piece_type"] == 'B':
            player_2_pieces.append(eval(coord))
    return player_1_pieces, player_2_pieces


# play with this
nbr_of_games = 25
command = "python main_abalone.py -t local random_player_abalone.py my_player.py -c alien -r -g"
turn = 1 # 0 if first (player1), 1 if second (player 2)

# simulate n games with command line
for i in range(nbr_of_games):
    output, error = run_command(command)
    print(i)
    #if error:
        #print("Error:", error)

# analyse json files for result and store them
games = open_json_files_in_folder()
won = 0
lost = 0
score_equal = 0
closer = 0
for game in games:
    last_turn = game[-1]
    #get player id
    player_1_id = last_turn["players"][0]["id"]
    player_2_id = last_turn["players"][1]["id"]
    #get scores with id
    score_1 = last_turn["scores"][str(player_1_id)]
    score_2 = last_turn["scores"][str(player_2_id)]
    if score_1>score_2:
        if turn==0:
            won +=1
        elif turn==1:
            lost +=1
    elif score_1<score_2:
        if turn==0:
            lost +=1
        elif turn==1:
            won +=1
    else:
        score_equal +=1
        pieces1, pieces2 = get_players_pieces(last_turn)
        if distance_to_center(pieces1)<distance_to_center(pieces2):
            if turn==0:
                closer +=1 
        else:
            if turn==1:
                closer +=1
        
#print stats
pure_win_per = won/len(games)
win_per = (won+closer)/len(games)
pure_loss_per = lost/len(games)
loss_per = (lost+(score_equal-closer))
if score_equal != 0:
    closer_perc = closer/score_equal


print("STATS :")
print("Pure win percerntage : "+ str(pure_win_per), " Games won : " + str(won)+"/"+str(len(games)))
print("Pure loss percerntage : "+ str(pure_loss_per), " Games lost : " + str(lost)+"/"+str(len(games)))
print("Equalities: "+ str(score_equal) + ", " + str(closer)+"/" +str(score_equal)+ " won by being closer")






