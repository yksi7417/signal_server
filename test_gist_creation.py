#!/usr/bin/env python3
"""Test gist creation with actual bug report data."""

import os
import sys
import base64

# Test PyGithub availability
try:
    from github import Github
    print("✓ PyGithub is available")
except ImportError:
    print("✗ PyGithub NOT available - install with: pip install PyGithub")
    sys.exit(1)

# Check GITHUB_TOKEN
github_token = os.getenv("GITHUB_TOKEN")
if not github_token:
    print("✗ GITHUB_TOKEN not set")
    print("\nSet it with:")
    print("  PowerShell: $env:GITHUB_TOKEN='your_token_here'")
    print("  Linux:      export GITHUB_TOKEN='your_token_here'")
    sys.exit(1)

print(f"✓ GITHUB_TOKEN is set ({'*' * 8}{github_token[-4:]})")

# Test bug report
parquet_path = "bug_reports/bug_ba1e3514/actions.parquet"

if not os.path.exists(parquet_path):
    print(f"✗ Parquet file not found: {parquet_path}")
    sys.exit(1)

print(f"✓ Parquet file exists ({os.path.getsize(parquet_path)} bytes)")

# Read and encode
print("\nReading parquet file...")
with open(parquet_path, "rb") as f:
    parquet_content = f.read()

print(f"✓ Read {len(parquet_content)} bytes")

# Encode to base64
print("Encoding to base64...")
parquet_b64 = base64.b64encode(parquet_content).decode('ascii')
print(f"✓ Encoded to {len(parquet_b64)} characters")

# Prepare gist files
bug_id = "ba1e3514"
action_count = 87

gist_files = {
    "actions.parquet.b64": {
        "content": parquet_b64
    },
    "README.md": {
        "content": f"# Bug Report Action Log\n\n"
                   f"Bug ID: `{bug_id}`\n\n"
                   f"This gist contains the action log for bug report {bug_id}.\n\n"
                   f"## Files\n"
                   f"- `actions.parquet.b64`: Base64-encoded parquet file with {action_count} actions\n\n"
                   f"## How to Use\n"
                   f"Download `actions.parquet.b64` and decode:\n"
                   f"```bash\n"
                   f"# On Linux/Mac:\n"
                   f"base64 -d actions.parquet.b64 > actions.parquet\n\n"
                   f"# On Windows PowerShell:\n"
                   f"[System.Convert]::FromBase64String((Get-Content actions.parquet.b64)) | Set-Content actions.parquet -Encoding Byte\n\n"
                   f"# Then view the actions:\n"
                   f"python -m mahjong_engine.action_log actions.parquet\n"
                   f"```"
    }
}

print(f"\nPrepared gist with {len(gist_files)} files")
print(f"  - actions.parquet.b64: {len(parquet_b64)} chars")
print(f"  - README.md: {len(gist_files['README.md']['content'])} chars")

# Try to create gist
print("\nConnecting to GitHub...")
try:
    gh = Github(github_token)
    user = gh.get_user()
    print(f"✓ Connected as: {user.login}")

    print("\nCreating private gist...")
    gist = user.create_gist(
        public=False,
        files=gist_files,
        description=f"Action log for bug {bug_id}"
    )

    print(f"\n✅ SUCCESS! Gist created:")
    print(f"   URL: {gist.html_url}")
    print(f"   ID: {gist.id}")
    print(f"   Files: {len(gist.files)}")

except Exception as e:
    print(f"\n✗ FAILED to create gist:")
    print(f"   Error: {e}")
    print(f"\n   Full traceback:")
    import traceback
    traceback.print_exc()
    sys.exit(1)
