from llama_cpp import Llama

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
        response = llm(
            prompt=prompt,
            stop=["\n\n"],  # stop at double newline
            temperature=0.2
        )
        return response["choices"][0]["text"].strip()
    except Exception as e:
        return f"LLM error: {e}"
