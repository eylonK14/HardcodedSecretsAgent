# הנחה: llama 7B רץ מקומית עם HuggingFace Transformers או llama.cpp

# אם אתה משתמש ב-llama.cpp:
# pip install llama-cpp-python

from llama_cpp import Llama

llm = Llama(model_path="models/llama-2-7b-chat.ggmlv3.q4_0.bin", n_ctx=2048)

def extract_secret_candidates_llama(file_path, file_content):
    prompt = f"""The following code is from a file called `{file_path}`.
Analyze the code and identify any string literals that may represent hardcoded secrets, like passwords, tokens, API keys, or private keys.

Respond in this exact JSON format:
[{{"value": "<the_secret>", "line": <line_number>}}]

Code:
{file_content}
"""
    output = llm(prompt=prompt, stop=["\n\n"], temperature=0)
    try:
        return [{"value": item["value"], "line": item["line"], "source": "llm", "file": file_path, "reason": "llm"} for item in eval(output["choices"][0]["text"])]
    except:
        return []
