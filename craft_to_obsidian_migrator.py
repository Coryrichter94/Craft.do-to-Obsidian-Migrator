# The Definitive Craft to Obsidian Migrator (Interactive Edition)
#
# A robust, interactive tool for a high-fidelity Craft.do to Obsidian migration.
# This script is the result of a collaboration with Cory Richter.
#
# Licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License.
# See the LICENSE.md file for details.
# Copyright (c) 2025 Cory Richter

import os
import re
import shutil
import argparse
import sys
import logging
import json
from datetime import datetime
from urllib.parse import unquote
from pathlib import Path
from typing import Tuple, List, Optional

# --- Constants ---
DEFAULT_NOTE_TITLE = "Untitled"
ATTACHMENTS_DIR = "attachments"
CRAFT_TAG = "source/craft"

# --- Setup Logging ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("craft_migration.log", mode='w'),
        logging.StreamHandler(sys.stdout)
    ]
)

# --- Globals ---
found_assets = set()
uuid_to_filename_map = {}

def sanitize_filename(filename: str, max_length: int = 200) -> str:
    """Removes invalid characters from a filename, trims whitespace, and handles edge cases."""
    if not filename: return DEFAULT_NOTE_TITLE
    sanitized = re.sub(r'[\\/*?:"<>|]', "", filename).strip()[:max_length]
    return sanitized if sanitized else DEFAULT_NOTE_TITLE

def build_uuid_map(input_dir: str) -> None:
    """Pass 1: Walk through all .textbundle files to map identifier to sanitized filename."""
    logging.info("--- Pass 1: Building UUID to Filename Map ---")
    input_path = Path(input_dir)
    for root, dirs, _ in os.walk(input_path):
        for dir_name in dirs:
            if dir_name.lower().endswith('.textbundle'):
                info_path = Path(root) / dir_name / 'info.json'
                try:
                    with open(info_path, 'r', encoding='utf-8') as f: data = json.load(f)
                    block_id = data.get('identifier')
                    note_title = sanitize_filename(dir_name.replace('.textbundle', ''))
                    if block_id and note_title: uuid_to_filename_map[block_id] = note_title
                except (FileNotFoundError, json.JSONDecodeError, KeyError):
                    logging.warning(f"Could not process info.json for {dir_name}")
    logging.info(f"Finished Pass 1: Mapped {len(uuid_to_filename_map)} unique note IDs.")

def get_metadata(bundle_path: Path) -> Tuple[Optional[str], Optional[str]]:
    """Reads creation and modification dates from info.json."""
    info_path = bundle_path / 'info.json'
    try:
        with open(info_path, 'r', encoding='utf-8') as f: data = json.load(f)
        creation_timestamp = data.get('creationDate')
        modification_timestamp = data.get('modificationDate')
        if creation_timestamp is None:
            creation_date = None
        else:
            creation_date = datetime.fromtimestamp(float(creation_timestamp)).strftime('%Y-%m-%d')
        if modification_timestamp is None:
            modification_date = None
        else:
            modification_date = datetime.fromtimestamp(float(modification_timestamp)).strftime('%Y-%m-%d')
        return creation_date, modification_date
    except (FileNotFoundError, json.JSONDecodeError, KeyError, ValueError, TypeError):
        logging.warning(f"Could not find a valid timestamp in {info_path}. Date properties will be omitted.")
        return None, None

def create_frontmatter(tags: List[str], creation_date: Optional[str], modification_date: Optional[str], add_craft_tag: bool) -> str:
    """Creates a YAML frontmatter block, correctly combining existing and optional new tags."""
    lines = ["---"]
    if creation_date: lines.append(f"creation_date: {creation_date}")
    if modification_date: lines.append(f"modification_date: {modification_date}")
    
    unique_tags = sorted(list(set(tag for tag in tags if tag)))
    if add_craft_tag and CRAFT_TAG not in unique_tags:
        unique_tags.append(CRAFT_TAG)
        unique_tags.sort()
        
    if unique_tags:
        tag_list_str = '[' + ', '.join(f'"{tag}"' for tag in unique_tags) + ']'
        lines.append(f"tags: {tag_list_str}")
        
    lines.append("---")
    return "\n".join(lines) + "\n" if len(lines) > 2 else ""


