# Логопедке арналған ЖИ ассистент

Веб-қосымша логопедке арналған карточкалармен жұмыс істеуге көмектеседі.

## Құрылымы

- `index.html` - негізгі интерфейс.
- `cards/` - карточка суреттері.
- `audio/` - сәлемдесу және мадақтау аудиосы.
- `api/generate.py` - Vercel-дегі OpenAI backend функциясы.
- `server.py` - жергілікті компьютерде тексеруге арналған локал сервер.

## Vercel-ге орнату

1. Репозиторийді GitHub-қа жүктеңіз.
2. Vercel ішінде `Add New Project` таңдаңыз.
3. GitHub репозиторийін қосыңыз.
4. `Settings -> Environment Variables` бөліміне мыналарды қосыңыз:
   - `OPENAI_API_KEY` - клиенттің OpenAI API кілті.
   - `OPENAI_MODEL` - мысалы, `gpt-4o`.
5. `Deploy` басыңыз.

`.env` файлын GitHub-қа жүктемеңіз. Ол `.gitignore` ішінде жабылған.

## Локал тексеру

Компьютерде Python болса:

```powershell
python server.py
```

Содан кейін браузерде ашыңыз:

```text
http://127.0.0.1:8000/
```

## Карточкаларды өзгерту

Жаңа суреттерді `cards/` ішіне бұрынғы атау үлгісімен салыңыз:

- `plot1.jpeg`, `plot2.jpeg`
- `story1.jpeg`, `story2.jpeg`
- `yes_no1.jpeg`
- `actions1.jpeg`
- `because1.jpeg`
- `sentence1.jpeg`
- `option1.jpeg`
- `request1.jpeg`

Саны өзгерсе, `index.html` ішіндегі `CARD_TYPES` бөліміндегі `count` мәнін өзгертіңіз.
