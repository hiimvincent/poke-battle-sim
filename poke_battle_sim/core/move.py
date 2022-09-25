from __future__ import annotations

import poke_battle_sim.conf.global_settings as gs


class Move:
    def __init__(self, move_data: list):
        self.md = move_data
        self.id = move_data[gs.MOVE_ID]
        self.name = move_data[gs.MOVE_NAME]
        self.type = move_data[gs.MOVE_TYPE]
        self.o_power = move_data[gs.MOVE_POWER]
        self.power = move_data[gs.MOVE_POWER]
        self.max_pp = move_data[gs.MOVE_PP]
        self.acc = move_data[gs.MOVE_ACC]
        self.prio = move_data[gs.MOVE_PRIORITY]
        self.target = move_data[gs.MOVE_TARGET]
        self.category = move_data[gs.MOVE_CATEGORY]
        self.ef_id = move_data[gs.MOVE_EFFECT_ID]
        self.ef_chance = move_data[gs.MOVE_EFFECT_CHANCE]
        self.ef_amount = move_data[gs.MOVE_EFFECT_AMT]
        self.ef_stat = move_data[gs.MOVE_EFFECT_STAT]
        self.cur_pp = self.max_pp
        self.pos = None
        self.disabled = 0
        self.encore_blocked = False

    def reset(self):
        self.cur_pp = self.max_pp
        self.pos = None
        self.disabled = 0
        self.encore_blocked = False
        self.power = self.md[gs.MOVE_POWER]
        self.max_pp = self.md[gs.MOVE_PP]
        self.acc = self.md[gs.MOVE_ACC]
        self.prio = self.md[gs.MOVE_PRIORITY]
        self.category = self.md[gs.MOVE_CATEGORY]
        self.ef_id = self.md[gs.MOVE_EFFECT_ID]
        self.ef_chance = self.md[gs.MOVE_EFFECT_CHANCE]
        self.ef_amount = self.md[gs.MOVE_EFFECT_AMT]
        self.ef_stat = self.md[gs.MOVE_EFFECT_STAT]

    def get_tcopy(self) -> Move:
        copy = Move(self.md)
        copy.ef_id = self.ef_id
        copy.ef_amount = self.ef_amount
        copy.ef_stat = self.ef_stat
        copy.cur_pp = self.cur_pp
        copy.pos = self.pos
        copy.disabled = self.disabled
        return copy
