import re
import json

def extract_secret_candidates_llama(llm, file_path, file_content):
    escaped_code = json.dumps(file_content)  # זה מבטיח שהקוד יהיה בטוח בתוך prompt

    prompt = f"""[INST] <<SYS>>
    You are a static code analysis assistant specialized in detecting *secrets* (e.g., API keys, tokens, credentials) and analyzing whether they are *used securely*.

    You must:
    1. Identify sensitive values (e.g., keys, tokens, passwords) appearing in the code (including in comments),
    2. Determine whether they are:
       - hardcoded directly in the code,
       - logged (e.g., via print or log functions),
       - written to disk,
       - sent over the network.

    Only include values that meet all of the following:
    - The value is sensitive in nature (e.g., real credentials, tokens, API keys).
    - The value is **not** a generic or meaningless string like "hello", "safeString", or "notApiButRegularString".
    - The value is either **hardcoded** (i.e., directly written as a string literal), or **used unsafely** as described above.

    🛑 DO NOT flag:
    - Values loaded securely from environment variables (e.g., `os.getenv()`).
    - Parameters passed to functions unless their value is clearly hardcoded or used unsafely.
    - Any string that appears only in print/log/debug lines and is clearly non-sensitive.

    ✅ You may include values from comments or assignments if they are unsafe.
    
    Any response that includes a variable name like "VAL" or "API_KEY" instead of a real secret value will be considered invalid.
    Respond strictly and **ONLY** with valid JSON inside this block:
    [OUT]
    [{{"value": "<secret>", "line": <line_number>, "unsafe_usage": true or false, "reason": "..." }}, ...]
    [/OUT]

    ⚠️ If your response contains anything outside this block — it will be ignored.

    The code to analyze is from `{file_path}`:

    Code:
    {escaped_code}
    [/INST]
    """

    try:
        output = llm(prompt=prompt, temperature=0, max_tokens=1024)
        raw = output["choices"][0]["text"]
        json_match = re.search(r'(\[\s*\{.*?\}\s*\])', raw, re.DOTALL)
        if json_match:
            json_text = json_match.group(1)
            try:
                parsed = json.loads(json_text)
                return [{"value": item["value"],"line": item["line"],"source": "llm","file": file_path,"reason": "llm"} for item in parsed if item.get("unsafe_usage")]
            except json.JSONDecodeError as e:
                print(f"[!] JSON decode error: {e}")
                return []
        else:
            print("[!] No JSON array found in output.")
            return []

    except Exception as e:
        print(f"[!] Failed to get model output: {e}")
        return []