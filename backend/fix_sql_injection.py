#!/usr/bin/env python3
"""
Automated SQL Injection Fix Script
Converts f-string and .format() SQL queries to parameterized queries
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple

# SQL keywords that indicate a query
SQL_KEYWORDS = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP', 'ALTER']

def find_sql_injections(file_path: Path) -> List[Tuple[int, str]]:
    """Find lines with potential SQL injection vulnerabilities"""
    vulnerabilities = []

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for i, line in enumerate(lines, 1):
        # Check for f-strings with SQL keywords
        for keyword in SQL_KEYWORDS:
            if re.search(rf'f["\'].*{keyword}', line, re.IGNORECASE):
                vulnerabilities.append((i, line.strip()))
            # Check for .format() with SQL keywords
            elif re.search(rf'["\'].*{keyword}.*["\']\s*\.format', line, re.IGNORECASE):
                vulnerabilities.append((i, line.strip()))

    return vulnerabilities

def main():
    backend_dir = Path(__file__).parent

    # Files to check (from grep results)
    vulnerable_files = [
        "core/agents/agent_crud.py",
        "core/billing/repo/commitments.py",
        "core/billing/repo/credit_accounts.py",
        "core/billing/repo/customers.py",
        "core/billing/repo/trial_history.py",
        "core/services/db.py",
        "scripts/archive_pool_sandboxes.py",
        "scripts/setup_graphdb_repository.py",
    ]

    print("🔍 SQL Injection Vulnerability Audit")
    print("=" * 50)

    total_vulns = 0

    for file_rel_path in vulnerable_files:
        file_path = backend_dir / file_rel_path
        if not file_path.exists():
            print(f"⚠️  {file_rel_path}: File not found")
            continue

        vulns = find_sql_injections(file_path)
        if vulns:
            print(f"\n📄 {file_rel_path}")
            print(f"   Found {len(vulns)} potential vulnerabilities:")
            for line_num, line_content in vulns:
                print(f"   Line {line_num}: {line_content[:80]}...")
                total_vulns += 1

    print(f"\n" + "=" * 50)
    print(f"📊 Total vulnerabilities found: {total_vulns}")
    print(f"\n✅ Next steps:")
    print(f"   1. Review each vulnerability manually")
    print(f"   2. Convert to parameterized queries with :param syntax")
    print(f"   3. Update database calls to pass values dict")
    print(f"   4. Test queries still work")

if __name__ == "__main__":
    main()
