"""
Data Migration Script: Local Files to Azure Blob Storage

This script migrates existing local data (resumes, reports, and processed files) 
to Azure Blob Storage and cleans up local directories if migration is successful.

Usage:
    python scripts/migrate_to_blob.py [--dry-run] [--user-id USER_ID]
    
Arguments:
    --dry-run: Preview what files would be migrated without actually moving them
    --user-id: Associate migrated files with a specific user session (default: guest)
"""

import os
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple

# Import blob storage service
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.services.blob_storage import blob_storage


def scan_local_files() -> Dict[str, List[Tuple[str, str]]]:
    """
    Scan local directories for files to migrate.
    
    Returns:
        Dict mapping category to list of (local_path, suggested_blob_name) tuples
    """
    base_path = Path(__file__).parent.parent
    categories = {}
    
    # Raw resumes from data/raw_resumes/
    raw_resumes_dir = base_path / "data" / "raw_resumes"
    if raw_resumes_dir.exists():
        raw_files = []
        for file_path in raw_resumes_dir.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in ['.pdf', '.docx', '.txt', '.zip']:
                blob_name = f"raw_resumes/{file_path.name}"
                raw_files.append((str(file_path), blob_name))
        categories["raw_resumes"] = raw_files
    
    # Processed text files from data/processed/
    processed_dir = base_path / "data" / "processed"
    if processed_dir.exists():
        processed_files = []
        for file_path in processed_dir.rglob("*.txt"):
            if file_path.is_file():
                blob_name = f"processed/{file_path.name}"
                processed_files.append((str(file_path), blob_name))
        categories["processed"] = processed_files
    
    # Reports from reports/
    reports_dir = base_path / "reports"
    if reports_dir.exists():
        report_files = []
        for file_path in reports_dir.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in ['.json', '.xlsx', '.pdf', '.csv']:
                blob_name = f"reports/{file_path.name}"
                report_files.append((str(file_path), blob_name))
        categories["reports"] = report_files
    
    return categories


def migrate_files(categories: Dict[str, List[Tuple[str, str]]], user_id: str = "guest", dry_run: bool = False) -> Dict[str, int]:
    """
    Migrate files to Azure Blob Storage.
    
    Args:
        categories: Dict from scan_local_files()
        user_id: User ID for session-based organization
        dry_run: If True, only preview what would be migrated
        
    Returns:
        Dict with migration statistics
    """
    stats = {"uploaded": 0, "errors": 0, "total": 0}
    
    # Create a new session for migrated data
    if not dry_run:
        session_id = blob_storage.create_session(user_id, f"Migration {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print(f"Created migration session: {session_id}")
    
    for category, files in categories.items():
        print(f"\n=== Migrating {category} ({len(files)} files) ===")
        
        for local_path, blob_name in files:
            stats["total"] += 1
            
            try:
                file_size = os.path.getsize(local_path)
                print(f"  {local_path} -> {blob_name} ({file_size:,} bytes)")
                
                if not dry_run:
                    # Read file content
                    with open(local_path, "rb") as f:
                        file_content = f.read()
                    
                    # Upload to session-based blob storage
                    blob_url = blob_storage.upload_file_session(file_content, blob_name, user_id)
                    print(f"    ✓ Uploaded to: {blob_url}")
                    
                    stats["uploaded"] += 1
                else:
                    print(f"    [DRY RUN] Would upload to session-based blob storage")
                    
            except Exception as e:
                stats["errors"] += 1
                print(f"    ✗ Error: {e}")
    
    return stats


def cleanup_local_files(categories: Dict[str, List[Tuple[str, str]]], confirm: bool = False):
    """
    Remove local files after successful migration.
    
    Args:
        categories: Dict from scan_local_files()
        confirm: If True, actually delete files; otherwise just preview
    """
    print(f"\n=== Cleanup {'(PREVIEW)' if not confirm else ''} ===")
    
    for category, files in categories.items():
        print(f"\n{category}:")
        for local_path, _ in files:
            if confirm:
                try:
                    os.remove(local_path)
                    print(f"  ✓ Deleted: {local_path}")
                except Exception as e:
                    print(f"  ✗ Failed to delete {local_path}: {e}")
            else:
                print(f"  Would delete: {local_path}")
    
    # Remove empty directories
    base_path = Path(__file__).parent.parent
    for dir_name in ["data/raw_resumes", "data/processed", "reports"]:
        dir_path = base_path / dir_name
        if dir_path.exists() and confirm:
            try:
                if not any(dir_path.iterdir()):  # Check if empty
                    dir_path.rmdir()
                    print(f"  ✓ Removed empty directory: {dir_path}")
            except Exception as e:
                print(f"  ✗ Failed to remove directory {dir_path}: {e}")


def main():
    parser = argparse.ArgumentParser(description="Migrate local Resume Screener data to Azure Blob Storage")
    parser.add_argument("--dry-run", action="store_true", help="Preview migration without actually moving files")
    parser.add_argument("--user-id", default="guest", help="User ID for session organization (default: guest)")
    parser.add_argument("--cleanup", action="store_true", help="Delete local files after successful migration")
    
    args = parser.parse_args()
    
    print("Resume Screener - Data Migration to Azure Blob Storage")
    print("=" * 60)
    
    # Check Azure Blob configuration
    try:
        # Test connection
        blob_storage._ensure_container_exists()
        print("✓ Azure Blob Storage connection verified")
    except Exception as e:
        print(f"✗ Azure Blob Storage connection failed: {e}")
        print("\nEnsure AZURE_STORAGE_CONNECTION_STRING and AZURE_BLOB_CONTAINER are set correctly.")
        return 1
    
    # Scan for local files
    print(f"\nScanning for local files to migrate...")
    categories = scan_local_files()
    
    total_files = sum(len(files) for files in categories.values())
    if total_files == 0:
        print("No local files found to migrate.")
        return 0
    
    print(f"Found {total_files} files to migrate:")
    for category, files in categories.items():
        print(f"  - {category}: {len(files)} files")
    
    if args.dry_run:
        print("\n=== DRY RUN MODE ===")
    
    # Migrate files
    stats = migrate_files(categories, args.user_id, args.dry_run)
    
    print(f"\n=== Migration Summary ===")
    print(f"Total files: {stats['total']}")
    print(f"Successfully uploaded: {stats['uploaded']}")
    print(f"Errors: {stats['errors']}")
    
    # Cleanup if requested and migration was successful
    if args.cleanup and not args.dry_run and stats["errors"] == 0:
        confirm = input("\nDelete local files after successful migration? (y/N): ")
        if confirm.lower() == 'y':
            cleanup_local_files(categories, confirm=True)
        else:
            print("Local files preserved.")
    elif args.cleanup:
        cleanup_local_files(categories, confirm=False)
    
    return 0


if __name__ == "__main__":
    exit(main())