import time
import json
import requests
import config

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

def call_llm_json(prompt: str, system_prompt: str="") -> dict:
    """Call LLM and parse the response as JSON."""
    text = call_llm(prompt, system_prompt)
    # Strip markdown code fences if LLM wraps response in ```json ... ```
    text = text.strip().removeprefix("```json").removesuffix("```").strip()
    return json.loads(text)