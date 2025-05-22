from llama_cpp import Llama

def analyze_with_llama(llm: Llama, context: str, secret: str) -> str:
    """
    שולח את הקוד הרלוונטי ל-LLM ומחזיר תשובה האם הסוד בשימוש בטוח.
    """
    prompt = f"""
You are a security expert. A secret with value "{secret}" was detected in the following code.

Your response must meet ALL of the following strict rules:
- Analyze ONLY the code shown between BEGIN CODE and END CODE.
- DO NOT invent or assume the existence of any other files.
- DO NOT generate or include any code.
- DO NOT include explanations or commentary.
- Respond ONLY with valid JSON in the following format:
{{"safe": true or false, "reason": "..." }}

If you cannot determine the answer from the provided code, explain that clearly — but still return a valid JSON object.

=== BEGIN CODE ===
{context}
=== END CODE ===
"""

    try:
        output = llm(prompt=prompt, temperature=0, max_tokens=1024)
        return output["choices"][0]["text"].strip()
    except Exception as e:
        return f"LLM error: {e}"
