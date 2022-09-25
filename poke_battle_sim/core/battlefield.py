from __future__ import annotations

import poke_battle_sim.core.battle as bt

import poke_battle_sim.util.process_ability as pa

import poke_battle_sim.conf.global_settings as gs


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
                    self.cur_battle.add_text("The sandstorm is raging.")
                elif self.weather == gs.RAIN:
                    self.cur_battle.add_text("Rain continues to fall.")
                elif self.weather == gs.HARSH_SUNLIGHT:
                    self.cur_battle.add_text("The sunlight is strong.")
                elif self.weather == gs.HAIL:
                    self.cur_battle.add_text("The hail is crashing down.")
            else:
                if self.weather == gs.SANDSTORM:
                    self.cur_battle.add_text("The sandstorm subsided.")
                elif self.weather == gs.RAIN:
                    self.cur_battle.add_text("The rain stopped.")
                elif self.weather == gs.HARSH_SUNLIGHT:
                    self.cur_battle.add_text("The harsh sunlight faded.")
                elif self.weather == gs.HAIL:
                    self.cur_battle.add_text("The hail stopped.")
        if self.gravity_count:
            self.gravity_count -= 1
            if not self.gravity_count:
                self.acc_modifier = 1
                self.cur_battle.t1.current_poke.grounded = False
                self.cur_battle.t2.current_poke.grounded = False
        if self.trick_room_count:
            self.trick_room_count -= 1
            if not self.trick_room_count:
                self.cur_battle.add_text("The twisted dimensions returned to normal!")

    def change_weather(self, weather: int):
        if self.weather != weather:
            self.weather = weather
            pa.weather_change_abilities(self.cur_battle, self)

    def process_weather_effects(self, poke: pk.Pokemon):
        if not poke.is_alive or self.weather_count >= 999:
            return
        if (
            self.weather == gs.SANDSTORM
            and not poke.has_ability("sand-veil")
            and not poke.in_ground
            and not poke.in_water
            and not any(type in poke.types for type in ["ground", "steel", "rock"])
        ):
            self.cur_battle.add_text(poke.nickname + " is buffeted by the Sandstorm!")
            poke.take_damage(max(1, poke.max_hp // 16))
        if (
            self.weather == gs.HAIL
            and not poke.has_ability("ice-body")
            and not poke.in_ground
            and not poke.in_water
            and not any(type in poke.types for type in ["ice"])
        ):
            self.cur_battle.add_text(poke.nickname + " is buffeted by the Hail!")
            poke.take_damage(max(1, poke.max_hp // 16))
        if self.weather == gs.HAIL and poke.has_ability("ice-body"):
            self.cur_battle.add_text(poke.nickname + " was healed by its Ice Body!")
            poke.heal(max(1, poke.max_hp // 16), text_skip=True)
        if self.weather == gs.RAIN and poke.has_ability("dry-skin"):
            self.cur_battle.add_text(poke.nickname + " was healed by its Dry Skin!")
            poke.heal(max(1, poke.max_hp // 8), text_skip=True)
        if self.weather == gs.HARSH_SUNLIGHT and poke.has_ability("dry-skin"):
            self.cur_battle.add_text(poke.nickname + " was hurt by its Dry Skin!")
            poke.take_damage(max(1, poke.max_hp // 8))
