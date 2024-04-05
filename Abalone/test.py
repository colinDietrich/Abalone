import subprocess
import os
import json
import shutil

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


# play with this
nbr_of_games = 100
turn = 0 # 0 if first (player1), 1 if second (player 2)
command = "python main_abalone.py -t local my_player.py greedy_player_abalone.py -c alien -r -g"

# simulate n games with command line
for i in range(nbr_of_games):
    output, error = run_command(command)
    #if error:
        #print("Error:", error)

# analyse json files for result and store them
games = open_json_files_in_folder()
won = 0
lost = 0
none = 0
for game in games:
    last_turn = game[-1]
    #get player id
    player_1_id = last_turn["players"][0]["id"]
    player_2_id = last_turn["players"][1]["id"]
    #get scores with id
    score_1 = last_turn["scores"][str(player_1_id)]
    score_2 = last_turn["scores"][str(player_2_id)]
    if score_1>score_2:
        won +=1
    elif score_1<score_2:
        lost +=1
    else:
        none +=1
        
#print stats
pure_win_per = won/len(games)
pure_loss_per = lost/len(games)
none_perc = none/len(games)

print("STATS :")
print("Pure win percerntage : "+ str(pure_win_per), " Games won : " + str(won)+"/"+str(len(games)))
print("Pure loss percerntage : "+ str(pure_loss_per), " Games lost : " + str(lost)+"/"+str(len(games)))
print("Equalities: "+ str(none) +" (real winner is the one closer to the center)")






