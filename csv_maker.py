import os
import csv
import urllib.parse

OWNER = "NicoM2024"
REPO = "ttrpg-audio"
BRANCH = "raw/refs/heads/main"

def construct(includes):
    
    rows = []
    for game in os.listdir("Music"):
        if not game.lower() in includes:
            continue
        
        # Tag it with origin game
        for root, dirs, files in os.walk(f"Music/{game}"):
            for file in files:
                if not file.lower().endswith((".mp3", ".wav", ".ogg")):
                    continue
                # Path
                file_path = os.path.relpath(os.path.join(root, file), ".").replace("\\", "/")
                file_path = urllib.parse.quote(file_path)
                
                # Title
                title = os.path.splitext(file)[0]
                
                # URL
                url = f"https://github.com/{OWNER}/{REPO}/{BRANCH}/{file_path}"
                
                # Tags
                tags = [game, "raw"]
                
                # Look at all folders in the path to see if any are music types
                rel_path_from_game = os.path.relpath(root, f"Music/{game}").replace("\\", "/")
                if rel_path_from_game != ".":  # skip the game root folder itself
                    parts = rel_path_from_game.split("/")
                    for part in parts:
                        if part.lower() in get_music_types():
                            tags.append(part.lower())
                
                tags_str = "|".join(tags)
                
                rows.append([title, url, tags_str])
    
    while True:
        try:
            # Write to file
            downloads = os.path.join(os.path.expanduser("~"), "Downloads")
            file_name = input("What would you like to call the file?\n").split(".")[0].strip()
            csv_path = os.path.join(downloads, f"{file_name}.csv")

            # Read existing CSV
            existing_rows = []
            existing_urls_titles = {}  # url -> title
            
            if os.path.exists(csv_path):
                with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        existing_rows.append([row['title'], row['url'], row['tags']])
                        existing_urls_titles[row['url']] = row['title']
            
            original_urls_titles = {}
            for title, url, tags in rows:
                original_urls_titles[url] = title

            # Merge rows
            rows_to_write = []
            for row in rows:  # row = [title, url, tags]
                title, url, tags = row
                if not url in existing_urls_titles or title != existing_urls_titles[url]:
                    rows_to_write.append([title, url, tags])

            # Combine with existing rows
            all_rows = existing_rows + rows_to_write
            
            for i in range(len(all_rows)):
                title, url, tags = all_rows[i]
                if url in original_urls_titles and title != original_urls_titles[url]:
                    tag_list = tags.split("|")
                    if "custom" not in tag_list:
                        if "raw" in tag_list:
                            tag_list.remove("raw")
                        tag_list.insert(1, "custom")
                    new_tags_str = "|".join(tag_list)
                    all_rows[i][2] = new_tags_str
            
            all_rows.sort(key=lambda row: (
                get_tag_safe(row[2], 1),                     # nature (raw, custom)
                get_tag_safe(row[2], 0).lower(),             # game name (first tag)
                get_tag_safe(row[2], 2).lower(),             # type (second tag)
                row[0].lower()                               # song title
            ))

            # Write CSV
            with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(['title', 'url', 'tags'])
                writer.writerows(all_rows)
                
            print(f"CSV updated at {csv_path}")
            break
        
        except PermissionError:
            print("\n!ERROR!\nCouldn't modify the file because it is in use by another process.")
            print("Try closing the file and trying again.")
            return
    
def get_tag_safe(tag_str, i):
    if not tag_str:
        return ""
    tags = [t.strip() for t in tag_str.split("|")]
    if i < 0 or i >= len(tags):
        return ""
    return tags[i]

def get_input():
    while True:
        print("Please enter the names of the games' music you would like to include seperated by commas.")
        print("For information on the available games, enter 'HELP'. For all games, enter 'ALL'")
        
        response = input("\n").strip()
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
    i = get_input()
    construct(i)