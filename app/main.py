import pickle
import os
import string
import random
from uuid import uuid4

from fastapi import FastAPI, Request, status, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="html")


class PlayersInfo(BaseModel):
    player1_name: str
    player2_name: str | None


class GameSaveInfo(BaseModel):
    game_code: str


class IncreaseScoreInfo(BaseModel):
    player_name: str
    game_code: str


class GameURLInfo(BaseModel):
    game_url: str


class PlayerNotFoundError(Exception):
    pass


class GameNotFoundError(Exception):
    pass


class Player:
    def __init__(self, name: str, id=uuid4()):
        self.name = name
        self.id = id
        self.score = 0


class CPUPlayer(Player):
    def __init__(self, id=uuid4()):
        super().__init__("CPUPlayer", id)


class Game:
    """A class to keep track of the score between player 1 and player 2"""

    def __init__(self, code: str, player1: Player, player2: Player):
        self.code = code

        self.players = {player1.name: player1, player2.name: player2}
        self.player1 = player1
        self.player2 = player2

    def get_player(self, player_name: str) -> Player:
        if player_name not in self.players:
            raise PlayerNotFoundError()

        return self.players[player_name]

    def increase_score(self, player_name: str):
        player = self.get_player(player_name)
        player.score += 1

    def set_score(self, player_name: str, score: int):
        player = self.get_player(player_name)
        player.score = score


class GameManager:
    """The game manager controls access to the game object and manages saves"""
    save_path = "saves"
    save_file = "{game_code}.savefile"

    def __init__(self):
        self.games: dict[str, Game] = {}
        self.game_code_index = 0
        self.load_games()

    def load_games(self):
        """Load all saved games from the save path"""
        if not os.path.exists(self.save_path):
            return

        for path in os.listdir(self.save_path):
            if path.endswith(".savefile"):
                # Pickle is not safe and should be replaced with a suitable
                # alternative
                with open(os.path.join(self.save_path, path), "rb") as f:
                    self.games.update(pickle.load(f))

    def get_game(self, game_code: str) -> Game:
        """Get an existing game. If a game is not found, throw an exception"""
        if game_code not in self.games:
            raise GameNotFoundError()
        return self.games[game_code]

    def new_game(self, player1: Player, player2: Player) -> Game:
        """Start a new game in the game manager"""
        code = GAME_CODES[self.game_code_index]
        self.games[code] = Game(code, player1, player2)
        self.game_code_index += 1
        return self.games[code]

    async def save_game(self, game_code: str):
        """Save the game to disk"""
        # ideally, this would be saved to SQL or similar
        # but for the sake of time, just save it to a file
        os.makedirs(self.save_path, exist_ok=True)

        game_filepath = os.path.join(
            self.save_path, self.save_file.format(game_code=game_code)
        )

        # Pickle is not safe and should be replaced with a suitable
        # alternative
        with open(game_filepath, "wb+") as f:
            pickle.dump({game_code: self.get_game(game_code)}, f)


def create_game_codes() -> list[str]:
    """Generate all permutations of all letters for game codes once"""
    codes: list[str] = []

    # Make sure they are random so that people can't predict
    # which games will be taken
    chars1 = list(string.ascii_uppercase)
    random.shuffle(chars1)
    chars2 = list(string.ascii_uppercase)
    random.shuffle(chars2)
    chars3 = list(string.ascii_uppercase)
    random.shuffle(chars3)
    chars4 = list(string.ascii_uppercase)
    random.shuffle(chars4)

    for ch1 in chars1:
        for ch2 in chars2:
            for ch3 in chars3:
                for ch4 in chars4:
                    code = f"{ch1}{ch2}{ch3}{ch4}"
                    if code not in GAME_MANAGER.games:
                        codes.append(code)
    return codes


# Global variables for game state
GAME_MANAGER = GameManager()
GAME_CODES: list[str] = create_game_codes()


@app.post("/save-game", response_class=HTMLResponse, status_code=200)
async def save_game(_: Request, game_save_info: GameSaveInfo, resp: Response):
    """Save the game to reload later"""
    try:
        await GAME_MANAGER.save_game(game_save_info.game_code)
    except GameNotFoundError:
        resp.status_code = status.HTTP_400_BAD_REQUEST


@app.post("/increase-score", response_class=HTMLResponse, status_code=200)
async def increase_score(_: Request, inc_score_info: IncreaseScoreInfo, resp: Response):
    try:
        game = GAME_MANAGER.get_game(inc_score_info.game_code)
        game.increase_score(inc_score_info.player_name)
    except (PlayerNotFoundError, GameNotFoundError):
        resp.status_code = status.HTTP_400_BAD_REQUEST


@app.post("/start-game", response_class=HTMLResponse)
async def start_game(request: Request, players_info: PlayersInfo):
    """Post route for creating the game info"""
    player2 = (
        Player(players_info.player2_name)
        if players_info.player2_name is not None
        else CPUPlayer()
    )

    game = GAME_MANAGER.new_game(Player(players_info.player1_name), player2)

    return JSONResponse(
        content=jsonable_encoder(
            GameURLInfo(game_url=request.url_for("game") + f"?game_code={game.code}")
        )
    )


@app.get("/game", response_class=HTMLResponse)
async def game(request: Request, game_code: str):
    """The main game route. Play the game here"""
    try:
        game = GAME_MANAGER.get_game(game_code)
        return templates.TemplateResponse(
            "game.html", {"request": request, "game": game}
        )
    except GameNotFoundError:
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "message": f"Game {game_code} not found!"},
        )


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """The route to enter information to play the game"""
    return templates.TemplateResponse("index.html", {"request": request})
