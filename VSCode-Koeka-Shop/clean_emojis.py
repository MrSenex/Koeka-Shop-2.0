#!/usr/bin/env python3
"""
Script to remove all emojis from the POS system files
"""

import os
import re
import glob

def remove_emojis_from_text(text):
    """Remove all emojis from text"""
    # Comprehensive emoji pattern
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U00002600-\U000027BF"  # misc symbols
        "\U0001F900-\U0001F9FF"  # supplemental symbols
        "\U00002700-\U000027BF"  # dingbats
        "\U0001F018-\U0001F270"  # various symbols
        "]+", 
        flags=re.UNICODE
    )
    
    # Also remove specific common emojis manually
    specific_emojis = [
        '', '', '', '', '', '️', '', '', '', '️', 
        '', '', '', '', '', '', '', '', '', '', 
        '', '', '', '️', '', '', '', '', '️', '',
        '', '', '', '', '', '', '', '', '', '', 
        '', '', '', '', '', '', '', '', '', '️',
        ''
    ]
    
    # Remove emojis using pattern
    cleaned = emoji_pattern.sub('', text)
    
    # Remove specific emojis
    for emoji in specific_emojis:
        cleaned = cleaned.replace(emoji, '')
    
    return cleaned

def clean_file(file_path):
    """Clean emojis from a file"""
    try:
        print(f"Cleaning: {file_path}")
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        cleaned_content = remove_emojis_from_text(content)
        
        # Only write if content changed
        if cleaned_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(cleaned_content)
            print(f"  - Cleaned emojis from {file_path}")
        else:
            print(f"  - No emojis found in {file_path}")
            
    except Exception as e:
        print(f"Error cleaning {file_path}: {e}")

def main():
    """Clean all files in the project"""
    print("Removing emojis from all POS system files...")
    print("=" * 50)
    
    # File patterns to clean
    patterns = [
        '**/*.py',
        '**/*.md',
        '**/*.txt',
        '**/*.bat',
        '**/*.sh'
    ]
    
    files_cleaned = 0
    
    for pattern in patterns:
        for file_path in glob.glob(pattern, recursive=True):
            # Skip __pycache__ and other temp directories
            if '__pycache__' in file_path or '.git' in file_path:
                continue
                
            clean_file(file_path)
            files_cleaned += 1
    
    print("=" * 50)
    print(f"Completed! Processed {files_cleaned} files.")
    print("All emojis have been removed from the POS system.")

if __name__ == "__main__":
    main()
