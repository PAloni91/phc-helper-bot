# PHC Helper Bot

A Telegram bot that answers simple health-centre questions in plain language, such as ORS, fever warning signs and basic first aid. It looks up relevant facts in a small knowledge base and asks an LLM (through OpenRouter) to answer using only those facts.

I built it as a small, complete AI/bot project. The design is inspired by a larger public-health supply-chain prototype I worked on, where the main lesson was that the interface must be simple enough for someone with a class-10 education.

## Features
- Answers from a local knowledge base (`knowledge/faq.md`), so replies stay grounded
- Safe by design: the system prompt forbids diagnosis and medicine doses, and always points to 108/112 for emergencies
- Per-user rate limiting (sliding window) to stop spam and control cost
- Input length limit and output token limit, with a clean error if the LLM fails or returns nothing
- All settings from environment variables; the bot fails at startup if a required one is missing
- Unit tests for the rate limiter, retrieval and prompt building

## Project structure
| File | Purpose |
|---|---|
| `bot.py` | Telegram handlers and startup |
| `llm.py` | OpenRouter call, limits, response validation |
| `knowledge.py` | Keyword retrieval over `knowledge/*.md` |
| `rate_limit.py` | Per-user sliding-window limiter |
| `config.py` | Reads and validates environment variables |
| `tests/` | Unit tests (`pytest`) |

## Setup
1. Python 3.10 or newer.
2. Create a bot with [@BotFather](https://t.me/BotFather) on Telegram and copy the token.
3. Get an API key from [OpenRouter](https://openrouter.ai).
4. Install and configure:
   ```bash
   python -m venv .venv
   source .venv/bin/activate        # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   cp .env.example .env             # then edit .env with your token and key
   ```
5. Run the tests and start the bot:
   ```bash
   pytest
   python bot.py
   ```
6. Open your bot in Telegram and send `/start`.

## Customising
Edit or add `.md` files in `knowledge/`. Put each fact in its own paragraph, separated by a blank line. Change the model with `OPENROUTER_MODEL` in `.env`.

## Limitations and next steps
- Retrieval is keyword-based; embeddings would handle spelling and Hindi/Marathi better
- Rate limiting is in memory, so it resets when the bot restarts
- No conversation memory yet (each question is answered on its own)
- Not a medical device. It gives general information only.
