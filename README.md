Craft.do to Obsidian Migrator
A robust, interactive Python script to migrate your notes from Craft to Obsidian, preserving links, attachments, and metadata with high fidelity.

This tool was born from a real-world migration and is designed to handle the complex edge cases that other converters miss. It uses a powerful two-pass system to map your entire vault before conversion, ensuring every internal link is preserved perfectly.

Key Features
✅ Interactive & User-Friendly: No complex command-line flags to remember. The script asks you simple yes/no questions to configure the entire process.

🔗 Perfect Link Conversion: Accurately converts all internal Craft links (craftdocs://) into Obsidian [[wikilinks]], correctly creating aliases ([[Note Title|Different Display Text]]) when needed by mapping Craft's internal note IDs.

🗂️ Preserves All Metadata: Keeps your original creation/modification dates, correctly uses the title for daily notes, and intelligently consolidates #tags into Obsidian's frontmatter.

🖼️ Organized Attachments: Moves all images and files into per-note subfolders, prevents duplicate filenames, and updates all links to the new, clean structure.

✨ Intelligent Cleanup & Polishing:

Optionally finds and removes broken image links from web clippings.

Optionally deletes empty notes.

Automatically standardizes daily note titles (e.g., 2025.09.07 -> 2025-09-07) for compatibility with the Calendar plugin.

Renames untitled notes based on their content.

🛡️ Safe & Reliable: Warns before overwriting an existing vault, prevents data loss from duplicate files, and creates a detailed craft_migration.log file for easy review.

Who is this for?
This tool is for any Craft user who wants a reliable and thorough way to move their notes into Obsidian without losing the rich structure and metadata they've built. Its interactive setup makes powerful migration features accessible to everyone, regardless of technical skill.

How to Use
1. Setup Your Folders
Create a main folder on your computer (e.g., craft-migration).

Place the craft_to_obsidian_migrator.py script inside this folder.

Inside craft-migration, create an input folder.

Unzip your Craft export and place the main content folder (e.g., Craft Export) inside the input folder.

Your final structure should look like this:

craft-migration/
├── craft_to_obsidian_migrator.py
└── input/
    └── Craft Export/
        └── ... (all your notes, folders, and .textbundle files)

2. Run the Script
Open your terminal or command prompt (like Terminal on Mac, or Command Prompt/PowerShell on Windows).

Navigate to your main craft-migration folder.

# Example for Windows
cd C:\Users\YourUser\Downloads\craft-migration

# Example for Mac/Linux
cd ~/Downloads/craft-migration

Run the script with one simple command, pointing it to your export folder:

python craft_to_obsidian_migrator.py "./input/Craft Export"

(Using quotes around the path is a good habit to handle any spaces in folder names.)

3. Answer the Questions
The script will then ask you a series of simple y/n questions to tailor the conversion to your exact needs.

This will completely overwrite the output directory. Continue? (y/n):

Add a 'source/craft' tag to all imported notes? (y/n):

Clean up links to images that are missing from the export? (y/n):

Delete notes that are empty after conversion? (y/n):

Once you've answered, the script will take care of the rest, building you a perfect Obsidian vault in a folder named obsidian-vault.

License

This project is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License. See the LICENSE.md file for details. This means you are free to share and adapt the work for non-commercial purposes, as long as you give appropriate credit and distribute your contributions under the same license.
