#!/usr/bin/env python3
"""
Security Cleanup Script
Replaces all sensitive Azure information with placeholders
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# =====================================
# SENSITIVE DATA TO REPLACE
# =====================================

REPLACEMENTS = {
    # Public IPs
    "172.168.108.4": "<YOUR-PHASE1-PUBLIC-IP>",
    "172.169.51.14": "<YOUR-PUBLIC-IP>",
    
    # Azure Container Registry
    "acrmaqfapkj24vye7.azurecr.io": "<YOUR-ACR>.azurecr.io",
    "acrmaqfapkj24vye7": "<YOUR-ACR>",
    
    # Azure OpenAI
    "oai-qfapkj24vye7a.openai.azure.com": "<YOUR-OPENAI-RESOURCE>.openai.azure.com",
    "oai-qfapkj24vye7a": "<YOUR-OPENAI-RESOURCE>",
    
    # Image tags (specific deployment IDs)
    ":azd-deploy-1762200192": ":latest",
}

# Files to exclude from cleanup (already templates or safe)
EXCLUDE_FILES = {
    ".env.example",
    ".env.template",
    "cleanup_sensitive_data.py",
    "setup_project.py",
    ".git",
    ".gitignore",
    "__pycache__",
    "SECURITY_CLEANUP_CHECKLIST.md",
}

# File extensions to process
INCLUDE_EXTENSIONS = {
    ".py",
    ".md",
    ".sh",
    ".yaml",
    ".yml",
    ".json",
    ".txt",
}


class SensitiveDataCleaner:
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir).resolve()
        self.replacements = REPLACEMENTS
        self.files_modified: List[str] = []
        self.dry_run = False
        
    def should_process_file(self, file_path: Path) -> bool:
        """Check if file should be processed"""
        # Skip excluded files/directories
        for exclude in EXCLUDE_FILES:
            if exclude in str(file_path):
                return False
        
        # Only process specific extensions
        if file_path.suffix not in INCLUDE_EXTENSIONS:
            return False
            
        # Skip binary files
        if file_path.suffix in {".pyc", ".pyo", ".so", ".dll", ".exe"}:
            return False
            
        return True
    
    def find_sensitive_data(self, content: str) -> List[Tuple[str, str]]:
        """Find all sensitive data in content"""
        found = []
        for sensitive, placeholder in self.replacements.items():
            if sensitive in content:
                found.append((sensitive, placeholder))
        return found
    
    def clean_file(self, file_path: Path) -> bool:
        """Clean sensitive data from a single file"""
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Find sensitive data
            found = self.find_sensitive_data(content)
            if not found:
                return False
            
            # Replace sensitive data
            modified_content = content
            for sensitive, placeholder in found:
                modified_content = modified_content.replace(sensitive, placeholder)
            
            # Write back if not dry run
            if not self.dry_run:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(modified_content)
            
            # Record modification
            self.files_modified.append(str(file_path.relative_to(self.root_dir)))
            
            # Print changes
            print(f"{'[DRY RUN] ' if self.dry_run else ''}✓ {file_path.relative_to(self.root_dir)}")
            for sensitive, placeholder in found:
                count = content.count(sensitive)
                print(f"  • {sensitive} → {placeholder} ({count} occurrences)")
            
            return True
            
        except Exception as e:
            print(f"✗ Error processing {file_path}: {e}", file=sys.stderr)
            return False
    
    def scan_directory(self):
        """Scan directory for files with sensitive data"""
        print(f"\n{'='*60}")
        print(f"Scanning: {self.root_dir}")
        print(f"Mode: {'DRY RUN (no changes)' if self.dry_run else 'LIVE (will modify files)'}")
        print(f"{'='*60}\n")
        
        files_processed = 0
        files_with_changes = 0
        
        for file_path in self.root_dir.rglob("*"):
            if not file_path.is_file():
                continue
                
            if not self.should_process_file(file_path):
                continue
            
            files_processed += 1
            if self.clean_file(file_path):
                files_with_changes += 1
        
        # Summary
        print(f"\n{'='*60}")
        print(f"SUMMARY")
        print(f"{'='*60}")
        print(f"Files scanned: {files_processed}")
        print(f"Files {'that would be ' if self.dry_run else ''}modified: {files_with_changes}")
        
        if self.files_modified:
            print(f"\n{'Files that would be modified:' if self.dry_run else 'Modified files:'}")
            for f in sorted(self.files_modified):
                print(f"  • {f}")
        
        print(f"{'='*60}\n")
        
        return files_with_changes


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Clean sensitive data from project files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run (preview changes without modifying files)
  python cleanup_sensitive_data.py --dry-run
  
  # Clean all files
  python cleanup_sensitive_data.py
  
  # Clean specific directory
  python cleanup_sensitive_data.py --dir ./docs
        """
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without modifying files'
    )
    
    parser.add_argument(
        '--dir',
        default='.',
        help='Directory to scan (default: current directory)'
    )
    
    args = parser.parse_args()
    
    # Confirm if not dry run
    if not args.dry_run:
        print("\n⚠️  WARNING: This will modify files in place!")
        print("Make sure you have committed your changes or have a backup.")
        response = input("\nContinue? [y/N]: ")
        if response.lower() != 'y':
            print("Cancelled.")
            return 1
    
    # Run cleaner
    cleaner = SensitiveDataCleaner(args.dir)
    cleaner.dry_run = args.dry_run
    files_changed = cleaner.scan_directory()
    
    if args.dry_run and files_changed > 0:
        print("Run without --dry-run to apply these changes.\n")
    elif files_changed > 0:
        print("✓ Cleanup complete!\n")
        print("Next steps:")
        print("  1. Review the changes: git diff")
        print("  2. Test the application still works")
        print("  3. Commit the changes: git add . && git commit -m 'Remove sensitive data'")
        print()
    else:
        print("No sensitive data found. Project is clean!\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
