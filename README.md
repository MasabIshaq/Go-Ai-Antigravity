# Go Ai

A ChatGPT-style chatbot powered by [OpenRouter](https://openrouter.ai/), built with Python (FastAPI) and a streaming web UI.

## Features

- ChatGPT-like dark UI with sidebar, chat history, and streaming replies
- Markdown and syntax-highlighted code blocks with copy buttons
- Multiple models via OpenRouter (GPT-4o, Claude, Gemini, Llama, DeepSeek, etc.)
- Local chat persistence

## Setup

1. **Get an OpenRouter API key** from [openrouter.ai/keys](https://openrouter.ai/keys).

2. **Install dependencies:**

```bash
cd "Go Ai"
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

3. **Configure environment:**

```bash
copy .env.example .env
```

Edit `.env` and set your `OPENROUTER_API_KEY`.

4. **Run the app:**

```bash
python run.py
```

Open [http://localhost:8000](http://localhost:8000) in your browser.

## Environment variables

| Variable | Description |
|----------|-------------|
| `OPENROUTER_API_KEY` | Your OpenRouter API key (required) |
| `DEFAULT_MODEL` | Default model ID (e.g. `openai/gpt-4o-mini`) |
| `APP_TITLE` | App name shown in the UI |
| `SITE_URL` | URL sent to OpenRouter for attribution |

## Project structure

```
Go Ai/
├── app/
│   ├── main.py        # FastAPI routes
│   ├── openrouter.py  # Streaming API client
│   ├── storage.py     # Chat persistence
│   └── config.py
├── static/
│   ├── index.html
│   ├── css/style.css
│   └── js/app.js
├── data/              # Saved chats (auto-created)
├── run.py
└── requirements.txt
```
