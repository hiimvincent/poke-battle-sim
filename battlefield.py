from __future__ import annotations
import battle as bt

CLEAR = 0
HARSH_SUNLIGHT = 1
RAIN = 2
SANDSTORM = 3
HAIL = 4
FOG = 5

class Battlefield:
    def __init__(self, battle: bt.Battle):
        self.weather = CLEAR
        self.acc_modifier = 1
        self.weather_count = 0
        self.gravity_count = 0
        self.gravity_stats = None
        self.cur_battle = battle

    def update(self):
        if self.weather_count:
            self.weather_count -= 1
            if self.weather_count:
                if self.weather == SANDSTORM:
                    self.cur_battle._add_text('The sandstorm is raging.')
                elif self.weather == RAIN:
                    self.cur_battle._add_text('Rain continues to fall.')
                elif self.weather == HARSH_SUNLIGHT:
                    self.cur_battle._add_text('The sunlight is strong.')
                elif self.weather == HAIL:
                    self.cur_battle._add_text('The hail is crashing down.')
            else:
                if self.weather == SANDSTORM:
                    self.cur_battle._add_text('The sandstorm subsided.')
                elif self.weather == RAIN:
                    self.cur_battle._add_text('The rain stopped.')
                elif self.weather == HARSH_SUNLIGHT:
                    self.cur_battle._add_text('The harsh sunlight faded.')
                elif self.weather == HAIL:
                    self.cur_battle._add_text('The hail stopped.')
        if self.gravity_count:
            self.gravity_count -= 1
            if not self.gravity_count:
                self.acc_modifier = 1
                self.cur_battle.t1.current_poke.grounded = False
                self.cur_battle.t2.current_poke.grounded = False





