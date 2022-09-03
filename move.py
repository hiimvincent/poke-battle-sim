from __future__ import annotations

MOVE_ID = 0
MOVE_NAME = 1
MOVE_TYPE = 3
MOVE_POWER = 4
MOVE_PP = 5
MOVE_ACC = 6
MOVE_PRIORITY = 7
MOVE_TARGET = 8
MOVE_CATEGORY = 9
MOVE_EFFECT_ID = 10
MOVE_EFFECT_CHANCE = 11
MOVE_EFFECT_AMT = 12
MOVE_EFFECT_STAT = 13

class Move:
    def __init__(self, move_data: list):
        self.md = move_data
        self.id = move_data[MOVE_ID]
        self.name = move_data[MOVE_NAME]
        self.type = move_data[MOVE_TYPE]
        self.o_power = move_data[MOVE_POWER]
        self.power = move_data[MOVE_POWER]
        self.max_pp = move_data[MOVE_PP]
        self.acc = move_data[MOVE_ACC]
        self.prio = move_data[MOVE_PRIORITY]
        self.target = move_data[MOVE_TARGET]
        self.category = move_data[MOVE_CATEGORY]
        self.ef_id = move_data[MOVE_EFFECT_ID]
        self.ef_chance = move_data[MOVE_EFFECT_CHANCE]
        self.ef_amount = move_data[MOVE_EFFECT_AMT]
        self.ef_stat = move_data[MOVE_EFFECT_STAT]
        self.cur_pp = self.max_pp
        self.pos = None
        self.disabled = 0

    def reset(self):
        self.cur_pp = self.max_pp
        self.pos = None
        self.disabled = 0
        self.power = self.md[MOVE_POWER]
        self.max_pp = self.md[MOVE_PP]
        self.acc = self.md[MOVE_ACC]
        self.prio = self.md[MOVE_PRIORITY]
        self.category = self.md[MOVE_CATEGORY]
        self.ef_id = self.md[MOVE_EFFECT_ID]
        self.ef_chance = self.md[MOVE_EFFECT_CHANCE]
        self.ef_amount = self.md[MOVE_EFFECT_AMT]
        self.ef_stat = self.md[MOVE_EFFECT_STAT]

    def get_tcopy(self) -> Move:
        copy = Move(self.md)
        copy.ef_id = self.ef_id
        copy.ef_amount = self.ef_amount
        copy.ef_stat = self.ef_stat
        copy.cur_pp = self.cur_pp
        copy.pos = self.pos
        copy.disabled = self.disabled
        return copy
