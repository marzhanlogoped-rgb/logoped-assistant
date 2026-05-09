from __future__ import annotations

import base64
import json
import mimetypes
import os
import urllib.error
import urllib.request
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o")


def load_dotenv() -> None:
    env_path = ROOT / ".env"
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def json_response(handler: SimpleHTTPRequestHandler, status: int, payload: dict[str, Any]) -> None:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def card_image_data_url(card: dict[str, Any]) -> str:
    src = str(card.get("src", ""))
    path = (ROOT / src).resolve()
    cards_root = (ROOT / "cards").resolve()
    if not str(path).startswith(str(cards_root)) or not path.exists():
        raise ValueError("Карточка файлы табылмады.")
    mime = mimetypes.guess_type(path.name)[0] or "image/jpeg"
    data = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{data}"


def ask_openai(card: dict[str, Any], system_prompt: str) -> dict[str, Any]:
    if card.get("section") == "communicative":
        return {
            "instructor": (
                "Карточкадағы дайын сұрақтарды қолданыңыз. ОНР 1 деңгейінде бір сөзді, "
                "көрсетуді немесе иә/жоқ жауабын қабылдаңыз. ОНР 2 деңгейінде жауапты "
                "қысқа сөйлемге дейін кеңейтіңіз."
            ),
            "onr1": [],
            "onr2": [],
        }

    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY табылмады. Оны .env файлына немесе орта айнымалысына қосыңыз.")

    image_url = card_image_data_url(card)
    user_text = (
        f"Карточка атауы: {card.get('label', '')}. "
        f"Бөлім: {card.get('sectionTitle', '')}. "
        f"Сұрақ түрі: {card.get('typeTitle', '')}. "
        "ОНР 1 және ОНР 2 үшін сұрақтар дайында."
    )
    payload = {
        "model": MODEL,
        "max_tokens": 1200,
        "messages": [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": image_url}},
                    {"type": "text", "text": user_text},
                ],
            },
        ],
    }
    request = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        details = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(details) from exc

    content = data["choices"][0]["message"]["content"].replace("```json", "").replace("```", "").strip()
    return json.loads(content)


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_POST(self) -> None:
        if self.path != "/api/generate":
            json_response(self, HTTPStatus.NOT_FOUND, {"error": "Not found"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            result = ask_openai(payload["card"], payload.get("systemPrompt", ""))
            json_response(self, HTTPStatus.OK, {"result": result})
        except Exception as exc:
            json_response(self, HTTPStatus.BAD_REQUEST, {"error": str(exc)})


if __name__ == "__main__":
    load_dotenv()
    port = int(os.environ.get("PORT", "8000"))
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"Open http://127.0.0.1:{port}")
    server.serve_forever()
