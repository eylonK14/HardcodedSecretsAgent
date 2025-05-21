import re
import json

def extract_secret_candidates_llama(llm, file_path, file_content):
    escaped_code = json.dumps(file_content)  # זה מבטיח שהקוד יהיה בטוח בתוך prompt

    prompt = f"""[INST] <<SYS>>
You are a static code analysis assistant specialized in detecting *hardcoded secrets*
Your job is to identify values that are:
- sensitive (e.g., API keys, access tokens, passwords, database credentials),
- hardcoded directly in the source code,
- and should not be committed to a Git repository.

⚠️ DO NOT return values that are general string literals or clearly non-sensitive values

Your analysis should ONLY include values that match the characteristics of real secrets.

Format your response strictly and ONLY like this:
[OUT]
[{{"value": "<secret>", "line": <line_number>}}, ...]
[/OUT]

The code to analyze is from the file `{file_path}`:

Code:
{escaped_code}
[/INST]
"""

    try:
        output = llm(prompt=prompt, temperature=0, max_tokens=1024)
        raw = output["choices"][0]["text"]
        match = re.search(r"\[OUT\]\s*(.*?)\s*\[/OUT\]", raw, re.DOTALL)
        if match:
            json_text = match.group(1)
            parsed = eval(json_text)
            return [{"value":item["value"], "line":item["line"], "source":"llm", "file":file_path, "reason":"llm"} for item in parsed]
        else:
            print("[!] No [OUT] block found.")
            return []
    except Exception as e:
        print(f"[!] Failed to get model output: {e}")
        return []