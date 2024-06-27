import json
import math
import random
import time
from enum import Enum
from dataclasses import dataclass
from random import Random
from typing import Dict, ClassVar

from rng.mersenne_rng import MersenneRng
from rng.scram_rng import ScramRng
from schema.pfgschema import PFGSchema
from schema.smoothing import NoneSmoother, AddReduceSmoother


class GameSettings:

    def __init__(self):
        self.use_pfg = True
        self.use_scram = True  # no effect if !use_pfg
        self.smoothing = True  # no effect if !use_pfg


class GameRNG:
    game_settings: GameSettings

    class FakePFG:

        def __init__(self, rate, seed):
            self.rate = rate
            self.inner = Random(seed)

        def next(self) -> bool:
            return self.inner.random() >= self.rate

        def update(self, wins, losses):
            self.rate = wins/losses
            pass

    def __init__(self, rate, seed: int | None = None):
        if rate < 0 or rate > 1:
            raise ValueError("Invalid rate passed")

        p_seed = seed if seed else int(time.time() * 1000)

        self.game_settings = GameRNG.game_settings
        self.rate = rate
        if GameRNG.game_settings.use_pfg:
            self.random = PFGSchema(
                wins=int(rate * 100),
                losses=100,
                inner_generator=ScramRng
                if GameRNG.game_settings.use_scram else MersenneRng,
                smoother=AddReduceSmoother
                if GameRNG.game_settings.smoothing else NoneSmoother)

            if GameRNG.game_settings.use_scram:
                self.random.inner_generator.seed = p_seed
        else:
            self.random = GameRNG.FakePFG(rate=rate, seed=p_seed)

    def update(self, rate):
        self.random.update(int(rate*100), 100)

    def next(self) -> bool:
        return self.random.next()


@dataclass(frozen=True)
class Item:
    class Slot(Enum):
        FISHING_ROD = 0,
        BAIT = 1,
        HAT = 2,
        BOAT = 3,
        CHARM = 4

    name: str
    slot: Slot | str
    fishing_power: float = 0
    rare_bonus: int = 0
    comfort: float = 0 # no effect
    stealth: float = 0 # no effect

    price: float = 0

    items: ClassVar[Dict[str, "Item"]]

    @staticmethod
    def init_items():
        item_dict = json.load(open("demo/item_definitions.json", "r"))
        Item.items = {
            k: Item(**v) for k, v in item_dict.items()
        }

    def __post_init__(self):
        object.__setattr__(self, "slot", Item.Slot[self.slot])


class Player:
    def __init__(self):
        self.money = 0
        self.debt = 10000
        self.items = []
        self.items_slots: Dict[Item.Slot, Item | None] = {
            x: None
            for x in Item.Slot
        }


class EngineState(Enum):
    EXIT = 0,
    FISHING = 1,
    SHOP = 2,
    INVENTORY = 3,
    EVENT = 4