def process_content(content: str, note_title: str, attachments_subfolder_name: str) -> Tuple[str, List[str]]:
    """Performs all processing on the markdown content."""
    def replace_craft_link(match: re.Match) -> str:
        display_text, url = match.groups()
        uuid_match = re.search(r'(?:blockId|id|identifier)=([a-fA-F0-9\-]+)', url, re.IGNORECASE)
        if uuid_match and uuid_match.group(1) in uuid_to_filename_map:
            target_filename = uuid_to_filename_map[uuid_match.group(1)]
            sanitized_display = sanitize_filename(display_text)
            if target_filename == sanitized_display: return f"[[{target_filename}]]"
            return f"[[{target_filename}|{display_text}]]"
        logging.warning(f"Could not find UUID for link '{display_text}'. Falling back to simple wikilink.")
        return f"[[{sanitize_filename(display_text)}]]"
    content = re.sub(r'\[([^\]]+)\]\((craftdocs:\/\/open\?[^)]+)\)', replace_craft_link, content)
    
    def update_asset_link(match: re.Match) -> str:
        decoded_filename = unquote(match.group(2))
        sanitized_filename = sanitize_filename(decoded_filename)
        full_link_path = Path(attachments_subfolder_name) / sanitized_filename
        return f"![[{full_link_path.as_posix()}]]"
    content = re.sub(r'!\[(.*?)\]\(assets/(.*?)\)', update_asset_link, content)

    content = re.sub(r'\[([^\]]+)\]\(javascript:[^)]+\)', r'\1', content)
    
    tags = re.findall(r'#([a-zA-Z0-9_\-\/]+(?:\.[a-zA-Z0-9_\-\/]+)*)', content)
    content = re.sub(r'#([a-zA-Z0-9_\-\/]+(?:\.[a-zA-Z0-9_\-\/]+)*)', r'\1', content)
    
    content = re.sub(r'(?m)^(\s*-\s\[\s*\].+?)(?:\s+#task)?$', r'\1 #task', content)
    
    if note_title:
        content = re.sub(r'(?i)^#\s*' + re.escape(note_title) + r'\s*\n', '', content, count=1)
    
    return content.strip(), tags

def process_textbundle(bundle_path: Path, output_dir_for_note: Path, assets_base_dir: Path, add_craft_tag: bool) -> bool:
    """Processes a single .textbundle into a single, faithful .md file."""
    markdown_files = list(bundle_path.glob('*.markdown')) + list(bundle_path.glob('*.md'))
    if len(markdown_files) > 1: logging.warning(f"Multiple markdown files in {bundle_path.name}; using first: {markdown_files[0].name}")
    if not markdown_files: logging.warning(f"Skipping '{bundle_path.name}', no markdown file found."); return False

    try:
        note_title = sanitize_filename(bundle_path.stem)
        creation_date, modification_date = get_metadata(bundle_path)
        
        if match := re.match(r'(\d{4})[.-](\d{2})[.-](\d{2})', note_title):
            try:
                year, month, day = map(int, match.groups())
                title_date_str = datetime(year, month, day).strftime('%Y-%m-%d')
                creation_date = title_date_str
                # Preserve original modification date
            except ValueError:
                logging.warning(f"Filename '{note_title}' looks like a date, but is invalid.")

        with open(markdown_files[0], 'r', encoding='utf-8') as f: full_content = f.read()
        
        attachments_subfolder = f"{ATTACHMENTS_DIR}/{note_title}"
        content, tags = process_content(full_content, note_title, attachments_subfolder)
        frontmatter = create_frontmatter(tags, creation_date, modification_date, add_craft_tag)
        
        output_filepath = output_dir_for_note / f"{note_title}.md"
        counter = 1; base_name = note_title
        while output_filepath.exists():
            note_title = f"{base_name}-{counter}"; output_filepath = output_dir_for_note / f"{note_title}.md"; counter += 1

        output_filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(output_filepath, 'w', encoding='utf-8') as f: f.write(frontmatter + "\n" + content)
        logging.info(f"Converted: {output_filepath}")

        bundle_assets_path = bundle_path / 'assets'
        if bundle_assets_path.is_dir():
            note_assets_dir = assets_base_dir / note_title
            note_assets_dir.mkdir(parents=True, exist_ok=True)
            for asset_path in bundle_assets_path.iterdir():
                if asset_path.suffix.lower() != '.bin':
                    sanitized_name = sanitize_filename(unquote(asset_path.name))
                    dest_path = note_assets_dir / sanitized_name
                    asset_counter = 1; asset_stem, asset_suffix = dest_path.stem, dest_path.suffix
                    while dest_path.exists():
                        dest_path = note_assets_dir / f"{asset_stem}-{asset_counter}{asset_suffix}"; asset_counter += 1
                    shutil.copy2(asset_path, dest_path)
                    final_asset_path = Path(attachments_subfolder) / dest_path.name
                    found_assets.add(final_asset_path.as_posix())
        return True
    except Exception as e:
        logging.error(f"Failed processing {bundle_path.name}: {e}", exc_info=True); return False

