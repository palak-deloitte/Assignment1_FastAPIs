# Assignment 1: FastAPI Microservice

A FastAPI microservice that wraps two external APIs (weather and jokes) and exposes an authenticated LLM text-summary endpoint.

## Endpoints

| Method | Path                   | Description                   | Auth               |
| ------ | ---------------------- | ----------------------------- | ------------------ |
| GET    | `/weather?city=<name>` | Current weather for a city    | None               |
| GET    | `/joke`                | Random joke                   | None               |
| POST   | `/summary`             | LLM summary of the given text | `X-API-Key` header |

### Status codes

| Endpoint   | Code | When                                                  |
| ---------- | ---- | ----------------------------------------------------- |
| `/weather` | 200  | Success                                               |
|            | 404  | City not found                                        |
|            | 422  | `city` parameter missing                              |
|            | 502  | Weather API unreachable or failing                    |
| `/joke`    | 200  | Success                                               |
|            | 502  | Joke API unreachable or failing                       |
| `/summary` | 200  | Success                                               |
|            | 400  | `text` empty, missing, or longer than 5000 characters |
|            | 401  | `X-API-Key` missing or invalid                        |
|            | 502  | LLM provider failed (including rate limits)           |

### Example responses

`GET /weather?city=London`

```json
{
  "city": "London",
  "temperature": 14.2,
  "condition": "overcast clouds",
  "humidity": 81
}
```

`GET /joke`

```json
{ "joke": "...", "category": "Misc" }
```

`POST /summary` with body `{"text": "..."}` and header `X-API-Key: <your key>`

```json
{ "summary": "..." }
```

## Design decisions

- **LLM provider:** Groq, model 'openai/gpt-oss-20b'. The model name is configurable through the `GROQ_MODEL` environment variable.
- **Summary style:** 2 to 3 concise sentences, generated at temperature 0.3 for consistent output.
- **Maximum input length:** 5000 characters (`MAX_TEXT_LENGTH` in `app/config.py`). Longer input returns 400.
- **Authentication:** `/summary` requires an `X-API-Key` header, compared against `SERVICE_API_KEY` using a constant-time comparison. Auth is checked before the body is validated, so unauthenticated callers get 401 regardless of the body.
- **Prompt handling:** user text is wrapped in `<text>` tags and the system prompt tells the model to treat it only as material to summarize, to reduce prompt injection.
- **Error handling:** service functions raise `CityNotFound` or `UpstreamError`. Only the route layer decides HTTP status codes.
- **Timeouts:** upstream HTTP calls use a 5 second timeout, and the LLM call uses 15 seconds.
- **Safe jokes:** the joke API is called with `safe-mode` enabled.
- **Logging:** upstream failures are logged with the error type and message. API keys and user text are never logged.
- **Secrets:** all keys are loaded from environment variables (`.env`), which is git-ignored.

## Setup

Requires Python 3.12.

```bash
python -m venv venv
venv\Scripts\activate            # Windows
# source venv/bin/activate       # macOS / Linux
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in the values:

| Variable              | Description                                            |
| --------------------- | ------------------------------------------------------ |
| `OPENWEATHER_API_KEY` | Key from openweathermap.org                            |
| `GROQ_API_KEY`        | Key from console.groq.com                              |
| `GROQ_MODEL`          | Groq chat model ID                                     |
| `SERVICE_API_KEY`     | Any long random string; clients send it as `X-API-Key` |

Generate a service key with:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Run

```bash
uvicorn app.main:app --reload
```

Interactive docs: http://127.0.0.1:8000/docs

## Tests

```bash
python -m pytest -v
```

External services are mocked, so tests run offline and do not use any API quota.

## Project structure

```
app/
  main.py       routes and request/response models
  services.py   calls to the weather, joke and LLM APIs
  auth.py       X-API-Key dependency
  config.py     settings loaded from .env
tests/
  test_api.py   endpoint tests (mocked upstream services)
```

## Notes and limitations

- Free-tier LLM limits apply, so heavy use may return 502 when the provider rate-limits requests.
- The service does not cache responses or rate-limit callers.