class Engine:
    def __init__(self, settings: GameSettings):
        self.state = EngineState.FISHING
        self.settings = settings

        GameRNG.game_settings = settings

        rng_settings: Dict[str, dict] = {
            "good_event_rng": {
                "rate": 0.50,  # good/bad
            },
            "event_rng": {
                "rate": 0.5,  # event/no event
            },
            "fish_catch": {
                "rate": 0.25  # catch/no catch
            },
            "fish_catch_rare": {
                "rate": 0.25 # rare/not rare
            },
            "economy": {
                "rate": 0.5,  # line go up, line go down
            }
        }

        self.RNGs: Dict[str, GameRNG] = {
            k: GameRNG(**v)
            for k, v in rng_settings.items()
        }

        Item.init_items()

        self.player = Player()
        self.player.items_slots[Item.Slot.FISHING_ROD] = Item.items["stringstick"]

        self.economy_state = 1

        self.shop_items: list[Item] = []

        self.refresh_shop()

    def run(self):
        while self.state != EngineState.EXIT:
            match self.state:
                case EngineState.FISHING:
                    self.fishing()
                    pass
                case EngineState.SHOP:
                    self.shop()
                    pass
                case EngineState.INVENTORY:
                    self.inventory()
                    pass
                case EngineState.EVENT:
                    self.event()
                    pass

    def fishing(self):
        while self.state == EngineState.FISHING:
            print("You are sitting in your boat at the edge of the lake. What do you want to do? (case-insensitive)")
            print("[F] Catch fish")
            print("[S] Go to the store")
            print("[I] Look at inventory")
            print("[P] Pass the day (refresh shop items, forward the economy)")
            print("[T] Go talk to people")
            print("[E] Exit")
            match input().upper():
                case "F":
                    fishing_power = sum([v.fishing_power for k,v in self.player.items_slots.items() if v is not None])
                    rare_chance = sum([v.rare_bonus for k, v in self.player.items_slots.items() if v is not None])
                    self.RNGs["fish_catch"].update(1 / (1 + math.exp(-(fishing_power/100))))
                    if self.RNGs["fish_catch"].next():
                        self.RNGs["fish_catch_rare"].update(1 / (1 + math.exp(-(rare_chance/100))))
                        if self.RNGs["fish_catch_rare"].next():
                            value = random.randint(100, 1000)
                            print(f"You caught a rare fish! You sold it for {value}")
                            self.player.money += value
                        else:
                            value = random.randint(1,150)
                            print(f"You caught a fish. You sould it for {value}")
                            self.player.money += value
                    else:
                        print("You caught nothing.")

                case "S":
                    self.state = EngineState.SHOP
                case "T":
                    self.state = EngineState.EVENT
                case "I":
                    self.state = EngineState.INVENTORY
                case "P":
                    line_go_up = self.RNGs["economy"].next()
                    self.economy_state += 0.1 if line_go_up else -0.1
                    self.refresh_shop()
                case "E":
                    self.state = EngineState.EXIT
                case _:
                    print("Unknown option, try again")

    def refresh_shop(self):
        # this doesn't use PFG because why would you
        self.shop_items = random.choices(list(Item.items.values()), k=10)

    def shop(self):
        while self.state == EngineState.SHOP:
            print("You are in Little Frog Shop. What do you want to?")
            print("[B] Look at what you can buy or buy it")
            print("[S] Look at what you can sell or sell it")
            print("[L] Leave")
            match input().upper():
                case "B":
                    while True:
                        print(f"You have ${self.player.money}. Type number to buy or [B] to go back.")
                        price_map = {}
                        for i in range(len(self.shop_items)):
                            price_map[i] = self.shop_items[i].price * self.economy_state
                            print(f"{i} ----- {self.shop_items[i]}, actual price: {price_map[i]}")
                        choice = input(">> ")
                        if choice == "B":
                            break
                        elif choice.isnumeric() and len(self.shop_items) > 0 and \
                                0 <= int(choice) < len(self.shop_items):
                            i_choice = int(choice)
                            if self.player.money >= price_map[i_choice]:
                                self.player.money -= price_map[i_choice]
                                self.player.items.append(self.shop_items[i_choice])
                                del self.shop_items[i_choice]
                            else:
                                print("You can't afford that")
                        else:
                            print("Unknown option, try again")
                case "S":
                    while True:
                        print("Type number to sell or [B] to go back.")
                        price_map = {}
                        for i in range(len(self.player.items)):
                            price_map[i] = self.player.items[i] * self.economy_state
                            print(f"{i} ----- {self.player.items}, sell for: {price_map[i]}")
                        choice = input(">> ")
                        if choice == "B":
                            break
                        elif choice.isnumeric() and len(self.player.items) > 0 and \
                                0 <= int(choice) < len(self.player.items):
                            i_choice = int(choice)
                            self.player.money += price_map[i_choice]
                            self.shop_items.append(self.player.items[i_choice])
                            del self.player.items[i_choice]
                case "L":
                    self.state = EngineState.FISHING
                case _:
                    print("Unknown option, try again")

    def inventory(self):
        while self.state == EngineState.INVENTORY:
            print("You are looking at your storage. What do you want to do?")
            print("[I] Show information about your inventory or equip items")
            print("[E] Show information about your equipped items or unequip them")
            print("[L] Leave your storage")
            match input().upper():
                case "I":
                    while True:
                        print("Type number to equip or [B] to go back")
                        for i in range(len(self.player.items)):
                            print(f"{i} ----- {self.player.items[i]}")
                        choice = input(">> ")
                        if choice == "B":
                            break
                        elif choice.isnumeric() and len(self.player.items) > 0 and \
                                0 <= int(choice) < len(self.player.items):
                            to_equip: Item = self.player.items[int(choice)]
                            equipped = self.player.items_slots[to_equip.slot]
                            if equipped is not None:
                                self.player.items.append(equipped)
                            self.player.items_slots[to_equip.slot] = to_equip
                            del self.player.items[int(choice)]
                case "E":
                    while True:
                        mapping = {}
                        print("Type number to unequip or [B] to go back")
                        for i, x in enumerate(self.player.items_slots):
                            print(f"{i} ----- (slot: {x.name.lower()}) {self.player.items_slots[x]}")
                            mapping[i] = x
                        choice = input(">> ")
                        if choice == "B":
                            break
                        elif choice.isnumeric() and int(choice) in mapping.keys():
                            print(self.player.items_slots)
                            self.player.items.append(self.player.items_slots[mapping[int(choice)]])
                            self.player.items_slots[mapping[int(choice)]] = None
                        else:
                            print("Unknown option, try again")
                case "L":
                    self.state = EngineState.FISHING
                case _:
                    print("Unknown option, try again")

    def event(self):
        is_event = self.RNGs["event_rng"].next()
        if not is_event:
            self.state = EngineState.FISHING
            print("Nothing interesting happened")
            return

        if self.RNGs["good_event_rng"].next() or self.player.debt == 0:
            print("You met a guy who owed you money. You got $50.")
            self.player.money += 50
        else:
            print("You met a bank representative. He took a part of your debt from you - 25$.")
            if self.player.money >= 25:
                self.player.money -= 25
                self.player.debt -= 25
            else:
                print("You cannot afford the debt! You are taken to jail and you cannot fish ever again.")
                self.state = EngineState.EXIT
                return

        self.state = EngineState.FISHING
