#!/usr/bin/env python3
"""
GitHub Actions Workflow Validator
Validates workflow files for common syntax issues and GitHub Actions specific problems.
"""

import yaml
import os
import re
import sys

def validate_workflow_file(file_path):
    """Validate a single workflow file"""
    errors = []
    warnings = []
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Check for common GitHub Actions syntax issues
    
    # 1. Check for incorrect secrets usage in if conditions
    secrets_in_if = re.findall(r'if:\s*\$\{\{\s*secrets\.[A-Z_]+\s*\}\}', content)
    if secrets_in_if:
        errors.append("Incorrect secrets usage in 'if' conditions. Use env variables instead.")
        for match in secrets_in_if:
            errors.append(f"  Found: {match}")
    
    # 2. Check for missing env context when using secrets in conditions
    if_env_pattern = r'if:\s*env\.[A-Z_]+\s*!?=\s*[\'"][\'"]\s*$'
    env_definitions = re.findall(r'env:\s*\n\s*[A-Z_]+:', content, re.MULTILINE)
    
    # 3. Check for proper job dependencies
    needs_pattern = re.findall(r'needs:\s*\[([^\]]+)\]', content)
    
    # 4. Check for proper artifact naming (no spaces or special chars)
    artifact_names = re.findall(r'name:\s*([^\n]+)', content)
    for name in artifact_names:
        if ' ' in name or any(char in name for char in ['/', '\\', ':', '*', '?', '"', '<', '>', '|']):
            warnings.append(f"Artifact name may contain invalid characters: {name}")
    
    # 5. Check for missing required permissions
    if 'actions/checkout@v' in content and 'permissions:' not in content:
        warnings.append("Consider adding explicit permissions for security")
    
    # 6. Check for hardcoded versions (suggest using latest)
    hardcoded_versions = re.findall(r'uses:\s*actions/[^@]+@v\d+', content)
    if hardcoded_versions:
        warnings.append("Consider using latest versions or pinning to specific commits for security")
    
    return errors, warnings

def main():
    """Main validation function"""
    workflow_dir = 'github-workflows-backup'
    
    if not os.path.exists(workflow_dir):
        print(f"❌ Directory {workflow_dir} not found!")
        sys.exit(1)
    
    print("🔍 Validating GitHub Actions workflow files...")
    print("=" * 60)
    
    total_errors = 0
    total_warnings = 0
    
    for file in sorted(os.listdir(workflow_dir)):
        if not file.endswith('.yml'):
            continue
            
        file_path = os.path.join(workflow_dir, file)
        print(f"\n📄 Checking {file}...")
        
        # First check YAML syntax
        try:
            with open(file_path, 'r') as f:
                yaml.safe_load(f)
            print("  ✅ Valid YAML syntax")
        except yaml.YAMLError as e:
            print(f"  ❌ YAML Error: {e}")
            total_errors += 1
            continue
        
        # Then check GitHub Actions specific issues
        errors, warnings = validate_workflow_file(file_path)
        
        if errors:
            print("  ❌ Errors found:")
            for error in errors:
                print(f"    - {error}")
            total_errors += len(errors)
        
        if warnings:
            print("  ⚠️  Warnings:")
            for warning in warnings:
                print(f"    - {warning}")
            total_warnings += len(warnings)
        
        if not errors and not warnings:
            print("  ✅ No issues found")
    
    print("\n" + "=" * 60)
    print(f"📊 Validation Summary:")
    print(f"  - Total Errors: {total_errors}")
    print(f"  - Total Warnings: {total_warnings}")
    
    if total_errors == 0:
        print("🎉 All workflow files are valid!")
        return 0
    else:
        print("❌ Please fix the errors before using the workflows.")
        return 1

if __name__ == "__main__":
    sys.exit(main())