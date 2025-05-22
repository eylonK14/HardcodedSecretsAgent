import os
import tempfile
import subprocess
from analyzer_llama import analyze_with_llama
from context import step2_analyze_secrets
import tkinter as tk

from llama_cpp import Llama

def run_analysis(repo_path, ui):
    print("[*] Initializing LLaMA model...")
    llm = Llama(model_path="models/Nous-Hermes-2-Mistral-7B-DPO.Q5_K_M.gguf", n_ctx=2048)

    print("[*] Running context analyzer...")
    full_analysis = step2_analyze_secrets(llm, repo_path)

    print("\n[+] Final analysis with LLaMA:\n")
    for idx, entry in enumerate(full_analysis, 1):
        ui.insert(tk.END, f"\n🔐 Secret #{idx}\n")
        ui.insert(tk.END, f"- Secret: {entry['secret']}\n")
        ui.insert(tk.END, f"- Variable: {entry['source_var']}\n")
        ui.insert(tk.END, f"- Defined in: {entry['defined_in']}\n")
        ui.insert(tk.END, f"- Used in files: {entry['used_in']}\n\n")
        ui.insert(tk.END, "📄 Context (first 1k chars):\n")
        snippet = entry["context"][:1000].replace("\n", "\n    ")
        ui.insert(tk.END, f"    {snippet}\n\n")

        # LLaMA analysis
        result = analyze_with_llama(llm, entry["context"], entry["secret"])
        ui.insert(tk.END, "🤖 LLaMA says:\n")
        ui.insert(tk.END, f"    {result}\n" + ("-" * 60) + "\n")

if __name__ == "__main__":
    git_urls = [
        "https://github.com/AdamSinale/AI_test_plaintext.git",
        "https://github.com/AdamSinale/AI_test_env.git",
        "https://github.com/AdamSinale/AI_test_log.git",
        "https://github.com/AdamSinale/AI_test_comment.git",
        "https://github.com/AdamSinale/AI_test_unrelated_string.git"
    ]
    for git_url in git_urls:
        run_analysis(git_url)