# Как выложить сайт на GitHub и Vercel

## Что заливать в GitHub

Заливайте содержимое папки:

```text
C:\Users\User\Documents\New project\logoped-assistant
```

В репозитории должны быть:

- `index.html`
- `api/generate.py`
- `cards/`
- `audio/`
- `vercel.json`
- `.env.example`
- `.gitignore`
- `README.md`

Не загружайте:

- `.env`
- `.vercel/`
- `__pycache__/`
- файлы `*.log`

Они уже добавлены в `.gitignore`.

## Как подключить Vercel

1. Создайте GitHub-репозиторий на аккаунте клиентки.
2. Загрузите туда файлы проекта.
3. Откройте Vercel.
4. Нажмите `Add New Project`.
5. Выберите этот GitHub-репозиторий.
6. Framework Preset можно оставить `Other`.
7. Нажмите `Deploy`.

## Где добавить OpenAI ключ

В Vercel откройте проект:

```text
Settings -> Environment Variables
```

Добавьте:

```text
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-5.4
```

После добавления переменных нажмите:

```text
Deployments -> Redeploy
```

## Важно

OpenAI ключ нельзя писать в `index.html` и нельзя загружать в GitHub.

GitHub хранит файлы сайта, Vercel хранит секретный ключ и запускает backend.

Клиентка будет пользоваться обычной ссылкой Vercel, без Python и без `.exe`.
