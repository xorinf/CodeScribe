"""
Secret scanning heuristics for CodeScribe Data Cleanser.
"""

import re
import logging
from typing import List

logger = logging.getLogger("CodeScribe.Cleanser.Secrets")

class SecretScanner:
    """Scans code for common secrets (PII, tokens, keys)."""
    
    # Common high-confidence secret patterns
    SECRET_PATTERNS = [
        # AWS Access Key ID
        re.compile(r"(?i)\b(?:AKIA|ABIA|ACCA|ASIA)[0-9A-Z]{16}\b"),
        # Generic API Key / Secret assignments
        re.compile(r"(?i)(?:api[_-]?key|secret|token|password)[\s]*[:=][\s]*[\"'][a-zA-Z0-9\-_]{20,}[\"']"),
        # GitHub Personal Access Token
        re.compile(r"(?i)\bgh[pousr]_[A-Za-z0-9_]{36}\b"),
        # Slack Token
        re.compile(r"(?i)\bxox[baprs]-[0-9]{10,13}-[a-zA-Z0-9]{24}\b"),
        # RSA Private Key
        re.compile(r"-----BEGIN (?:RSA )?PRIVATE KEY-----"),
    ]

    def has_secrets(self, content: str) -> bool:
        """
        Check if the content contains any matched secrets.
        Returns True if a secret is found, False otherwise.
        """
        for pattern in self.SECRET_PATTERNS:
            if pattern.search(content):
                return True
        return False
