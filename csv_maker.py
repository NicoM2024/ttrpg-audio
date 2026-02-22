import os
import csv
import urllib.parse

OWNER = "NicoM2024"
REPO = "ttrpg-audio"
BRANCH = "raw/refs/heads/main"

def construct(includes):
    
    rows = [["title", "url", "tags"]]
    for game in os.listdir("Music"):
        if not game.lower() in includes:
            continue
        
        # Tag it with origin game
        for root, dirs, files in os.walk(f"Music/{game}"):
            
            # Tag it with type
            music_type_tag = os.path.basename(root).lower() if os.path.basename(root).lower() in get_music_types() else ""
            
            for file in files:
                
                if not file.lower().endswith((".mp3", ".wav", ".ogg")):
                    continue
                
                file_path = os.path.relpath(os.path.join(root, file), ".").replace("\\", "/")
                file_path = urllib.parse.quote(file_path)
                # Init info
                title = os.path.splitext(file)[0]
                url = f"https://github.com/{OWNER}/{REPO}/{BRANCH}/{file_path}"
                tags = f"{game}|{music_type_tag}"
                
                rows.append([title, url, tags])
    
    while True:
        try:
            # Write to file
            file_name = input("What would you like to call the file?\n").split(".")[0].strip()
            downloads = os.path.join(os.path.expanduser("~"), "Downloads")
            csv_path = os.path.join(downloads, f"{file_name}.csv")
            
             # Remove if it exists
            if os.path.exists(csv_path):
                os.remove(csv_path)
            
            with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerows(rows)
                
            break
        
        except PermissionError:
            print("\n!ERROR!\nCouldn't modify the file because it is in use by another process.")
            print("Try closing the file and trying again.")
            return
    
    print("Success!")

def get_input():
    while True:
        print("Please enter the names of the games' music you would like to include seperated by commas.")
        print("For information on the available games, enter 'HELP'. For all games, enter 'ALL'")
        
        response = input("\n")
        if response.lower() == 'help':
            print_games(get_games())
            continue
    
        if response.lower() == 'all':
            return lower_array(get_games())
        
        includes = parse_response(response)
        if not includes[0]:
            print("The list of games you gave was invalid.")
            print("Make sure the names are correct, and they are seperated by commas with no spacing in between names\n")
            continue
    
        return includes[1]
            
    
def print_games(games):
    print("\nHere are the game choices:")
    for game in games:
        print(f" - {game}")
    print()

def get_games():
    to_return = []
    
    for item in os.listdir("Music"):
        to_return.append(item)

    return to_return

def get_music_types():
    return ["ambient", "combat", "other"]

def lower_array(arr):
    return [item.lower() for item in arr]

def strip_array(arr):
    return [item.strip() for item in arr]
    
def parse_response(response):
    given_games = strip_array(lower_array(response.split(",")))
    real_games = lower_array(get_games())
    
    valid = all(game in real_games for game in given_games)
            
    return valid, given_games
    
if __name__ == '__main__':
    includes = get_input()
    construct(includes)