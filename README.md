# 🎮 Modpack Builder

A powerful and intuitive Python script for creating Minecraft modpacks from CurseForge and Modrinth mods. Modpack Builder automatically handles mod downloads, loader compatibility, and modpack compilation with intelligent mod loader prioritization.

## ✨ Features

- **Multi-Platform Support**: Download mods from both CurseForge and Modrinth
- **Smart Loader Detection**: Automatically detects and prioritizes mod loaders in the following order:
  1. NeoForge (Primary)
  2. Forge (Secondary)
  3. Fabric (Fallback)
- **Flexible Loader Options**: Support for NeoForge, Forge, Fabric, or Mixed loader configurations
- **Intelligent Naming**: Automatically formats mod files with loader information: `[LoaderType] ModName.jar`
- **Progress Tracking**: Visual download progress bars for each mod
- **Automatic Compilation**: Creates a ready-to-use modpack ZIP file
- **Error Handling**: Robust error checking and user-friendly messages

## 🚀 Getting Started

### Prerequisites

```bash
pip install requests tqdm
```

### Configuration

You'll need a CurseForge API key to use this script. You can obtain one from the [CurseForge API Portal](https://docs.curseforge.com/#getting-started).

### Usage

1. Run the script:
   ```bash
   python modpackforge.py
   ```

2. Follow the prompts:
   - Enter your CurseForge API key (saved for future use)
   - Specify your modpack name
   - Enter Minecraft version (e.g., 1.21.1)
   - Choose modloader (Forge/NeoForge/Fabric/Mixed)
   - Input mod IDs from either CurseForge or Modrinth
   - Type 'done' when finished

3. The script will:
   - Download all mods with appropriate loader versions
   - Name files consistently with loader information
   - Create a ZIP file containing your modpack
   - Clean up temporary files automatically

## 🔍 Mod Loader Priority

When using the "Mixed" loader option or searching for mods, ModpackForge follows this priority:

1. **NeoForge**: Always preferred if available
2. **Forge**: Used if NeoForge version isn't available
3. **Fabric**: Used as a last resort if neither NeoForge nor Forge versions exist

## 📁 Output Structure

```
YourModpack.zip
└── mods/
    ├── [NeoForge] Mod1.jar
    ├── [Forge] Mod2.jar
    └── [Fabric] Mod3.jar
```

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest enhancements
- Submit pull requests
- Improve documentation

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- CurseForge API for mod information and downloads
- Modrinth API for additional mod support
- Python community for excellent libraries
- Minecraft modding community

## ⚠️ Disclaimer

This tool is not affiliated with CurseForge, Modrinth, or Mojang. All mods downloaded using this tool are subject to their respective licenses and terms of use.
