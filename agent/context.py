import os
import ast
from collections import defaultdict
from typing import Dict, List, Set

from scanner_regex import extract_secret_candidates_regex
from scanner_llama import extract_secret_candidates_llama


def find_secret_assignments(secret_value: str, repo_path: str) -> List[Dict]:
    """Search all .py files for assignment of the given secret value to a variable."""
    matches = []
    for root, _, files in os.walk(repo_path):
        for file in files:
            if not file.endswith(".py"):
                continue
            full_path = os.path.join(root, file)
            try:
                with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Assign):
                            if isinstance(node.value, ast.Str) and secret_value in node.value.s:
                                for target in node.targets:
                                    if isinstance(target, ast.Name):
                                        matches.append({
                                            "var": target.id,
                                            "file": full_path,
                                            "line": node.lineno
                                        })
            except Exception:
                continue
    return matches


def track_variable_usage(secret_name: str, repo_path: str) -> Set[str]:
    """Track variable usage and propagation across .py files."""
    related_files = set()
    queue = [secret_name]
    seen_vars = set()

    for root, _, files in os.walk(repo_path):
        for file in files:
            if not file.endswith(".py"):
                continue
            full_path = os.path.join(root, file)
            try:
                with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Assign):
                            if isinstance(node.value, ast.Name) and node.value.id in queue:
                                for target in node.targets:
                                    if isinstance(target, ast.Name):
                                        if target.id not in seen_vars:
                                            queue.append(target.id)
                                            seen_vars.add(target.id)
                                        related_files.add(full_path)
                        elif isinstance(node, ast.Name) and node.id in queue:
                            related_files.add(full_path)
            except Exception:
                continue
    return related_files


def collect_related_code(files: Set[str]) -> str:
    """Concatenate the content of all related files into one text block."""
    combined_code = ""
    for file_path in sorted(files):
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                combined_code += f"\n=== {os.path.basename(file_path)} ===\n"
                combined_code += f.read()
        except Exception:
            continue
    return combined_code


def step2_analyze_secrets(repo_path: str):
    all_results = []

    for root, _, files in os.walk(repo_path):
        for file in files:
            if file.endswith(".py"):
                full_path = os.path.join(root, file)
                try:
                    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        secrets = extract_secret_candidates_regex(full_path, content)
                        secrets += extract_secret_candidates_llama(full_path, content)

                        for s in secrets:
                            secret_val = s["value"]
                            assignments = find_secret_assignments(secret_val, repo_path)

                            for assign in assignments:
                                secret_var = assign["var"]
                                defining_file = assign["file"]

                                related_files = track_variable_usage(secret_var, repo_path)
                                related_files.add(defining_file)

                                code_context = collect_related_code(related_files)

                                all_results.append({
                                    "secret": secret_val,
                                    "source_var": secret_var,
                                    "defined_in": defining_file,
                                    "used_in": list(related_files),
                                    "context": code_context
                                })
                except Exception:
                    continue

    return all_results
