from enum import Enum
from typing import Dict

from demo.engine import Engine, GameSettings


class GameState(Enum):
    MENU = 1
    GAME = 2
    SETTINGS = 3
    EXIT = 4


class Game:

    def __init__(self):
        self.state = GameState.MENU
        self.game_settings = GameSettings()

    def run(self):
        while self.state != GameState.EXIT:
            match self.state:
                case GameState.MENU:
                    self.menu()
                case GameState.GAME:
                    self.play_game()
                case GameState.SETTINGS:
                    self.settings()
                case _:
                    pass

    def menu(self):
        while self.state == GameState.MENU:
            print(10 * "=")
            print("~~Fortune Fisher~~")
            print("[P] Play")
            print("[S] Settings")
            print("[E] Exit")
            choice = input(">> ")
            match choice.upper():
                case "P":
                    self.state = GameState.GAME
                case "S":
                    self.state = GameState.SETTINGS
                case "E":
                    self.state = GameState.EXIT
                case _:
                    print("Unknown option, try again")

    def play_game(self):
        engine = Engine(self.game_settings)
        engine.run()
        self.state = GameState.MENU

    def settings(self):
        print(self.state)
        while self.state == GameState.SETTINGS:
            print(10 * "=")
            print("SETTINGS")
            print("Enter number to toggle, or [E] to exit")
            gs_dict = self.game_settings.__dict__
            mapping: Dict[int, str] = {}
            for i, x in enumerate(gs_dict):
                print(f"[{i}]: {x} ----- {gs_dict[x]}")
                mapping[i] = x

            choice = input(">> ")

            if choice == "E":
                self.state = GameState.MENU
            elif choice.isnumeric() and int(choice) in mapping.keys():
                gs_dict[mapping[int(choice)]] ^= True
            else:
                print("Unknown option, try again")


if __name__ == "__main__":
    game = Game()
    game.run()
