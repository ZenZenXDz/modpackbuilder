import os
import requests
import zipfile
from tqdm import tqdm
import json
import re
import shutil

CONFIG_FILE = "config.json"

# API URLs
CURSEFORGE_API_URL = "https://api.curseforge.com/v1"
MODRINTH_API_URL = "https://api.modrinth.com/v2"

# Function to load or prompt for the API key
def get_api_key():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
            if "curseforge_api" in config:
                return config["curseforge_api"]
    
    print("🔑 Enter your CurseForge API Key (this will be saved for future use):")
    api_key = input(">>> ").strip()
    
    with open(CONFIG_FILE, "w") as f:
        json.dump({"curseforge_api": api_key}, f)
    
    return api_key

# Function to get CurseForge mod name
def get_curseforge_mod_name(mod_id):
    url = f"{CURSEFORGE_API_URL}/mods/{mod_id}"
    headers = {"x-api-key": CURSEFORGE_API_KEY}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return None
    return response.json()["data"]["name"]

# Function to get Modrinth mod name
def get_modrinth_mod_name(mod_id):
    url = f"{MODRINTH_API_URL}/project/{mod_id}"
    response = requests.get(url)
    if response.status_code != 200:
        return None
    return response.json()["title"]

CURSEFORGE_API_KEY = get_api_key()

# Ask user for modpack name
modpack_name = input("Enter your modpack name: ").strip()
modpack_name = re.sub(r'[<>:"/\\|?*]', "", modpack_name)

MODPACK_DIR = modpack_name
MODS_DIR = os.path.join(MODPACK_DIR, "mods")
os.makedirs(MODS_DIR, exist_ok=True)

# Validate Minecraft version
version_pattern = re.compile(r"^1\.\d+\.\d+$")
while True:
    mc_version = input("Enter Minecraft version (e.g., 1.21.1): ").strip()
    if version_pattern.match(mc_version):
        break
    print("❌ Invalid Minecraft version! Use the format '1.xx.x' (e.g., 1.21.1).")

# Validate modloader
while True:
    modloader = input("Enter modloader (Forge/NeoForge/Fabric/Mixed): ").strip().lower()
    if modloader in ["forge", "neoforge", "fabric", "mixed"]:
        break
    print("❌ Invalid modloader! Please enter 'Forge', 'NeoForge', 'Fabric', or 'Mixed'.")

# Function to clean file names
def sanitize_filename(name):
    return re.sub(r'[<>:"/\\|?*]', "", name)

# Detect mod source based on ID format (CurseForge = numbers, Modrinth = letters)
def detect_mod_source(mod_id):
    return "curseforge" if mod_id.isdigit() else "modrinth"

# Function to get CurseForge mod download URL with NeoForge prioritization
def get_curseforge_download_url(mod_id, mc_version, modloader):
    url = f"{CURSEFORGE_API_URL}/mods/{mod_id}/files"
    headers = {"x-api-key": CURSEFORGE_API_KEY}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return None, None
    files = response.json().get("data", [])

    # Initialize variables for different loader versions
    neoforge_match = None
    forge_match = None
    fabric_match = None

    for file in files:
        if mc_version in file["gameVersions"]:
            file_loaders = file["gameVersions"]
            
            # Check for each loader type
            if "NeoForge" in file_loaders:
                neoforge_match = (file["downloadUrl"], "NeoForge")
            elif "Forge" in file_loaders and not neoforge_match:
                forge_match = (file["downloadUrl"], "Forge")
            elif "Fabric" in file_loaders and not neoforge_match and not forge_match:
                fabric_match = (file["downloadUrl"], "Fabric")

    # Return the best match based on priority
    if modloader == "mixed":
        return neoforge_match or forge_match or fabric_match or (None, None)
    elif modloader == "neoforge":
        return neoforge_match or (None, None)
    elif modloader == "forge":
        return forge_match or (None, None)
    elif modloader == "fabric":
        return fabric_match or (None, None)

# Function to get Modrinth mod download URL with NeoForge prioritization
def get_modrinth_download_url(mod_id, mc_version, modloader):
    url = f"{MODRINTH_API_URL}/project/{mod_id}/version"
    response = requests.get(url)
    if response.status_code != 200:
        return None, None
    versions = response.json()

    # Initialize variables for different loader versions
    neoforge_match = None
    forge_match = None
    fabric_match = None

    for version in versions:
        if mc_version in version["game_versions"]:
            file_loaders = version["loaders"]
            
            # Check for each loader type
            if "neoforge" in file_loaders:
                neoforge_match = (version["files"][0]["url"], "NeoForge")
            elif "forge" in file_loaders and not neoforge_match:
                forge_match = (version["files"][0]["url"], "Forge")
            elif "fabric" in file_loaders and not neoforge_match and not forge_match:
                fabric_match = (version["files"][0]["url"], "Fabric")

    # Return the best match based on priority
    if modloader == "mixed":
        return neoforge_match or forge_match or fabric_match or (None, None)
    elif modloader == "neoforge":
        return neoforge_match or (None, None)
    elif modloader == "forge":
        return forge_match or (None, None)
    elif modloader == "fabric":
        return fabric_match or (None, None)

# Function to download mod files
def download_mod(url, save_path):
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get("content-length", 0))
    with open(save_path, "wb") as file, tqdm(
        desc=os.path.basename(save_path),
        total=total_size,
        unit="B",
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for chunk in response.iter_content(chunk_size=1024):
            file.write(chunk)
            bar.update(len(chunk))

# Loop to continuously ask for mod project IDs
while True:
    mod_id = input("Enter mod project ID (or type 'done' to finish): ").strip()
    if mod_id.lower() == "done":
        break

    mod_source = detect_mod_source(mod_id)

    if mod_source == "curseforge":
        mod_name = get_curseforge_mod_name(mod_id)
        download_url, used_loader = get_curseforge_download_url(mod_id, mc_version, modloader)
    else:
        mod_name = get_modrinth_mod_name(mod_id)
        download_url, used_loader = get_modrinth_download_url(mod_id, mc_version, modloader)

    if not mod_name or not download_url:
        print(f"❌ Failed to get mod information for ID {mod_id}. Skipping...")
        continue

    sanitized_mod_name = sanitize_filename(mod_name)
    formatted_name = f"[{used_loader}] {sanitized_mod_name}.jar"
    save_path = os.path.join(MODS_DIR, formatted_name)

    print(f"⬇ Downloading {mod_name}...")
    download_mod(download_url, save_path)
    print(f"✅ Downloaded: {formatted_name}")

# Create a ZIP of the modpack
modpack_zip = f"{modpack_name}.zip"
def create_modpack_zip(output_filename):
    with zipfile.ZipFile(output_filename, "w", zipfile.ZIP_DEFLATED) as modpack_zip:
        for foldername, subfolders, filenames in os.walk(MODPACK_DIR):
            for filename in filenames:
                file_path = os.path.join(foldername, filename)
                modpack_zip.write(file_path, os.path.relpath(file_path, MODPACK_DIR))

create_modpack_zip(modpack_zip)
print(f"✅ Modpack compiled into {modpack_zip}")

# Remove the temporary folder after zipping
shutil.rmtree(MODPACK_DIR)
print(f"🗑️ Deleted temporary folder: {MODPACK_DIR}")