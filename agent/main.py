import os
import tempfile
import subprocess
from analyzer_llama import analyze_with_llama
from context import step2_analyze_secrets

from llama_cpp import Llama

def clone_repo(git_url):
    temp_dir = tempfile.mkdtemp()
    subprocess.run(["git", "clone", git_url, temp_dir], check=True)
    return temp_dir

if __name__ == "__main__":
    print("[*] Initializing LLaMA model...")
    llm = Llama(model_path="models/Nous-Hermes-2-Mistral-7B-DPO.Q5_K_M.gguf", n_ctx=2048)

    git_urls = [
        "https://github.com/AdamSinale/AI_test_plaintext.git",
        "https://github.com/AdamSinale/AI_test_env.git",
        "https://github.com/AdamSinale/AI_test_log.git",
        "https://github.com/AdamSinale/AI_test_comment.git",
        "https://github.com/AdamSinale/AI_test_unrelated_string.git"
    ]
    for git_url in git_urls:
        repo_path = clone_repo(git_url)

        # שלב 2: מציאת ההקשר של כל סוד והקבצים שמשתמשים בו
        print("[*] Running context analyzer...")
        full_analysis = step2_analyze_secrets(llm, repo_path)

        print("\n[+] Final analysis with LLaMA:\n")
        for idx, entry in enumerate(full_analysis, 1):
            print(f"\n🔐 Secret #{idx}")
            print(f"- Secret: {entry['secret']}")
            print(f"- Variable: {entry['source_var']}")
            print(f"- Defined in: {entry['defined_in']}")
            print(f"- Used in files: {entry['used_in']}")

            print("\n📄 Context:\n")
            print(entry["context"][:1000])  # הצצה לקוד

            # LLaMA analysis
            result = analyze_with_llama(llm, entry["context"], entry["secret"])
            print("\n🤖 LLaMA says:")
            print("Is it safe? : " + str(result["safe"]))
            print("Why? : " + result["reason"])
