from __future__ import annotations

import base64
import json
import mimetypes
import os
import urllib.error
import urllib.request
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
from pathlib import Path
from typing import Any


ROOT = Path.cwd()
MODEL = os.environ.get("OPENAI_MODEL", "gpt-5.4")


def write_json(handler: BaseHTTPRequestHandler, status: int, payload: dict[str, Any]) -> None:
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


def communicative_result() -> dict[str, Any]:
    return {
        "instructor": (
            "Карточкадағы дайын сұрақтарды қолданыңыз. ОНР 1 деңгейінде бір сөзді, "
            "көрсетуді немесе иә/жоқ жауабын қабылдаңыз. ОНР 2 деңгейінде жауапты "
            "қысқа сөйлемге дейін кеңейтіңіз."
        ),
        "onr1": [],
        "onr2": [],
    }


def ask_openai(card: dict[str, Any], system_prompt: str) -> dict[str, Any]:
    if card.get("section") == "communicative":
        return communicative_result()

    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY Vercel Environment Variables ішінде табылмады.")

    image_url = card_image_data_url(card)
    user_text = (
        f"Карточка атауы: {card.get('label', '')}. "
        f"Бөлім: {card.get('sectionTitle', '')}. "
        f"Сұрақ түрі: {card.get('typeTitle', '')}. "
        "ОНР 1 және ОНР 2 үшін сұрақтар дайында."
    )

    payload = {
        "model": MODEL,
        "max_completion_tokens": 1200,
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

    content = data["choices"][0]["message"]["content"]
    content = content.replace("```json", "").replace("```", "").strip()
    return json.loads(content)


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self) -> None:
        self.send_response(HTTPStatus.NO_CONTENT)
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self) -> None:
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            result = ask_openai(payload["card"], payload.get("systemPrompt", ""))
            write_json(self, HTTPStatus.OK, {"result": result})
        except Exception as exc:
            write_json(self, HTTPStatus.BAD_REQUEST, {"error": str(exc)})
