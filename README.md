# Rock Paper Scissors Game

## Instructions

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

uvicorn app.main:app --host 0.0.0.0 --port 8080
```

## Stack

I used uvicorn + FastAPI for the backend, and simple JS + HTML + Bulma
CSS for the frontend.

## Accomplished

I was able to get the backend mostly done and added the initial page for
the frontend. A game is able to be created, saved, and loaded. A basic
game page exists, but just notifies the player of who is playing. If the
player 2 field is left blank, a player named CPUPlayer is created.

## Further Improvements

If given more time, I would have liked to explore creating the full game
UI and revise my design as needed. The main game would have been played
on the frontend, with just the score being tracked on the backend. This
is the design I went with, so no game logic actually exists.

I thought it would have been cool to use websockets and allow a player
to use a game code from a separate window or computer on the same
network to make a simple online multiplayer version. This would be more
fun since the second player wouldn't be able to see the other's screen.

The saving mechanism could be improved with an actual SQL/Mongo or
equivalent server. Pickle is generally unsafe because it can cause
remote code execution vulnerabilities, but it was used to save time.

It was my first time using FastAPI, so there are likely multiple style
and usability improvements that could be utilized with more time.

Better UI outline and arrangement could also be done, but is limited by
my design skills. I would probably enlist a designer to help with that.

I could have added a one time public/private keypair for signing and 
validating the post requests so that you can't just increase your own
score by using fabricated post requests.
