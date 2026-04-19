import time
import json
import requests
import config
import re

_last_call_time = 0

def call_llm(prompt: str, system_prompt: str = "") -> str:
    """Send a prompt to the configured LLM. Rate-limited to 35 RPM."""
    global _last_call_time

    # Enforce 1.75s gap between calls (35 RPM safety)
    elapsed = time.time() - _last_call_time
    if elapsed < 1.75:
        time.sleep(1.75 - elapsed)

    headers = {
        "Authorization": f"Bearer {config.LLM_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": config.LLM_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.1,  # Low temp = more deterministic output
        "max_tokens": 1024,
    }

    response = requests.post(
        config.LLM_ENDPOINT,
        headers=headers,
        json=payload
        )
    _last_call_time = time.time()
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

# def call_llm_json(prompt: str, system_prompt: str="") -> dict:
#     """Call LLM and parse the response as JSON."""
#     text = call_llm(prompt, system_prompt)
#     # Strip markdown code fences if LLM wraps response in ```json ... ```
#     # text = text.strip().removeprefix("```json").removesuffix("```").strip()
#     text = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
#     return json.loads(text)

def call_llm_json(prompt: str, system_prompt: str = "") -> dict:
    """Call LLM and parse the response as JSON."""
    text = call_llm(prompt, system_prompt)
    # print("RAW LLM RESPONSE:", repr(text))

    cleaned = (
        text.strip()
        .removeprefix("```json")
        .removeprefix("```")
        .removesuffix("```")
        .strip()
    )

    if not cleaned:
        raise ValueError("LLM returned empty content.")

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise