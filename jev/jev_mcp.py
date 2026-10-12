"""Servidor MCP (stdio) que expõe o Jev como ferramenta para o Claude Code.

Sem dependências externas: fala JSON-RPC 2.0 direto pela entrada e saída padrão.
"""

import json
import sys

from jev_client import MODEL, evaluate

PROTOCOL_VERSION = "2024-11-05"

TOOL = {
    "name": "jev_evaluate",
    "description": (
        "Avalia um texto (state) contra perguntas tipadas do Jev. "
        "Tipos: 'noul' (probabilidade de sim), 'choice' (uma opção de criteria) "
        "e 'score' (posição em escala). Retorna probabilidades, não texto."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "state": {"type": "string", "description": "Texto a ser avaliado."},
            "questions": {
                "type": "object",
                "description": "Perguntas por nome. Ex.: {\"refund\": {\"type\": \"noul\", \"instructions\": \"...\"}}",
            },
            "model": {"type": "string", "description": f"Modelo Jev. Padrão: {MODEL}."},
        },
        "required": ["state", "questions"],
    },
}


def respond(request_id, result=None, error=None):
    message = {"jsonrpc": "2.0", "id": request_id}
    if error is not None:
        message["error"] = error
    else:
        message["result"] = result
    sys.stdout.write(json.dumps(message, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def handle(request):
    method = request.get("method")
    request_id = request.get("id")

    if method == "initialize":
        respond(request_id, {
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "jev", "version": "0.1.0"},
        })
    elif method == "tools/list":
        respond(request_id, {"tools": [TOOL]})
    elif method == "tools/call":
        params = request.get("params", {})
        if params.get("name") != TOOL["name"]:
            respond(request_id, error={"code": -32602, "message": "Ferramenta desconhecida"})
            return
        args = params.get("arguments", {})
        try:
            result = evaluate(
                state=args["state"],
                questions=args["questions"],
                model=args.get("model", MODEL),
            )
            respond(request_id, {
                "content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}],
            })
        except Exception as error:
            respond(request_id, {
                "content": [{"type": "text", "text": f"Erro ao chamar o Jev: {error}"}],
                "isError": True,
            })
    elif request_id is not None:
        respond(request_id, error={"code": -32601, "message": f"Método não suportado: {method}"})
    # Notificações (sem id), como notifications/initialized, não exigem resposta.


def main():
    for line in sys.stdin:
        line = line.strip()
        if line:
            handle(json.loads(line))


if __name__ == "__main__":
    main()
