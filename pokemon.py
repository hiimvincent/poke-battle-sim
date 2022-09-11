from __future__ import annotations
from queue import Queue
from poke_sim import PokeSim
import process_move
import battlefield
import battle as bt
from move import Move
import random

# STAT_ORDERING_FORMAT
HP = 0
ATK = 1
DEF = 2
SP_ATK = 3
SP_DEF = 4
SPD = 5
STAT_NUM = 6

STATUS = 1
PHYSICAL = 2
SPECIAL = 3

# STAT_RANGES
LEVEL_MIN, LEVEL_MAX = 1, 100
STAT_ACTUAL_MIN, STAT_ACTUAL_MAX = 1, 500
IV_MIN, IV_MAX = 0, 31
EV_MIN, EV_MAX = 0, 255
EV_TOTAL_MAX = 510
NATURE_DEC, NATURE_INC = 0.9, 1.1

V_STATUS_NUM = 9
POSSIBLE_GENDERS = ['male', 'female', 'genderless']

# NON_VOLATILE_STATUSES
NV_STATUSES = {
    'burned': 1,
    'frozen': 2,
    'paralyzed': 3,
    'poisoned': 4,
    'asleep': 5,
    'badly poisoned': 6
}

# STATS_BASE_FORMAT
_NDEX = 0
_NAME = 1
_TYPE1 = 2
_TYPE2 = 3
_STAT_START = 4
_HEIGHT = 10
_WEIGHT = 11
_BASE_EXP = 12
_GEN = 13

HP_TYPES = ['fighting', 'flying', 'poison', 'ground', 'rock', 'bug', 'ghost', 'steel', 'fire', 'water', 'grass',
            'electric', 'psychic', 'ice', 'dragon', 'dark']

GROUNDED_CHECK = ['bounce', 'fly', 'high-jump-kick', 'jump-kick', 'magnet-rise', 'splash']

HEAL_BLOCK_CHECK = ['heal-order', 'milk-drink', 'moonlight', 'morning-sun', 'recover', 'rest', 'roost', 'slack-off',
                    'soft-boiled', 'synthesis', 'wish', 'lunar-dance', 'healing-wish']

