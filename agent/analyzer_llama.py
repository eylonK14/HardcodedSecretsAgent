from llama_cpp import Llama
import json

def analyze_with_llama(llm: Llama, context: str, secret: str) -> str:
    """
    שולח את הקוד הרלוונטי ל-LLM ומחזיר תשובה האם הסוד בשימוש בטוח.
    """
    prompt = f"""
You are a security expert. A secret with value "{secret}" was detected in the following code.

Analyze all usages of this secret across the files below and determine:
- Is it used securely?
- Is it printed, logged, or sent over the network?
- Are there any risky or unsafe operations involving it?

Respond strictly in the following JSON format:
{{"safe": true or false, "reason": "..." }}

=== BEGIN CODE ===
{context}
=== END CODE ===
"""

    try:
        output = llm(prompt=prompt, temperature=0, max_tokens=1024)
        text = output["choices"][0]["text"].strip()
        parsed = json.loads(text)
        return parsed
    except Exception as e:
        print(f"[!] LLM error: {e}")
        return {"safe": "unknown", "reason": str(e)}
