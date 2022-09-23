from __future__ import annotations
import pokemon as pk
import battle as bt
import global_settings as gs
import global_data as gd
import process_item as pi

class Trainer:
    def __init__(self, name: str, poke_list: list[pk.Pokemon], selection: callable = None):
        if not isinstance(poke_list, list) or not all([isinstance(p, pk.Pokemon) for p in poke_list]):
            raise Exception
        if len(poke_list) < gs.POKE_NUM_MIN or len(poke_list) > gs.POKE_NUM_MAX:
            raise Exception
        if not name or not isinstance(name, str):
            raise Exception
        if selection and not isinstance(selection, callable):
            raise Exception
        self.selection = selection
        self.name = name
        self.poke_list = poke_list
        for poke in self.poke_list:
            poke.trainer = self
        self.in_battle = False

    def start_pokemon(self, battle: bt.Battle):
        for poke in self.poke_list:
            poke.start_battle(battle)
        self.current_poke = self.poke_list[0]
        self.light_screen = 0
        self.safeguard = 0
        self.reflect = 0
        self.mist = 0
        self.stealth_rock = 0
        self.fs_dmg = 0
        self.fs_count = 0
        self.dd_dmg = 0
        self.dd_count = 0
        self.tailwind_count = 0
        self.wish = 0
        self.lucky_chant = 0
        self.spikes = 0
        self.toxic_spikes = 0
        self.num_fainted = 0
        self.wish_poke = None
        self.imprisoned_poke = None
        self.in_battle = False
        self.has_moved = False

    def is_valid_action(self, action: list[str]) -> bool:
        if not isinstance(action, list) or len(action) < 2:
            return False
        if action[gs.ACTION_TYPE] == gd.MOVE:
            return self.can_use_move(action)
        if action == gd.SWITCH:
            return self.can_switch_out()
        if action[gs.ACTION_TYPE] == gd.ITEM:
            return can_use_move(action)
        return False

    def can_switch_out(self) -> bool:
        return self.current_poke.can_switch_out()

    def can_use_item(self, item_action: list[str]) -> bool:
        if not isinstance(item_action, list) or not isinstance(item_action[gs.ACTION_TYPE], str) or item_action[gs.ACTION_TYPE] != 'item':
            return False
        if len(item_action) == 3:
            return pi.can_use_item(self, battle, item_action[gs.ACTION_VALUE], item_action[gs.ITEM_TARGET_POS])
        elif len(item_action) == 4:
            return pi.can_use_item(self, battle, item_action[gs.ACTION_VALUE], item_action[gs.ITEM_TARGET_POS], item_action[gs.MOVE_TARGET_POS])
        return False

    def can_use_move(self, move_action: list[str]) -> bool:
        if not isinstance(item_action, list) or not isinstance(item_action[gs.ACTION_TYPE], str) or item_action[gs.ACTION_TYPE] != 'move':
            return False
        if len(move_action) == 2:
            return any([move_action[gs.ACTION_VALUE] == move.name for move in self.current_poke.get_available_moves()])
        return False