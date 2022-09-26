from __future__ import annotations
from random import randrange
from queue import Queue

from poke_battle_sim.poke_sim import PokeSim
from poke_battle_sim.core.move import Move

import poke_battle_sim.core.battle as bt
import poke_battle_sim.core.battlefield as bf

import poke_battle_sim.util.process_move as pm
import poke_battle_sim.util.process_ability as pa
import poke_battle_sim.util.process_item as pi

import poke_battle_sim.conf.global_settings as gs
import poke_battle_sim.conf.global_data as gd


class Pokemon:
    def __init__(
        self,
        name_or_id: str | int,
        level: int,
        moves: [str],
        gender: str,
        ability=None,
        nature: str = None,
        cur_hp: int = None,
        stats_actual: [int] = None,
        ivs: [int] = None,
        evs: [int] = None,
        item: str = None,
        status: str = None,
        nickname: str = None,
        friendship: int = 0,
    ):
        """
        Creating a Pokemon object involves five required and six optional fields.

        Required:

        - name_or_id: this can either be a Pokemon's real name such as 'Pikachu' or its Pokedex id (25)
        - level: this is the Pokemon's level as an interger between 1 and 100 inclusive by default
        - moves: this is a list of names of the Pokemon's moves, max of 4 by defeault
        - gender: this is the Pokemon's gender, either 'male', 'female', or 'typeless' by default
        - stats: either the Pokemon's actual stats (stats_actual) or its ivs, evs, and nature

        Optional:
        - ability: Pokemon's ability; if not used, assumed that Pokemon has ability not relevant to battle
        - nature: Pokemon's nature, not required if stats_actual provided; if not used, any effect that
        takes nature into account will process the worst-case scenario for the Pokemon
        - item: Pokemon's held item
        - status: Pokemon's non-volatile status such as poisoned or paralyzed
        - nickname: Pokemon's unique nickname
        - friendship: Pokemon's friendship value as an int between 0 and 255 by default
        """

        self.stats_base = PokeSim.get_pokemon(name_or_id)
        if not self.stats_base:
            raise Exception("Attempted to create Pokemon with invalid name or id")

        self.id = int(self.stats_base[gs.NDEX])
        self.name = self.stats_base[gs.NAME]
        self.types = (self.stats_base[gs.TYPE1], self.stats_base[gs.TYPE2])
        self.base = [
            int(self.stats_base[i])
            for i in range(gs.STAT_START, gs.STAT_START + gs.STAT_NUM)
        ]
        self.height = int(self.stats_base[gs.HEIGHT])
        self.weight = int(self.stats_base[gs.WEIGHT])
        self.base_exp = int(self.stats_base[gs.BASE_EXP])
        self.gen = int(self.stats_base[gs.GEN])

        if not isinstance(level, int) or level < gs.LEVEL_MIN or level > gs.LEVEL_MAX:
            raise Exception("Attempted to create Pokemon with invalid level")
        self.level = level

        if (
            not gender
            or not isinstance(gender, str)
            or gender.lower() not in gs.POSSIBLE_GENDERS
        ):
            raise Exception("Attempted to create Pokemon with invalid gender")
        self.gender = gender

        if not stats_actual and not ivs and not evs:
            raise Exception("Attempted to create Pokemon without providing stats information")

        if stats_actual and ivs and evs:
            raise Exception("Attempted to create Pokemon with conflicting stats information")

        if stats_actual:
            if not isinstance(stats_actual, list) or len(stats_actual) != gs.STAT_NUM:
                raise Exception("Attempted to create Pokemon with invalid stats")
            if not all(
                [
                    isinstance(s, int) and gs.STAT_ACTUAL_MIN < s < gs.STAT_ACTUAL_MAX
                    for s in stats_actual
                ]
            ):
                raise Exception("Attempted to create Pokemon with invalid stats")
            self.stats_actual = stats_actual
            self.ivs = None
            self.evs = None
            self.nature = None
            self.nature_effect = None
        else:
            if (
                not isinstance(ivs, list)
                or not isinstance(evs, list)
                or len(ivs) != gs.STAT_NUM
                or len(evs) != gs.STAT_NUM
            ):
                raise Exception("Attempted to create Pokemon with invalid evs or ivs")
            if not all(
                [isinstance(iv, int) and gs.IV_MIN <= iv <= gs.IV_MAX for iv in ivs]
            ):
                raise Exception("Attempted to create Pokemon with invalid ivs")
            self.ivs = ivs
            if (
                not all(
                    [isinstance(ev, int) and gs.EV_MIN <= ev <= gs.EV_MAX for ev in evs]
                )
                or sum(evs) > gs.EV_TOTAL_MAX
            ):
                raise Exception("Attempted to create Pokemon with invalid evs")
            self.evs = evs
            self.nature_effect = PokeSim.nature_conversion(nature.lower())
            if not self.nature_effect:
                raise Exception("Attempted to create Pokemon without providing its nature")
            self.nature = nature.lower()
            self.calculate_stats_actual()

        self.max_hp = self.stats_actual[gs.HP]
        if cur_hp and (not isinstance(cur_hp, int) or cur_hp < 0 or cur_hp > self.max_hp):
            raise Exception("Attempted to create Pokemon with invalid hp value")
        if not cur_hp:
            cur_hp = self.stats_actual[gs.HP]
        self.cur_hp = cur_hp

        moves_data = PokeSim.get_move_data(moves)
        if not moves_data:
            raise Exception("Attempted to create Pokemon with invalid moveset")
        self.moves = [Move(move_d) for move_d in moves_data]
        for i in range(len(self.moves)):
            self.moves[i].pos = i
        self.o_moves = self.moves

        if ability and (
            not isinstance(ability, str) or not PokeSim.check_ability(ability.lower())
        ):
            raise Exception("Attempted to create Pokemon with invalid ability")
        self.o_ability = ability.lower() if ability else None
        self.ability = self.o_ability

        if item and (not isinstance(item, str) or not PokeSim.check_item(item.lower())):
            raise Exception("Attempted to create Pokemon with invalid held item")
        self.o_item = item.lower() if item else None

        if nickname and not isinstance(nickname, str):
            raise Exception("Attempted to create Pokemon with invalid nickname")
        self.nickname = nickname if nickname else self.name
        self.nickname = self.nickname.upper()

        self.original = None
        self.trainer = None
        if status:
            if status not in gs.NV_STATUSES:
                raise Exception("Attempted to create Pokemon afflicted with invalid status")
            self.nv_status = gs.NV_STATUSES[status]
        else:
            self.nv_status = 0
        if self.nv_status == gs.NV_STATUSES["asleep"]:
            self.nv_counter = randrange(2, 6)
        if self.nv_status == gs.NV_STATUSES["badly poisoned"]:
            self.nv_counter = 1
        else:
            self.nv_counter = 0

        if not isinstance(friendship, int) or friendship < 0 or friendship > 255:
            raise Exception("Attempted to create Pokemon with invalid friendship value")
        self.friendship = friendship

        self.is_alive = self.cur_hp != 0
        self.in_battle = False
        self.transformed = False
        self.invulnerable = False

    def calculate_stats_actual(self):
        stats_actual = []
        nature_stat_changes = [1.0 for _ in range(6)]
        nature_stat_changes[self.nature_effect[0]] = gs.NATURE_INC
        nature_stat_changes[self.nature_effect[1]] = gs.NATURE_DEC
        stats_actual.append(
            ((2 * self.base[0] + self.ivs[0] + self.evs[0] // 4) * self.level) // 100
            + 10
        )
        for s in range(1, gs.STAT_NUM):
            stats_actual.append(
                (
                    ((2 * self.base[s] + self.ivs[s] + self.evs[s] // 4) * self.level)
                    // 100
                    + 5
                )
                * nature_stat_changes[s]
            )
        self.stats_actual = [int(stat) for stat in stats_actual]

    def calculate_stats_effective(self, ignore_stats: bool = False):
        if not ignore_stats:
            for s in range(1, 6):
                self.stats_effective[s] = max(
                    1,
                    int(
                        self.stats_actual[s]
                        * max(2, 2 + self.stat_stages[s])
                        / max(2, 2 - self.stat_stages[s])
                    ),
                )
        else:
            self.stats_effective = [s for s in self.stats_actual]
        pa.stat_calc_abilities(self)
        pi.stat_calc_items(self)
        if self.nv_status == gs.PARALYZED and not self.has_ability("quick-feet"):
            self.stats_effective[gs.SPD] //= 4

    def reset_stats(self):
        self.v_status = [0 for _ in range(gs.V_STATUS_NUM)]
        self.stat_stages = [0 for _ in range(gs.STAT_NUM)]
        self.accuracy_stage = 0
        self.evasion_stage = 0
        self.crit_stage = 0
        self.substitute = 0
        self.mr_count = 0
        self.db_count = 0
        self.perish_count = 0
        self.encore_count = 0
        self.bide_count = 0
        self.bide_dmg = 0
        self.protect_count = 0
        self.embargo_count = 0
        self.hb_count = 0
        self.uproar = 0
        self.stockpile = 0
        self.charged = 0
        self.taunt = 0
        self.inv_count = 0
        self.ability_count = 0
        self.metronome_count = 0
        self.last_damage_taken = 0
        self.last_move = None
        self.last_successful_move = None
        self.last_move_next = None
        self.last_successful_move_next = None
        self.last_move_hit_by = None
        self.last_consumed_item = None
        self.copied = None
        self.binding_type = None
        self.binding_poke = None
        self.encore_move = None
        self.mr_target = None
        self.infatuation = None
        self.r_types = None
        self.mf_move = None
        self.locked_move = None
        self.in_air = False
        self.in_ground = False
        self.in_water = False
        self.grounded = False
        self.ingrain = False
        self.invulnerable = False
        self.trapped = False
        self.perma_trapped = False
        self.minimized = False
        self.rage = False
        self.recharging = False
        self.biding = False
        self.df_curl = False
        self.protect = False
        self.endure = False
        self.transformed = False
        self.tormented = False
        self.magic_coat = False
        self.foresight_target = False
        self.me_target = False
        self.snatch = False
        self.mud_sport = False
        self.water_sport = False
        self.power_trick = False
        self.ability_suppressed = False
        self.ability_activated = False
        self.item_activated = False
        self.sp_check = False
        self.magnet_rise = False
        self.has_moved = False
        self.prio_boost = False
        self.next_will_hit = False
        self.unburden = False
        self.turn_damage = False
        self.moves = self.o_moves
        self.ability = self.o_ability
        if self.transformed:
            self.reset_transform()
        self.item = self.o_item
        self.h_item = self.item
        self.old_pp = [move.cur_pp for move in self.moves]
        self.next_moves = Queue()
        self.types = (self.stats_base[gs.TYPE1], self.stats_base[gs.TYPE2])
        self.stats_effective = self.stats_actual

    def start_battle(self, battle: bt.Battle):
        self.cur_battle = battle
        self.in_battle = True
        self.reset_stats()
        self.enemy = (
            self.cur_battle.t2
            if self.cur_battle.t1 is self.trainer
            else self.cur_battle.t1
        )

    def take_damage(self, damage: int, enemy_move: Move = None) -> int:
        if not damage or damage < 0 or not self.cur_battle:
            return 0
        if self.substitute:
            self.cur_battle.add_text(
                "The substitute took damage for " + self.nickname + "!"
            )
            if self.substitute - damage <= 0:
                self.substitute = 0
                self.cur_battle.add_text(self.nickname + "'s substitute faded!")
            else:
                self.substitute -= damage
            return 0
        if enemy_move:
            self.last_move_hit_by = enemy_move
            if (
                pa.on_hit_abilities(
                    self.enemy.current_poke, self, self.cur_battle, enemy_move
                )
                or not self.cur_battle
            ):
                return 0
            pi.on_hit_items(self.enemy.current_poke, self, self.cur_battle, enemy_move)
            if not self.cur_battle:
                return
        if self.bide_count:
            self.bide_dmg += damage
        if self.cur_hp - damage <= 0:
            self.last_damage_taken = self.cur_hp
            if self._endure_check() or self._fband_check() or self._fsash_check():
                self.cur_hp = 1
                return self.last_damage_taken - 1
            self._db_check()
            if (
                self.last_move
                and self.last_move.name == "grudge"
                and enemy_move
                and self.enemy.current_poke.is_alive
            ):
                self.cur_battle.add_text(
                    self.enemy.current_poke.name
                    + "'s "
                    + enemy_move
                    + " lost all its PP due to the grudge!"
                )
                enemy_move.cur_pp = 0
            if not self.cur_battle:
                return
            self.cur_hp = 0
            self.is_alive = False
            self.reset_stats()
            self.cur_battle._faint_check()
            self._aftermath_check(enemy_move)
            return self.last_damage_taken
        if self.rage and self.stat_stages[gs.ATK] < 6:
            self.stat_stages[gs.ATK] += 1
            self.cur_battle.add_text(self.nickname + "'s rage is building!")
        self.turn_damage = True
        self.cur_hp -= damage
        self.last_damage_taken = damage
        pi.on_damage_items(self, self.cur_battle, enemy_move)
        return self.last_damage_taken

    def faint(self):
        if not self.is_alive:
            return
        self.cur_hp = 0
        self.is_alive = False
        self.reset_stats()
        self.cur_battle._faint_check()

    def heal(self, heal_amount: int, text_skip: bool = False) -> int:
        if not self.cur_battle or heal_amount <= 0:
            return 0
        if self.cur_hp + heal_amount >= self.max_hp:
            amt = self.max_hp - self.cur_hp
            self.cur_hp = self.max_hp
            r_amt = amt
        else:
            self.cur_hp += heal_amount
            r_amt = heal_amount
        if not text_skip:
            self.cur_battle.add_text(self.nickname + " regained health!")
        return r_amt

    def get_move_data(self, move_name: str) -> Move:
        if self.copied and move_name == self.copied.name:
            return self.copied
        for move in self.moves:
            if move.name == move_name:
                return move

    def is_move(self, move_name: str) -> bool:
        if self.copied and self.copied.cur_pp:
            if move_name == self.copied.name:
                return True
            if move_name == "mimic":
                return False
        av_moves = self.get_available_moves()
        for move in av_moves:
            if move.name == move_name:
                return True
        return False

    def get_available_moves(self) -> list | None:
        if not self.next_moves.empty() or self.recharging:
            return
        av_moves = [move for move in self.moves if not move.disabled and move.cur_pp]
        if self.copied and self.copied.cur_pp:
            for i in range(len(av_moves)):
                if av_moves[i].name == "mimic":
                    av_moves[i] = self.copied
        if self.tormented and av_moves and self.last_move:
            av_moves = [move for move in av_moves if move.name != self.last_move.name]
        if self.taunt and av_moves:
            av_moves = [move for move in av_moves if move.category != gs.STATUS]
        if self.grounded and av_moves:
            av_moves = [move for move in av_moves if move not in gd.GROUNDED_CHECK]
        if self.hb_count and av_moves:
            av_moves = [move for move in av_moves if move not in gd.HEAL_BLOCK_CHECK]
        if (
            self.trainer.imprisoned_poke
            and self.trainer.imprisoned_poke is self.enemy.current_poke
            and av_moves
        ):
            i_moves = [move.name for move in self.trainer.imprisoned_poke.moves]
            av_moves = [move for move in av_moves if move.name not in i_moves]
        if self.has_ability("truant") and self.last_move and av_moves:
            av_moves = [move for move in av_moves if move.name != self.last_move.name]
        if self.locked_move:
            av_moves = [move for move in av_moves if move.name == self.locked_move]
        return av_moves

    def transform(self, target: Pokemon):
        if self.transformed or target.transformed:
            return
        self.original = [
            self.name,
            self.types,
            self.height,
            self.weight,
            self.base_exp,
            self.gen,
            self.ability,
            [stat for stat in self.stats_base],
            [iv for iv in self.ivs] if self.ivs else None,
            [ev for ev in self.evs] if self.evs else None,
            self.nature,
            self.nature_effect,
            [move.get_tcopy() for move in self.moves],
            [stat for stat in self.stats_actual],
        ]
        self.name = target.name
        self.types = target.types
        self.height = target.height
        self.weight = target.weight
        self.base_exp = target.base_exp
        self.gen = target.gen
        self.ability = target.ability
        self.moves = [move.get_tcopy() for move in target.moves]
        for move in self.moves:
            move.max_pp = min(5, move.max_pp)
            move.cur_pp = move.max_pp
        self.stats_actual = target.stats_actual
        self.stat_stages = target.stat_stages
        self.accuracy_stage = target.accuracy_stage
        self.evasion_stage = target.evasion_stage
        self.crit_stage = target.evasion_stage
        self.calculate_stats_effective()

        self.transformed = True

    def reset_transform(self):
        if not self.transformed or not self.original:
            return
        self.name = self.original[0]
        self.types = self.original[1]
        self.height = self.original[2]
        self.weight = self.original[3]
        self.base_exp = self.original[4]
        self.gen = self.original[5]
        self.ability = self.original[6]
        self.stats_base = self.original[7]
        self.ivs = self.original[8]
        self.evs = self.original[9]
        self.nature = self.original[10]
        self.nature_effect = self.original[11]
        self.moves = self.original[12]
        self.stats_actual = self.original[13]
        self.original = None
        self.transformed = False

    def give_ability(self, ability: str):
        self.ability = ability
        self.ability_activated = False
        self.ability_suppressed = False
        self.ability_count = 0
        pa.selection_abilities(self, self.cur_battle.battlefield, self.cur_battle)

    def battle_end_reset(self):
        if self.transformed:
            self.reset_transform()
        self.reset_stats()
        self.in_battle = False
        self.cur_battle = None
        self.enemy = None

    def switch_out(self):
        if self.transformed:
            self.reset_transform()
        self.reset_stats()
        if self.has_ability("natural-cure") and self.nv_status:
            pm._cure_nv_status(self.nv_status, self, self.cur_battle)

    def update_last_moves(self):
        if self.last_move_next:
            self.last_move = self.last_move_next
            self.last_move = None
        if self.last_successful_move_next:
            self.last_successful_move = self.last_successful_move_next
            self.last_successful_move_next = None

    def reduce_disabled_count(self):
        for move in self.moves:
            if move.disabled:
                move.disabled -= 1

    def no_pp(self) -> bool:
        return all(
            not move.cur_pp or move.disabled or move.encore_blocked
            for move in self.get_available_moves()
        )

    def can_switch_out(self) -> bool:
        if self.item == "shed-shell":
            return True
        if (
            self.trapped
            or self.perma_trapped
            or self.recharging
            or not self.next_moves.empty()
        ):
            return False
        enemy_poke = self.enemy.current_poke
        if enemy_poke.is_alive and enemy_poke.has_ability("shadow-tag"):
            return False
        if (
            "steel" in self.types
            and enemy_poke.is_alive
            and enemy_poke.has_ability("magnet_pull")
        ):
            return False
        if (
            (
                self.grounded
                or (not "flying" in self.types and not self.has_ability("levitate"))
            )
            and enemy_poke.is_alive
            and enemy_poke.has_ability("arena-trap")
        ):
            return False
        return True

    def can_use_item(self) -> bool:
        return not self.embargo_count

    def has_ability(self, ability_name: str) -> bool:
        return not self.ability_suppressed and self.ability == ability_name

    def reset_stages(self):
        self.accuracy_stage = 0
        self.evasion_stage = 0
        self.crit_stage = 0
        self.stat_stages = [0 for _ in range(gs.STAT_NUM)]

    def _endure_check(self) -> bool:
        if self.endure:
            self.cur_battle.add_text(self.nickname + " endured the hit!")
            self.cur_hp = 1
            return True
        return False

    def _fband_check(self) -> bool:
        if self.item == "focus-band" and randrange(10) < 1:
            self.cur_battle.add_text(self.nickname + " hung on using its Focus Band!")
            return True
        return False

    def _fsash_check(self) -> bool:
        if (
            self.item == "focus-sash"
            and self.cur_hp == self.max_hp
            and not self.item_activated
        ):
            self.cur_battle.add_text(self.nickname + " hung on using its Focus Sash!")
            self.item_activated = True
            return True
        return False

    def _db_check(self) -> bool:
        if not self.db_count:
            return False
        enemy_poke = self.enemy.current_poke
        self.cur_battle.add_text(
            self.nickname + " took down " + enemy_poke.nickname + " down with it!"
        )
        enemy_poke.faint()
        return True

    def _aftermath_check(self, enemy_move: Move):
        if (
            self.has_ability("aftermath")
            and enemy_move in gd.CONTACT_CHECK
            and self.enemy.current_poke.is_alive
            and not self.enemy.current_poke.has_ability("damp")
        ):
            self.enemy.current_poke.take_damage(
                max(1, self.enemy.current_poke.max_hp // 4)
            )
            self.cur_battle.add_text(
                self.enemy.current_poke.nickname
                + " was hurt by "
                + self.nickname
                + "'s Aftermath!"
            )

    def give_item(self, item: str):
        self.item = item
        self.h_item = item
        if not item:
            self.unburden = True
        pi.status_items(self, self.cur_battle)

    def hidden_power_stats(self) -> tuple[str, int] | None:
        if not self.ivs:
            return
        hp_type = 0
        for i in range(6):
            hp_type += 2**i * (self.ivs[i] & 1)
        hp_type = (hp_type * 15) // 63
        hp_power = 0
        for i in range(6):
            hp_power += 2**i * ((self.ivs[i] >> 1) & 1)
        hp_power = (hp_type * 40) // 63 + 30
        return (gd.HP_TYPES[hp_type], hp_power)

    def restore_pp(self, move_name: str, amount: int):
        for move in self.moves:
            if move.name == move_name:
                move.cur_pp = min(move.cur_pp + amount, move.max_pp)
        self.cur_battle.add_text(
            self.nickname + "'s " + pm.cap_name(move_name) + "'s pp was restored!"
        )

    def restore_all_pp(self, amount: int):
        for move in self.moves:
            move.cur_pp = min(move.cur_pp + amount, move.max_pp)
        self.cur_battle.add_text(self.nickname + "'s move's pp were restored!")
