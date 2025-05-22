import os
import ast
from collections import defaultdict
from typing import Dict, List, Set
import subprocess

from pyparsing import empty

from scanner_regex import extract_secret_candidates_regex
from scanner_llama import extract_secret_candidates_llama

def extract_variable_assignments_from_file(file_path: str, secret_val: str) -> Set[str]:
    vars_found = set()
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    if isinstance(node.value, ast.Str) and secret_val in node.value.s:
                        for target in node.targets:
                            if isinstance(target, ast.Name):
                                vars_found.add(target.id)
    except: pass
    return vars_found
import os
import ast
from typing import Set

def recursive_variable_propagation(defining_file: str, start_vars: Set[str], repo_path: str) -> Set[str]:
    related_files = set()
    seen_vars = set(start_vars)
    queue = list(start_vars)
    called_functions = set()
    max_depth = 10
    for depth in range(max_depth):
        new_vars = set()
        for root, _, files in os.walk(repo_path):
            for file in files:
                if not file.endswith(".py"): continue
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        tree = ast.parse(content)
                        file_used = False
                        for node in ast.walk(tree):
                            if isinstance(node, ast.Assign):
                                if isinstance(node.value, ast.Name) and node.value.id in queue:
                                    for target in node.targets:
                                        if isinstance(target, ast.Name):
                                            var_name = target.id
                                            if var_name not in seen_vars:
                                                new_vars.add(var_name)
                                                seen_vars.add(var_name)
                                                file_used = True
                            elif isinstance(node, ast.Name):
                                if node.id in queue:
                                    file_used = True
                            elif isinstance(node, ast.Call):
                                for arg in node.args:
                                    if isinstance(arg, ast.Name) and arg.id in queue:
                                        file_used = True
                                        if isinstance(node.func, ast.Name):
                                            called_functions.add(node.func.id)

                        if file_used: related_files.add(file_path)
                except Exception: continue
        if not new_vars: break
        queue.extend(new_vars)
    for root, _, files in os.walk(repo_path):
        for file in files:
            if not file.endswith(".py"): continue
            file_path = os.path.join(root, file)
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    tree = ast.parse(f.read())
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef) and node.name in called_functions:
                            related_files.add(file_path)
                            param_names = {arg.arg for arg in node.args.args}  # Set[str]
                            deeper_files = recursive_variable_propagation(file_path,param_names,repo_path)
                            related_files.update(deeper_files)
            except Exception: continue
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

def find_exposed_secrets(llm,full_path,f):
    content = f.read()
    secrets = extract_secret_candidates_regex(full_path, content)
    llm_results = extract_secret_candidates_llama(llm, full_path, content)
    existing_lines = set(s["line"] for s in secrets)
    for item in llm_results:
        if item["line"] not in set(s["line"] for s in secrets):
            secrets.append(item)
            existing_lines.add(item["line"])
    return secrets

def step2_analyze_secrets(llm,repo_path: str):
    all_results = []
    for root, _, files in os.walk(repo_path):
        for file in files:
            full_path = os.path.join(root, file)
            if is_ignored_by_git(repo_path, full_path): continue
            if not os.path.isfile(full_path): continue
            if not is_text_file(full_path): continue
            try:
                with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                    secrets = find_exposed_secrets(llm,full_path,f)
                    for s in secrets:
                        secret_val = s["value"]
                        defining_file = s["file"]
                        starting_vars = extract_variable_assignments_from_file(defining_file, secret_val)
                        related_files = recursive_variable_propagation(defining_file, starting_vars, repo_path)
                        related_files.add(defining_file)

                        if(is_sub_problem(related_files,all_results)): continue

                        code_context = collect_related_code(related_files)
                        all_results.append({
                            "secret": secret_val,
                            "source_var": ", ".join(starting_vars) if starting_vars else None,
                            "defined_in": defining_file,
                            "used_in": sorted(related_files),
                            "context": code_context
                        })
            except Exception: continue
        return all_results
def is_text_file(path):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            f.read(2048)  # נסה לקרוא קצת
        return True
    except:
        return False
def is_sub_problem(related_files,all_results):
    for existing in all_results:
        if related_files.issubset(set(existing["used_in"])):
             return True
    return False
def is_ignored_by_git(repo_path, filepath):
    try:
        if os.path.basename(filepath) == ".gitignore":
            return True
        result = subprocess.run(
            ["git", "check-ignore", filepath],
            cwd=repo_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True
        )
        return bool(result.stdout.strip())
    except Exception:
        return False