# need item, ability
class Pokemon:
    def __init__(
            self, name_or_id: str | int, level: int, moves: [str], gender: str, ability = None, nature: str = None,
            cur_hp: int = None, stats_actual: [int] = None, ivs: [int] = None, evs: [int] = None, item: str = None,
            status: str = None, nickname: str = None, friendship: int = 0):

        self.stats_base = PokeSim.get_pokemon(name_or_id)
        if not self.stats_base:
            raise Exception

        self.id = int(self.stats_base[_NDEX])
        self.name = self.stats_base[_NAME]
        self.types = (self.stats_base[_TYPE1], self.stats_base[_TYPE2])
        self.base = [int(self.stats_base[i]) for i in range(_STAT_START, _STAT_START + STAT_NUM)]
        self.height = int(self.stats_base[_HEIGHT])
        self.weight = int(self.stats_base[_WEIGHT])
        self.base_exp = int(self.stats_base[_BASE_EXP])
        self.gen = int(self.stats_base[_GEN])

        if not isinstance(level, int) or level < LEVEL_MIN or level > LEVEL_MAX:
            raise Exception
        self.level = level

        if not gender or not isinstance(gender, str) or gender.lower() not in POSSIBLE_GENDERS:
            raise Exception
        self.gender = gender

        if not stats_actual and not ivs and not evs:
            raise Exception

        if stats_actual and ivs and evs:
            raise Exception

        if stats_actual:
            if not isinstance(stats_actual, list) or len(stats_actual) != STAT_NUM:
                raise Exception
            if not all([isinstance(s, int) and STAT_ACTUAL_MIN < s < STAT_ACTUAL_MAX for s in stats_actual]):
                raise Exception
            self.stats_actual = stats_actual
            self.ivs = None
            self.evs = None
            self.nature = None
            self.nature_effect = None
        else:
            if not isinstance(ivs, list) or not isinstance(evs, list) or len(ivs) != STAT_NUM or len(evs) != STAT_NUM:
                raise Exception
            if not all([isinstance(iv, int) and IV_MIN <= iv <= IV_MAX for iv in ivs]):
                raise Exception
            self.ivs = ivs
            if not all([isinstance(ev, int) and EV_MIN <= ev <= EV_MAX for ev in evs]) or sum(evs) > EV_TOTAL_MAX:
                raise Exception
            self.evs = evs
            self.nature_effect = PokeSim.nature_conversion(nature.lower())
            if not self.nature_effect:
                raise Exception
            self.nature = nature.lower()
            self.calculate_stats_actual()

        self.max_hp = self.stats_actual[HP]
        if cur_hp and (cur_hp < 0 or cur_hp > self.max_hp):
            raise Exception
        if not cur_hp:
            cur_hp = self.stats_actual[HP]
        self.cur_hp = cur_hp

        self.o_item = item

        moves_data = PokeSim.get_move_data(moves)
        if not moves_data:
            raise Exception
        self.moves = [Move(move_d) for move_d in moves_data]
        for i in range(len(self.moves)):
            self.moves[i].pos = i
        self.o_moves = self.moves

        self.o_ability = ability
        self.ability = self.o_ability
        if nickname and not isinstance(nickname, str):
            raise Exception
        self.nickname = nickname if nickname else self.name
        self.nickname = self.nickname.upper()

        self.id = int(self.stats_base[_NDEX])
        self.name = self.stats_base[_NAME]
        self.types = (self.stats_base[_TYPE1], self.stats_base[_TYPE2])
        self.base = [int(self.stats_base[i]) for i in range(_STAT_START, _STAT_START + STAT_NUM)]
        self.height = int(self.stats_base[_HEIGHT])
        self.weight = int(self.stats_base[_WEIGHT])
        self.base_exp = int(self.stats_base[_BASE_EXP])
        self.gen = int(self.stats_base[_GEN])
        self.original = None
        self.trainer = None
        if status:
            if status not in NV_STATUSES:
                raise Exception
            self.nv_status = NV_STATUSES[status]
        else:
            self.nv_status = 0
        if self.nv_status ==  NV_STATUSES['asleep']:
            self.nv_counter = random.randrange(2,6)
        if self.nv_status ==  NV_STATUSES['badly poisoned']:
            self.nv_counter = 1
        else:
            self.nv_counter = 0

        if not isinstance(friendship, int) or friendship < 0 or friendship > 255:
            raise Exception
        self.friendship = friendship

        self.is_alive = self.cur_hp != 0
        self.in_battle = False
        self.transformed = False
        self.invulnerable = False

    def calculate_stats_actual(self):
        stats_actual = []
        nature_stat_changes = [1.0 for _ in range(6)]
        nature_stat_changes[self.nature_effect[0]] = NATURE_INC
        nature_stat_changes[self.nature_effect[1]] = NATURE_DEC
        stats_actual.append(((2 * self.base[0] + self.ivs[0] + self.evs[0] // 4) * self.level) // 100 + 10)
        for s in range(1, STAT_NUM):
            stats_actual.append((((2 * self.base[s] + self.ivs[s] + self.evs[s] // 4) * self.level) // 100 + 5) * nature_stat_changes[s])
        self.stats_actual = [int(stat) for stat in stats_actual]

    def calculate_stats_effective(self):
        for s in range(1, 6):
            self.stats_effective[s] = max(1, int(self.stats_actual[s] * max(2, 2 + self.stat_stages[s]) / max(2, 2 - self.stat_stages[s])))

    def reset_stats(self):
        self.v_status = [0 for _ in range(V_STATUS_NUM)]
        self.stat_stages = [0 for _ in range(STAT_NUM)]
        self.accuracy_stage = 0
        self.evasion_stage = 0
        self.crit_stage = 0
        self.substitute = 0
        self.mist_count = 0
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
        self.sp_check = False
        self.magnet_rise = False
        self.turn_damage = False
        self.moves = self.o_moves
        self.ability = self.o_ability
        if self.transformed:
            self.reset_transform()
        self.item = self.o_item
        self.h_item = self.item
        self.old_pp = [move.cur_pp for move in self.moves]
        self.next_moves = Queue()
        self.types = (self.stats_base[_TYPE1], self.stats_base[_TYPE2])
        self.stats_effective = self.stats_actual
        self.calculate_stats_effective()

    def start_battle(self, battle: bt.Battle):
        self.cur_battle = battle
        self.in_battle = True
        self.reset_stats()
        self.enemy = self.cur_battle.t2 if self.cur_battle.t1 is self.trainer else self.cur_battle.t1

    def take_damage(self, damage: int, enemy_move: Move = None) -> int:
        if damage <= 0:
            return 0
        if self.substitute:
            self.cur_battle._add_text('The substitute took damage for' + self.nickname + '!')
            if self.substitute - damage <= 0:
                self.substitute = 0
                self.cur_battle._add_text(self.nickname + '\'s substitute faded!')
            else:
                self.substitute -= damage
            return
        if enemy_move:
            self.last_move_hit_by = enemy_move
        if self.bide_count:
            self.bide_dmg += damage
        if self.cur_hp - damage <= 0:
            self.last_damage_taken = self.cur_hp
            if self._endure_check():
                self.cur_hp = 1
                return self.last_damage_taken - 1
            self._db_check()
            if self.last_move and self.last_move.name == 'grudge' and enemy_move and self.enemy.current_poke.is_alive:
                self.cur_battle._add_text(self.enemy.current_poke.name + '\'s ' + enemy_move + ' lost all its PP due to the grudge!')
                enemy_move.cur_pp = 0
            self.cur_hp = 0
            self.is_alive = False
            self.reset_stats()
            return self.last_damage_taken
        if self.rage and self.stat_stages[ATK] < 6:
            self.stat_stages[ATK] += 1
            self.cur_battle._add_text(self.nickname + '\'s rage is building!')
        self.turn_damage = True
        self.cur_hp -= damage
        self.last_damage_taken = damage
        return self.last_damage_taken

    def faint(self):
        if not self.is_alive:
            return
        self.cur_hp = 0
        self.is_alive = False
        self.reset_stats()
        self.cur_battle._faint_check()

    def heal(self, heal_amount: int, text_skip: bool = False) -> int:
        if heal_amount <= 0:
            return 0
        if self.cur_hp + heal_amount >= self.max_hp:
            amt = self.max_hp - self.cur_hp
            self.cur_hp = self.max_hp
            r_amt = amt
        else:
            self.cur_hp += heal_amount
            r_amt = heal_amount
        if not text_skip:
            self.cur_battle._add_text(self.nickname + ' regained health!')
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
            if move_name == 'mimic':
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
                if av_moves[i].name == 'mimic':
                    av_moves[i] = self.copied
        if self.tormented and av_moves and self.last_move:
            av_moves = [move for move in av_moves if move.name != self.last_move.name]
        if self.taunt and av_moves:
            av_moves = [move for move in av_moves if move.category != STATUS]
        if self.grounded:
            av_moves = [move for move in av_moves if move not in GROUNDED_CHECK]
        if self.hb_count:
            av_moves = [move for move in av_moves if move not in HEAL_BLOCK_CHECK]
        if self.trainer.imprisoned_poke and self.trainer.imprisoned_poke is self.enemy.current_poke and av_moves:
            i_moves = [move.name for move in self.trainer.imprisoned_poke.moves]
            av_moves = [move for move in av_moves if move.name not in i_moves]
        return av_moves

    def transform(self, target: Pokemon):
        if self.transformed or target.transformed:
            return
        self.original = [self.name, self.types, self.height, self.weight, self.base_exp,
                        self.gen,  self.ability, [stat for stat in self.stats_base],
                         [iv for iv in self.ivs] if self.ivs else None, [ev for ev in self.evs] if self.evs else None,
                         self.nature, self.nature_effect, [move.get_tcopy() for move in self.moves],
                         [stat for stat in self.stats_actual]]
        self.name = target.name
        self.types = target.types
        self.height = target.height
        self.weight = target.weight
        self.base_exp = target.base_exp
        self.gen = target.gen
        self.ability = target.ability
        self.moves = target.moves
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

    def battle_end_reset(self):
        if self.transformed:
            self.reset_transform()
        self.reset_stats()
        self.in_battle = False

    def switch_out(self):
        if self.transformed:
            self.reset_transform()
        self.reset_stats()

    def update_last_moves(self):
        if self.last_move_next:
            self.last_move = self.last_move_next
            self.last_move = None
        if self.last_successful_move_next:
            self.last_successful_move = self.last_successful_move_next
            self.last_successful_move_next = None

    def print_all_data(self):
        print('Name:', self.name)
        print('\nNDex:', self.id)
        print('\nLvl:', self.level)

    def reduce_disabled_count(self):
        for move in self.moves:
            if move.disabled:
                move.disabled -= 1

    def no_pp(self) -> bool:
        return all(not move.cur_pp or move.disabled or move.encore_blocked for move in self.get_available_moves())

    def reset_stages(self):
        self.accuracy_stage = 0
        self.evasion_stage = 0
        self.crit_stage = 0
        self.stat_stages = [0 for _ in range(STAT_NUM)]

    def _endure_check(self) -> bool:
        if self.endure:
            self.cur_battle._add_text(self.nickname + ' endured the hit!')
            self.cur_hp = 1
            return True
        return False

    def _db_check(self) -> bool:
        if not self.db_count:
            return False
        enemy_poke = self.enemy.current_poke
        self.cur_battle._add_text(self.nickname + ' took down ' + enemy_poke.nickname + ' down with it!')
        enemy_poke.faint()
        return True

    def give_item(self, item: str):
        self.item = item
        self.h_item = item

    def hidden_power_stats(self) -> tuple[str, int] | None:
        if not self.ivs:
            return
        hp_type = 0
        for i in range(6):
            hp_type += 2 ** i * (self.ivs[i] & 1)
        hp_type = (hp_type * 15) // 63
        hp_power = 0
        for i in range(6):
            hp_power += 2 ** i * ((self.ivs[i] >> 1) & 1)
        hp_power = (hp_type * 40) // 63 + 30
        return (HP_TYPES[hp_type], hp_power)



