import os
import tempfile
import subprocess
from pathlib import Path

from scanner_regex import extract_secret_candidates_regex
from scanner_llama import extract_secret_candidates_llama
from context_llama import step2_analyze_secrets

def clone_repo(git_url):
    temp_dir = tempfile.mkdtemp()
    subprocess.run(["git", "clone", git_url, temp_dir], check=True)
    return temp_dir

def scan_all_files(repo_path):
    all_results = []
    for file_path in Path(repo_path).rglob("*"):
        if file_path.suffix in [".py", ".js", ".java", ".ts", ".go", ".rb", ".cpp", ".cs", ".php"]:
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    regex_res = extract_secret_candidates_regex(str(file_path), content)
                    llama_res = extract_secret_candidates_llama(str(file_path), content)
                    all_results.extend(regex_res + llama_res)
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
    return all_results

def deduplicate_results(results):
    seen = set()
    deduped = []
    for item in results:
        key = (item["file"], item["line"], item["value"])
        if key not in seen:
            seen.add(key)
            deduped.append(item)
    return deduped

if __name__ == "__main__":
    git_url = "https://github.com/AdamSinale/AI_test_env.git"
    repo_path = clone_repo(git_url)
    raw_results = scan_all_files(repo_path)
    final_results = deduplicate_results(raw_results)

    full_analysis = step2_analyze_secrets(repo_path)

    print("\n[+] Potential secrets found:\n")
    for r in final_results:
        print(f"- {r['value']} (line {r['line']} in {r['file']}, source: {r['source']})")
