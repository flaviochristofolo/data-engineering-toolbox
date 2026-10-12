"""Cliente mínimo para o Jev (TypeSafe) via OpenRouter.

A chave é lida de OPENROUTER_API_KEY. Se a variável não existir, a requisição
é enviada sem cabeçalho de autorização, o que funciona quando o proxy da
sessão injeta a credencial.
"""

import json
import os
import urllib.request

ENDPOINT = "https://openrouter.ai/api/v1/systemone"
MODEL = "jev-latest"


def evaluate(state, questions, model=MODEL, timeout=60):
    headers = {"Content-Type": "application/json"}
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    body = json.dumps({"model": model, "state": state, "questions": questions}).encode()
    request = urllib.request.Request(ENDPOINT, data=body, headers=headers, method="POST")
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read())


if __name__ == "__main__":
    result = evaluate(
        state="I was charged twice for my subscription.",
        questions={
            "refund": {"type": "noul", "instructions": "Is the customer asking for money back?"},
        },
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
