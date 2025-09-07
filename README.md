# **Craft.do to Obsidian Migrator**

A robust, interactive Python script to migrate your notes from Craft to Obsidian, preserving links, attachments, and metadata with high fidelity.

This tool was born from a real-world migration and is designed to handle the complex edge cases that other converters miss. It uses a powerful two-pass system to map your entire vault *before* conversion, ensuring every internal link is preserved perfectly.

### **Key Features**

* ✅ **Interactive & User-Friendly**: No complex command-line flags. The script asks simple yes/no questions to configure the entire process.  
* 🔗 **Perfect Link Conversion**: Accurately converts all internal Craft links (craftdocs://) into Obsidian \[\[wikilinks\]\], correctly creating aliases (\[\[Note Title|Different Display Text\]\]) by mapping Craft's internal note IDs.  
* 🗂️ **Preserves All Metadata**: Keeps original creation/modification dates, uses the title for daily notes, and intelligently consolidates \#tags into Obsidian's frontmatter.  
* 🖼️ **Organized Attachments**: Moves all images and files into per-note subfolders, prevents duplicate filenames, and updates links to the new structure.  
* ✨ **Intelligent Cleanup & Polishing**:  
  * Optionally removes broken image links from web clippings.  
  * Optionally deletes empty notes.  
  * Automatically standardizes daily note titles (e.g., 2025.09.07 \-\> 2025-09-07) for compatibility with the Calendar plugin.  
  * Renames untitled notes based on their content.  
* 🛡️ **Safe & Reliable**: Warns before overwriting an existing vault and creates a detailed craft\_migration.log file for review.

### **Who is this for?**

This tool is for any Craft user who wants a reliable way to move their notes into Obsidian without losing the rich structure and metadata they've built. Its interactive setup makes powerful migration features accessible to everyone.

## **How to Use**

### **Prerequisites**

This script requires Python 3\. If you don't have it, download it from https://www.python.org/downloads/.  
Important for Windows users: On the first screen of the Python installer, check the box at the bottom that says "Add Python to PATH".

### **Step 1: Setup Your Folders**

1. Create a main folder on your computer (e.g., craft-migration).  
2. Place the **craft\_to\_obsidian\_migrator.py** script inside this folder.  
3. Inside craft-migration, create a new folder named input.  
4. Unzip your Craft export. Find the main folder containing all your notes (e.g., **Craft Export**) and move it inside the input folder.

Your final structure should look like this:

craft-migration/  
├── craft\_to\_obsidian\_migrator.py  
└── input/  
    └── Craft Export/  
        └── ... (all your notes, folders, and .textbundle files)

### **Step 2: Run the Script**

The process is slightly different for Windows vs. Mac/Linux.

#### **For Windows Users**

1. Open **File Explorer** and navigate into your craft-migration folder.  
2. Click in the address bar at the top of the window. The current path will be highlighted.  
3. Type cmd directly into the address bar and press **Enter**.  
4. A Command Prompt window will open. Copy and paste the following command and press **Enter**:  
   python craft\_to\_obsidian\_migrator.py "./input/Craft Export"

#### **For Mac & Linux Users**

1. Open the **Terminal** application.  
2. Navigate to your craft-migration folder using the cd command. For example, if it's in your Downloads folder:  
   cd \~/Downloads/craft-migration

3. Now, run the script. Copy and paste the following command and press **Enter**:  
   python3 craft\_to\_obsidian\_migrator.py "./input/Craft Export"

*(Note: Mac/Linux often use python3 instead of python)*

### **Step 3: Answer the Questions**

The script is interactive. It will now ask you a series of simple y/n questions. Type y for yes or n for no and press **Enter** after each one.

* This will completely overwrite the output directory. Continue? (y/n):  
* Add a 'source/craft' tag to all imported notes? (y/n):  
* Clean up links to images that are missing from the export? (y/n):  
* Delete notes that are empty after conversion? (y/n):

### **Step 4: Check Your New Vault\!**

Once you've answered, the script will run through the conversion process. When it's finished, a new folder named **obsidian-vault** will be created inside your craft-migration folder. This is your new, ready-to-use Obsidian vault\!

## **Limitations**

While this script is robust, there are a few limitations to be aware of:

* **Craft-Specific Blocks**: Content that relies on special Craft features (like styled cards, synced blocks, or complex table formatting) may not render perfectly in Obsidian's standard Markdown. The text will be preserved, but the styling will be lost.  
* **"Ghost" Assets**: If you used Craft's web clipper, some pages might contain links to images that Craft never actually saved in the export. These will appear as broken links in Obsidian. Running the script with the "Clean up links" option is the best way to handle this.  
* **Embedded Files**: The script migrates attached files (like PDFs), but it does not convert their *content* into Markdown. You will have a working link to the PDF file in your Obsidian vault.  
* **Encrypted Notes**: The script cannot process encrypted or password-protected notes from Craft.

## **License**

This project is licensed under the **Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License**. See the LICENSE.md file for details. This means you are free to share and adapt the work for non-commercial purposes, as long as you give appropriate credit and distribute your contributions under the same license.
