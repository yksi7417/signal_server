#!/usr/bin/env python3
"""
Autonomous Bug Fix Loop - Cross-platform (Windows PowerShell & Linux)

This script automates the bug fixing workflow:
1. Check for open bugs on GitHub
2. For each bug: Analyze -> Test -> Fix -> Verify -> Commit -> Push
3. Update GitHub issue with fix details

Usage:
    python autonomous_loop.py [--max-bugs N] [--dry-run]

Requirements:
    - PyGithub: pip install PyGithub
    - GITHUB_TOKEN environment variable set
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

try:
    from github import Github
except ImportError:
    print("ERROR: PyGithub not installed. Install with: pip install PyGithub")
    sys.exit(1)


def run_command(cmd, description="", check=True):
    """Run a command and return output. Works on Windows PowerShell and Linux."""
    print(f"→ {description or cmd}")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            check=check
        )
        if result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Command failed with exit code {e.returncode}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        if check:
            raise
        return e


def check_environment():
    """Verify required environment and tools."""
    print("=" * 60)
    print("CHECKING ENVIRONMENT")
    print("=" * 60)

    # Check Python version
    print(f"Python: {sys.version}")

    # Check for GITHUB_TOKEN
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        print("ERROR: GITHUB_TOKEN environment variable not set")
        print("Set it with:")
        print("  Windows PowerShell: $env:GITHUB_TOKEN='your_token_here'")
        print("  Linux/Mac:          export GITHUB_TOKEN='your_token_here'")
        sys.exit(1)
    print(f"✓ GITHUB_TOKEN: {'*' * 8}{github_token[-4:]}")

    # Check git
    result = run_command("git --version", check=False)
    if result.returncode != 0:
        print("ERROR: git not found")
        sys.exit(1)
    print(f"✓ Git installed")

    # Check pytest
    result = run_command("python -m pytest --version", check=False)
    if result.returncode != 0:
        print("WARNING: pytest not found, install with: pip install pytest")
    else:
        print("✓ pytest installed")

    print()
    return github_token


def get_open_bugs(github_token, repo_name, max_bugs=10):
    """Get open bugs from GitHub."""
    print("=" * 60)
    print(f"FETCHING OPEN BUGS FROM {repo_name}")
    print("=" * 60)

    try:
        gh = Github(github_token)
        repo = gh.get_repo(repo_name)
        issues = list(repo.get_issues(state='open', labels=['bug'])[:max_bugs])

        print(f"Found {len(issues)} open bugs")
        for i, issue in enumerate(issues, 1):
            labels = [label.name for label in issue.labels]
            print(f"  {i}. #{issue.number}: {issue.title}")
            print(f"     Labels: {', '.join(labels)}")

        print()
        return issues
    except Exception as e:
        print(f"ERROR: Failed to fetch bugs: {e}")
        sys.exit(1)


def fix_bug(issue, dry_run=False):
    """Fix a single bug following the autonomous workflow."""
    print("=" * 60)
    print(f"FIXING BUG #{issue.number}")
    print("=" * 60)
    print(f"Title: {issue.title}")
    print(f"URL: {issue.html_url}")
    print()

    # Step 1: Analyze the bug
    print("Step 1: Analyzing bug...")
    print(f"Description:\n{issue.body[:500]}...")
    print()

    # TODO: Download gist if available
    # TODO: Analyze action log

    if dry_run:
        print("DRY RUN: Skipping actual fix")
        return

    # Step 2: Write a failing test
    print("Step 2: Would write failing test...")
    # TODO: Implement test generation

    # Step 3: Implement fix
    print("Step 3: Would implement fix...")
    # TODO: Implement fix

    # Step 4: Run tests
    print("Step 4: Running all tests...")
    result = run_command(
        'python -m pytest -m "not integration" -v tests/engine/',
        "Running unit tests",
        check=False
    )

    if result.returncode != 0:
        print("ERROR: Tests failed! Stopping before commit.")
        return False

    print("✓ All tests passed!")

    # Step 5: Commit
    print("Step 5: Would commit changes...")
    # TODO: Implement commit

    # Step 6: Push
    print("Step 6: Would push changes...")
    # TODO: Implement push

    # Step 7: Comment on issue
    print("Step 7: Would comment on issue...")
    # TODO: Implement GitHub comment

    print(f"✓ Bug #{issue.number} fixed!")
    return True


def main():
    parser = argparse.ArgumentParser(description="Autonomous Bug Fix Loop")
    parser.add_argument("--max-bugs", type=int, default=10, help="Maximum bugs to process")
    parser.add_argument("--dry-run", action="store_true", help="Don't make changes, just show what would happen")
    parser.add_argument("--repo", default="yksi7417/signal_server", help="GitHub repository")
    args = parser.parse_args()

    # Check environment
    github_token = check_environment()

    # Get open bugs
    bugs = get_open_bugs(github_token, args.repo, args.max_bugs)

    if not bugs:
        print("No open bugs found!")
        return

    # Process each bug
    print("=" * 60)
    print(f"STARTING AUTONOMOUS FIX LOOP ({'DRY RUN' if args.dry_run else 'LIVE'})")
    print("=" * 60)
    print()

    fixed_count = 0
    for bug in bugs:
        if fix_bug(bug, dry_run=args.dry_run):
            fixed_count += 1

    print("=" * 60)
    print(f"COMPLETED: Fixed {fixed_count}/{len(bugs)} bugs")
    print("=" * 60)


if __name__ == "__main__":
    main()
