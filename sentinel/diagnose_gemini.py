"""Probe the Gemini API with one fixed synthetic request; never print secrets.

Run in a private shell:
  python -m sentinel.diagnose_gemini
  python -m sentinel.diagnose_gemini --structured
"""
import os
import sys
from .ai import DEFAULT_MODEL, safe_gemini_warning


def main() -> int:
    args = sys.argv[1:]
    if args not in ([], ["--structured"]):
        print("Uso: python -m sentinel.diagnose_gemini [--structured]")
        return 2

    key = os.getenv("GEMINI_API_KEY", "")
    model = os.getenv("GEMINI_MODEL", DEFAULT_MODEL)
    if not key:
        print("GEMINI_API_KEY não configurada nesta sessão.")
        return 2

    try:
        from google import genai
        from google.genai import types

        configuration = None
        if args == ["--structured"]:
            configuration = types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema={
                    "type": "OBJECT",
                    "properties": {
                        "summary": {"type": "STRING"},
                        "suggestions": {"type": "ARRAY", "items": {"type": "STRING"}},
                    },
                    "required": ["summary", "suggestions"],
                },
            )
            prompt = "Exemplo fictício. Responda com summary='Teste concluído' e suggestions=['Exemplo seguro'] em JSON."
        else:
            prompt = "Responda somente OK."

        with genai.Client(api_key=key) as client:
            response = client.models.generate_content(
                model=model, contents=prompt, config=configuration,
            )
        if not response.text:
            print(f"API respondeu, mas sem texto. Modelo: {model}")
            return 1

        print(f"Chamada concluída com sucesso. Modelo: {model}; formato: {'estruturado' if configuration else 'simples'}.")
        return 0
    except Exception as exc:
        print(safe_gemini_warning(exc))
        print(f"Modelo consultado: {model}; formato: {'estruturado' if args else 'simples'}.")
        print("Nenhuma chave ou conteúdo da resposta foi exibido.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
