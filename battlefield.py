from __future__ import annotations
import battle as bt
import global_settings as gs

class Battlefield:
    def __init__(self, battle: bt.Battle):
        self.weather = gs.CLEAR
        self.acc_modifier = 1
        self.weather_count = 0
        self.gravity_count = 0
        self.trick_room_count = 0
        self.gravity_stats = None
        self.cur_battle = battle

    def update(self):
        if self.weather_count:
            self.weather_count -= 1
            if self.weather_count:
                if self.weather == gs.SANDSTORM:
                    self.cur_battle._add_text('The sandstorm is raging.')
                elif self.weather == gs.RAIN:
                    self.cur_battle._add_text('Rain continues to fall.')
                elif self.weather == gs.HARSH_SUNLIGHT:
                    self.cur_battle._add_text('The sunlight is strong.')
                elif self.weather == gs.HAIL:
                    self.cur_battle._add_text('The hail is crashing down.')
            else:
                if self.weather == gs.SANDSTORM:
                    self.cur_battle._add_text('The sandstorm subsided.')
                elif self.weather == gs.RAIN:
                    self.cur_battle._add_text('The rain stopped.')
                elif self.weather == gs.HARSH_SUNLIGHT:
                    self.cur_battle._add_text('The harsh sunlight faded.')
                elif self.weather == gs.HAIL:
                    self.cur_battle._add_text('The hail stopped.')
        if self.gravity_count:
            self.gravity_count -= 1
            if not self.gravity_count:
                self.acc_modifier = 1
                self.cur_battle.t1.current_poke.grounded = False
                self.cur_battle.t2.current_poke.grounded = False
        if self.trick_room_count:
            self.trick_room_count -= 1
            if not self.trick_room_count:
                self.cur_battle._add_text('The twisted dimensions returned to normal!')