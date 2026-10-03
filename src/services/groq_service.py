import json
from src.config import secret, GROQ_MODEL

def available():
    return bool(secret("GROQ_API_KEY"))

def _client():
    if not available():
        return None
    from groq import Groq
    return Groq(api_key=secret("GROQ_API_KEY"))

def ask_json(system_prompt, user_prompt, max_tokens=650):
    client=_client()
    if client is None:
        return {"summary":"Groq is not configured. Deterministic TenderPulse checks are still available.","requirements":[],"risks":[]}
    try:
        response=client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role":"system","content":system_prompt},
                {"role":"user","content":user_prompt},
            ],
            temperature=0.1,
            max_tokens=max_tokens,
            response_format={"type":"json_object"},
        )
        text=response.choices[0].message.content or "{}"
        data=json.loads(text)
        return data if isinstance(data,dict) else {"summary":str(data)}
    except Exception as exc:
        return {"summary":f"AI analysis unavailable: {exc}","requirements":[],"risks":[]}

def analyze_tender(*args, **kwargs):
    system_prompt=kwargs.pop("system_prompt","You are TenderPulse AI. Return concise valid JSON.")
    user_prompt="\n".join(str(x) for x in args) if args else str(kwargs)
    return ask_json(system_prompt,user_prompt)
