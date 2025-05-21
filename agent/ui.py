import re
import math
import pandas as pd

def shannon_entropy(data):
    if not data:
        return 0
    entropy = 0
    for x in set(data):
        p_x = data.count(x) / len(data)
        entropy += - p_x * math.log2(p_x)
    return entropy

def load_regex_patterns_from_excel(filepath="APIregex.xlsx"):
    df = pd.read_excel(filepath)
    regex_dict = {}
    for _, row in df.iterrows():
        name = str(row["Secret Type"]).strip()
        pattern = str(row["Regex"]).strip()
        if name and pattern:
            regex_dict[name] = pattern
    return regex_dict

regex_patterns = load_regex_patterns_from_excel()

def extract_secret_candidates_regex(file_path, file_content):
    results = []

    for line_num, line in enumerate(file_content.splitlines(), 1):
        matched_regex = False
        for name, pattern in regex_patterns.items():
            try:
                for match in re.findall(pattern, line):
                    results.append({
                        "value": match,
                        "line": line_num,
                        "source": "regex",
                        "reason": name,
                        "file": file_path
                    })
                    matched_regex = True
                    break
            except re.error: print(f"Invalid regex pattern for {name}: {pattern}")
            if matched_regex: break
    return results
