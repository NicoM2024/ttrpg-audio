import os
import csv
import urllib.parse
import urllib.request
import json
import unicodedata

OWNER = "NicoM2024"
REPO = "ttrpg-audio"
BRANCH = "raw/refs/heads/main"

# Access Github
def get_all_repo_files():
    api_url = f"https://api.github.com/repos/{OWNER}/{REPO}/git/trees/main?recursive=1"

    request = urllib.request.Request(
        api_url,
        headers={"User-Agent": "ttrpg-music-tool"}
    )

    response = urllib.request.urlopen(request)
    data = json.load(response)

    return data["tree"]

def construct(includes):
    
    # Get the files from github
    repo_files = get_all_repo_files()

    # Creates list of rows from the repo
    base_rows = []
    for item in repo_files:
        if item["type"] != "blob":
            continue
        
        file_path = item["path"]
        
        if not file_path.startswith("Music/"):
            continue
    
        if not file_path.lower().endswith((".mp3", ".wav", ".ogg")):
            continue
        
        parts = file_path.split("/")

        game = parts[1]
        if normalize_game_name(game) not in includes:
            continue

        title = os.path.splitext(parts[-1])[0]

        url = f"https://raw.githubusercontent.com/{OWNER}/{REPO}/main/{file_path}"

        tags = [game, "raw"]

        for part in parts:
            if part.lower() in get_music_types():
                tags.append(part.lower())

        tags_str = "|".join(tags)

        base_rows.append([title, url, tags_str])
    
    while True:
        try:
            downloads = os.path.join(os.path.expanduser("~"), "Downloads")
            print("What would you like to call the file?")
            print("Choosing an existing file will add missing files and NOT overwrite or delete changes.")
            file_name = input("\n").split(".")[0].strip()
            csv_path = os.path.join(downloads, f"{file_name}.csv")

            # Read existing CSV
            existing_rows = []

            if os.path.exists(csv_path):
                with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        existing_rows.append([row['title'], row['url'], row['tags']])

            # Track all seen titles
            existing_titles = set(row[0].strip() for row in existing_rows)

            # Only write the ones with titles not seen already
            rows_to_write = []
            for title, url, tags in base_rows:  # only iterate new scan rows
                if title.strip() not in existing_titles:
                    rows_to_write.append([title, url, tags])
                    existing_titles.add(title.strip())  # mark as seen immediately to avoid duplicates in this run

            # Combine
            all_rows = existing_rows + rows_to_write
            
            # Get list of original titles
            original_urls_titles = {}
            for title, url, tags in base_rows:
                original_urls_titles[url] = title
            
            # For each row, if it is not an original, replace its 'raw' tag with a 'custom' tag
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
            
            # Sort by raw/custom, game name, music type, and track title
            all_rows.sort(key=lambda row: (
                get_tag_safe(row[2], 1),                     # nature (raw, custom)
                get_tag_safe(row[2], 0).lower(),             # game name (first tag)
                get_tag_safe(row[2], 2).lower(),             # type (second tag)
                row[0].lower()                               # song title
            ))

            # Write to CSV
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

def normalize_game_name(text):
    # Normalize Unicode characters
    text = unicodedata.normalize("NFKD", text)
    
    # Remove accent marks
    text = "".join(c for c in text if not unicodedata.combining(c))
    
    # Lowercase + strip
    text = text.lower().strip()
    
    return text

def get_music_types():
    return ["ambient", "combat", "other"]

def lower_array(arr):
    return [item.lower() for item in arr]

def strip_array(arr):
    return [item.strip() for item in arr]
    
def parse_response(response):
    given_games = [normalize_game_name(g) for g in strip_array(lower_array(response.split(",")))]
    real_games = [normalize_game_name(n) for n in get_games()]
    
    valid = all(game in real_games for game in given_games)
            
    return valid, given_games
    
if __name__ == '__main__':
    user_input = get_input()
    construct(user_input)