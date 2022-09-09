from __future__ import annotations
import pokemon as pk
import battle as bt

POKE_NUM_MIN, POKE_NUM_MAX = 1, 6

class Trainer:
    def __init__(self, name: str, poke_list: [pk.Pokemon], selection: callable = None):
        if not isinstance(poke_list, list) or not all([isinstance(p, pk.Pokemon) for p in poke_list]):
            raise Exception
        if len(poke_list) < POKE_NUM_MIN or len(poke_list) > POKE_NUM_MAX:
            raise Exception
        if not name or not isinstance(name, str):
            raise Exception
        if selection and not isinstance(selection, callable):
            raise Exception
        self.selection = selection
        self.name = name
        self.poke_list = poke_list
        self.in_battle = False

    def start_pokemon(self, battle: bt.Battle):
        for poke in self.poke_list:
            poke.start_battle(battle)
            poke.trainer = self
        self.current_poke = self.poke_list[0]
        self.light_screen = 0
        self.safeguard = 0
        self.reflect = 0
        self.fs_dmg = 0
        self.fs_count = 0
        self.dd_dmg = 0
        self.dd_count = 0
        self.wish = 0
        self.spikes = 0
        self.num_fainted = 0
        self.wish_poke = None
        self.imprisoned_poke = None
        self.in_battle = False
        self.has_moved = False