def final_polish(output_dir: str, cleanup_links: bool, delete_empty: bool) -> None:
    """Performs final polishing and optional broken link cleanup."""
    logging.info("\n--- Starting Final Polishing Phase ---")
    output_path = Path(output_dir)
    deleted, renamed, daily_notes, cleaned_links = 0, 0, 0, 0
    
    all_files = list(output_path.rglob('*.md'))
    for filepath in all_files:
        try:
            content = filepath.read_text(encoding='utf-8')
            if cleanup_links:
                original_content = content
                def link_replacer(match):
                    link_target = match.group(1).replace('\\', '/')
                    if link_target not in found_assets: 
                        nonlocal cleaned_links
                        cleaned_links +=1
                        return ""
                    return match.group(0)
                content = re.sub(r'^\s*!\[\[([^\]]+)\]\]\s*$', link_replacer, content, flags=re.MULTILINE)
                if content != original_content: filepath.write_text(content, encoding='utf-8')

            content_after_frontmatter = re.sub(r'---\s*[\s\S]*?---', '', content, count=1).strip()
            if delete_empty and not content_after_frontmatter:
                filepath.unlink(); deleted += 1; logging.info(f"Deleted empty note: {filepath.name}"); continue
            
            if filepath.stem.lower() in ['new document', 'untitled', '']:
                new_name_base = sanitize_filename(content_after_frontmatter.split('\n')[0].lstrip('# ').strip())
                if new_name_base:
                    new_filepath = filepath.with_name(f"{new_name_base}.md")
                    if not new_filepath.exists():
                        filepath.rename(new_filepath); renamed += 1; logging.info(f"Renamed '{filepath.name}' to '{new_filepath.name}'"); filepath = new_filepath
            
            if match := re.match(r'(\d{4})[.-](\d{2})[.-](\d{2})', filepath.stem):
                try:
                    datetime(int(match.group(1)), int(match.group(2)), int(match.group(3)))
                    new_name = f"{match.group(1)}-{match.group(2)}-{match.group(3)}.md"
                    new_filepath = filepath.with_name(new_name)
                    if not new_filepath.exists(): filepath.rename(new_filepath); daily_notes += 1
                except ValueError: pass
        except (IOError, OSError) as e:
            logging.warning(f"Could not process {filepath.name}. Reason: {e}")
    
    summary = f"Deleted {deleted} notes, renamed {renamed} notes, standardized {daily_notes} daily notes"
    if cleanup_links: summary += f", cleaned {cleaned_links} broken image links"
    logging.info(f"\nPolishing Complete: {summary}.")

def get_user_preferences(output_path: Path) -> dict:
    """Asks user a series of questions to configure the script."""
    preferences = {}
    if output_path.exists() and any(output_path.iterdir()):
        logging.warning(f"Output directory '{output_path}' exists and is not empty.")
        if input("This will completely overwrite the output directory. Continue? (y/n): ").strip().lower() != 'y':
            logging.critical("Aborting to prevent data loss."); sys.exit(1)
    
    preferences['add_craft_tag'] = input(f"Add a '{CRAFT_TAG}' tag to all imported notes? (y/n): ").strip().lower() == 'y'
    preferences['cleanup_links'] = input("Clean up links to images that are missing from the export? (y/n): ").strip().lower() == 'y'
    preferences['delete_empty'] = input("Delete notes that are empty after conversion? (y/n): ").strip().lower() == 'y'
    
    return preferences

def main() -> None:
    parser = argparse.ArgumentParser(description="An interactive, user-friendly tool to convert Craft exports for Obsidian.")
    parser.add_argument("input_dir", help="Path to the directory containing exported Craft files (e.g., './input/Corys Space').")
    parser.add_argument("output_dir", nargs='?', default="obsidian-vault", help="Path for the final Obsidian vault.")
    args = parser.parse_args()

    input_path, output_path = Path(args.input_dir), Path(args.output_dir)
    if not input_path.is_dir(): logging.critical(f"Error: Input directory '{args.input_dir}' not found."); sys.exit(1)
    if not any(p.is_dir() and p.suffix.lower() in ['.textbundle', '.textpack'] for p in input_path.rglob('*')):
        logging.critical(f"Error: No .textbundle files found in '{args.input_dir}'."); sys.exit(1)

    logging.info("--- Welcome to the Craft to Obsidian Migrator ---")
    prefs = get_user_preferences(output_path)
    
    if output_path.exists(): shutil.rmtree(output_path)
    output_path.mkdir(parents=True)
    assets_base_dir = output_path / ATTACHMENTS_DIR; assets_base_dir.mkdir()
    build_uuid_map(args.input_dir)
    
    logging.info("\n--- Pass 2: Converting Notes and Assets ---")
    processed_count = 0
    bundles = [p for p in input_path.rglob('*') if p.is_dir() and p.suffix.lower() in ['.textbundle', '.textpack']]
    
    for i, bundle_path in enumerate(bundles):
        if (i + 1) % 50 == 0: logging.info(f"Progress: {i + 1} of {len(bundles)}...")
        relative_path = bundle_path.parent.relative_to(input_path)
        output_path_for_notes = output_path / (relative_path if relative_path != Path('.') else Path(''))
        if process_textbundle(bundle_path, output_path_for_notes, assets_base_dir, prefs['add_craft_tag']):
            processed_count += 1
            
    logging.info(f"\nConversion Phase Complete! Processed {processed_count} bundles.")
    final_polish(args.output_dir, prefs['cleanup_links'], prefs['delete_empty'])
    logging.info("\nAll tasks complete! Your Obsidian vault is ready.")

if __name__ == "__main__":
    main()
