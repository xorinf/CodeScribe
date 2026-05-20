"""
Data cleansing pipeline for CodeScribe.
Extracts files from zipballs, applies filters, and writes cleaned data to JSONL.
"""

import json
import logging
import zipfile
from pathlib import Path
from typing import List, Set

from .heuristics import QualityFilter
from .secrets import SecretScanner

logger = logging.getLogger("CodeScribe.Cleanser.Pipeline")

class CleanserPipeline:
    """Orchestrates the extraction and cleansing of scraped repositories."""

    def __init__(self, languages: List[str] = None):
        self.quality_filter = QualityFilter()
        self.secret_scanner = SecretScanner()
        # Default to python extensions if none provided
        self.allowed_extensions: Set[str] = set(languages or [".py"])

    def _is_allowed_extension(self, filename: str) -> bool:
        """Check if the file extension is allowed."""
        path = Path(filename)
        return path.suffix in self.allowed_extensions

    def process_directory(self, input_dir: Path, output_file: Path):
        """Process all zipballs in a directory and write to a JSONL file."""
        input_dir = Path(input_dir)
        output_file = Path(output_file)
        
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        zip_files = list(input_dir.glob("*.zip"))
        if not zip_files:
            logger.warning(f"No zip files found in {input_dir}")
            return

        logger.info(f"Starting cleansing pipeline for {len(zip_files)} zipballs...")
        
        total_files = 0
        retained_files = 0

        with open(output_file, "w", encoding="utf-8") as out_f:
            for zip_path in zip_files:
                try:
                    with zipfile.ZipFile(zip_path, "r") as z:
                        for file_info in z.infolist():
                            if file_info.is_dir():
                                continue
                                
                            filename = file_info.filename
                            if not self._is_allowed_extension(filename):
                                continue
                                
                            total_files += 1
                            
                            try:
                                # Read content and decode
                                content_bytes = z.read(file_info)
                                content = content_bytes.decode("utf-8")
                            except UnicodeDecodeError:
                                # Skip non-utf8 files
                                continue
                                
                            # Apply heuristics
                            if not self.quality_filter.is_high_quality(content):
                                continue
                                
                            # Apply secret scanning
                            if self.secret_scanner.has_secrets(content):
                                logger.debug(f"Secret detected in {filename} from {zip_path.name}")
                                continue
                                
                            # If it passes, we keep it
                            retained_files += 1
                            
                            # Derive repo name from zip file name (assumes owner_repo.zip format)
                            repo_name = zip_path.stem
                            
                            record = {
                                "repo": repo_name,
                                "file_path": filename,
                                "content": content
                            }
                            
                            out_f.write(json.dumps(record) + "\n")
                            
                except zipfile.BadZipFile:
                    logger.error(f"Bad zip file: {zip_path}")
                except Exception as e:
                    logger.error(f"Error processing {zip_path}: {e}")

        logger.info(
            f"Cleansing complete. Retained {retained_files}/{total_files} files ({(retained_files/max(1, total_files))*100:.2f}%). Output saved to {output_file}"
        )
