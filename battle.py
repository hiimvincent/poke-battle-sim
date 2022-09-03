from __future__ import annotations

import random

import pokemon as pk
import trainer as tr
import move
import battlefield as bf
import process_move as pm

ACTION_PRIORITY = {
    'other': 3,
    'item': 2,
    'move': 1
}

MOVE = 'move'

# STAT_ORDERING_FORMAT
HP = 0
ATK = 1
DEF = 2
SP_ATK = 3
SP_DEF = 4
SPD = 5
STAT_NUM = 6

CONFUSED = 0
FLINCHED = 1
LEECH_SEED = 2

BINDING_COUNT = 3
BIND = 1
WRAP = 2
FIRE_SPIN = 3
CLAMP = 4

NIGHTMARE = 4
CURSE = 5

# TURN_DATA
ACTION_TYPE = 0
ACTION_VALUE = 1

MOVE_PRIORITY = 7
MOVE_NAME = 1

RECHARDING = ('other', 'recharging')
BIDING = ('other', 'biding')
RAGE = ('move', 'rage')
STRUGGLE = ('move', 'struggle')

BURNED = 1
FROZEN = 2
PARALYZED = 3
POISONED = 4
ASLEEP = 5
BADLY_POISONED = 5

class Battle:
    def __init__(self, t1: tr.Trainer, t2: tr.Trainer):
        if not isinstance(t1, tr.Trainer) or not isinstance(t2, tr.Trainer):
            raise Exception
        if t1.in_battle or t2.in_battle:
            raise Exception
        for t1_poke in t1.poke_list:
            for t2_poke in t2.poke_list:
                if t1_poke is t2_poke:
                    raise Exception
        for t1_poke in t1.poke_list:
            if t1_poke.in_battle:
                raise Exception
        for t2_poke in t2.poke_list:
            if t2_poke.in_battle:
                raise Exception

        self.t1 = t1
        self.t2 = t2
        self.battle_started = False
        self.all_text = []
        self.cur_text = []

    def start(self):
        self.t1.start_pokemon(self)
        self.t2.start_pokemon(self)
        self.t1.in_battle = True
        self.t2.in_battle = True
        self.t1_faint = False
        self.t2_faint = False
        self.battlefield = bf.Battlefield()
        self.battle_started = True
        self.winner = None
        self.turn_count = 0
        self._add_text(self.t1.name + " sent out " + self.t1.current_poke.nickname + "!")
        self._add_text(self.t2.name + " sent out " + self.t2.current_poke.nickname + "!")

    def turn(self, t1_move: tuple[str, str], t2_move: tuple[str, str]) -> bool | None:
        self.turn_count += 1
        if not self.battle_started:
            raise Exception
        if self.is_finished():
            return

        t1_move_data = None
        t2_move_data = None
        t1_mv_check_bypass = False
        t2_mv_check_bypass = False

        if self.t1.current_poke.recharging:
            t1_move = RECHARDING
        elif self.t1.current_poke.bide_count:
            t1_move = BIDING
        elif self.t1.current_poke.rage:
            t1_move = RAGE
            t1_mv_check_bypass = True
        elif not self.t1.current_poke.next_moves.empty():
            t1_move_data = self.t1.current_poke.next_moves.get()
            t1_move = (MOVE, t1_move_data.name)
            t1_mv_check_bypass = True
        elif t1_move[ACTION_TYPE] == MOVE and self.t1.current_poke.no_pp():
            t1_move = STRUGGLE
            t1_mv_check_bypass = True
        if self.t2.current_poke.recharging:
            t2_move = RECHARDING
        elif self.t2.current_poke.bide_count:
            t2_move = BIDING
        elif self.t2.current_poke.rage:
            t2_move = RAGE
            t2_mv_check_bypass = True
        elif not self.t2.current_poke.next_moves.empty():
            t2_move_data = self.t2.current_poke.next_moves.get()
            t2_move = (MOVE, t2_move_data.name)
            t2_mv_check_bypass = True
        elif t2_move[ACTION_TYPE] == MOVE and self.t2.current_poke.no_pp():
            t2_move = STRUGGLE
            t2_mv_check_bypass = True

        if not isinstance(t1_move, tuple) or not all(isinstance(t1_move[i], str) for i in range(len(t1_move))) or len(t1_move) < 2:
            raise Exception
        if not isinstance(t2_move, tuple) or not all(isinstance(t2_move[i], str) for i in range(len(t2_move))) or len(t2_move) < 2:
            raise Exception

        self.t1.has_moved = False
        self.t2.has_moved = False
        t1_move = (t1_move[ACTION_TYPE].lower(), t1_move[ACTION_VALUE].lower())
        t2_move = (t2_move[ACTION_TYPE].lower(), t2_move[ACTION_VALUE].lower())
        self.t1_fainted = False
        self.t2_fainted = False

        if t1_move[ACTION_TYPE] not in ACTION_PRIORITY or t2_move[ACTION_TYPE] not in ACTION_PRIORITY:
            raise Exception
        if t1_move[ACTION_TYPE] == MOVE and not t1_mv_check_bypass and not self.t1.current_poke.is_move(t1_move[ACTION_VALUE]):
            raise Exception
        if t2_move[ACTION_TYPE] == MOVE and not t2_mv_check_bypass and not self.t2.current_poke.is_move(t2_move[ACTION_VALUE]):
            raise Exception

        if not t1_move_data and  t1_move[ACTION_TYPE] == MOVE:
            t1_move_data = self.t1.current_poke.get_move_data(t1_move[ACTION_VALUE])
        if not t2_move_data and t2_move[ACTION_TYPE] == MOVE:
            t2_move_data = self.t2.current_poke.get_move_data(t2_move[ACTION_VALUE])
        t1_prio = ACTION_PRIORITY[t1_move[ACTION_TYPE]]
        t2_prio = ACTION_PRIORITY[t2_move[ACTION_TYPE]]
        t1_first = t1_prio >= t2_prio
        if t1_prio == 1 and t2_prio == 1:
            if t1_move_data.prio != t2_move_data.prio:
                t1_first = t1_move_data.prio > t2_move_data.prio
            else:
                spd_dif = self.t1.current_poke.stats_effective[5] - self.t2.current_poke.stats_effective[5]
                if spd_dif == 0:
                    t1_first = random.randrange(2) < 1
                else:
                    t1_first = spd_dif > 0

        self._add_text("Turn " + str(self.turn_count) + ":")
        if t1_first:
            if self.t1.current_poke.is_alive:
                # trainer 1 turn
                self._half_turn(self.t1, self.t2, t1_move, t1_move_data)
            self._faint_check()
            if self.t2.current_poke.is_alive:
                #trainer 2 turn
                self._half_turn(self.t2, self.t1, t2_move, t2_move_data)
            self._faint_check()
        else:
            if self.t2.current_poke.is_alive:
                # trainer 2 turn
                self._half_turn(self.t2, self.t1, t2_move, t2_move_data)
            self._faint_check()
            if self.t1.current_poke.is_alive:
                # trainer 1 turn
                self._half_turn(self.t1, self.t2, t1_move, t1_move_data)
            self._faint_check()

        dif = self.t1.current_poke.stats_actual[SPD] - self.t2.current_poke.stats_actual[SPD]
        if dif > 0:
            faster = self.t1
            slower = self.t2
        elif dif < 0:
            faster = self.t2
            slower = self.t1
        else:
            faster = self.t1 if random.randrange(2) < 1 else self.t2
            slower = self.t2 if faster is self.t1 else self.t1

        if faster.current_poke.is_alive:
            self._post_process_status(faster, slower)
        self._faint_check()
        if not faster.current_poke.is_alive:
            faster.num_fainted += 1
            if faster.num_fainted == len(faster.poke_list):
                self._victory(slower, faster)
                return
            self._process_selection(faster)
        if slower.current_poke.is_alive:
            self._post_process_status(slower, faster)
        self._faint_check()
        if not slower.current_poke.is_alive:
            slower.num_fainted += 1
            if slower.num_fainted == len(slower.poke_list):
                self._victory(faster, slower)
                return
            self._process_selection(slower)

    def get_cur_text(self) -> list:
        cur_t = self.cur_text
        self.cur_text = []
        return cur_t

    def get_all_text(self) -> list:
        return self.all_text

    def _half_turn(self, attacker: tr.Trainer, defender: tr.Trainer, a_move: tuple[str, str], a_move_data: Move = None):
        if a_move[ACTION_TYPE] == 'other':
            self._process_other(attacker, defender, a_move)
        elif a_move[ACTION_TYPE] == 'item':
            process_item()
        else:
            pm.process_move(attacker.current_poke, defender.current_poke, self.battlefield, self, a_move_data.get_tcopy(), not defender.has_moved)
        attacker.has_moved = True

    def _post_process_status(self, trainer: tr.Trainer, other: tr.Trainer):
        poke = trainer.current_poke
        if trainer.reflect:
            trainer.reflect -= 1
        if trainer.light_screen:
            trainer.light_screen -= 1
        if poke.mist_count:
            poke.mist_count -= 1
        if poke.bide_count:
            poke.bide_count -= 1
        if poke.mr_count:
            poke.mr_count -= 1
            if not poke.mr_count:
                poke.mr_target = None
        if poke.protect:
            poke.protect = False
            poke.invulnerable = False
            if poke.last_successful_move not in ['protect', 'detect', 'endure']:
                poke.protect_count = 0
        if poke.v_status[FLINCHED]:
            poke.v_status[FLINCHED] = 0
        if poke.foresight_target and not poke.foresight_target is other.current_poke:
            poke.foresight_target = None
        if poke.nv_status == BURNED:
            poke.take_damage(max(1, poke.max_hp // 8))
            self._add_text(poke.nickname + " was hurt by its burn!")
        if poke.nv_status == POISONED:
            poke.take_damage(max(1, poke.max_hp // 8))
            self._add_text(poke.nickname + " was hurt by poison!")
        if poke.nv_status == BADLY_POISONED:
            poke.take_damage(max(1, poke.max_hp * poke.nv_counter // 16))
            poke.nv_counter += 1

        if poke.v_status[BINDING_COUNT] and poke.is_alive:
            if not poke.binding_poke is other.current_poke:
                poke.v_status[BINDING_COUNT] = 0
                poke.binding_type = None
            else:
                poke.take_damage(max(1, poke.max_hp // 16))
                self._add_text(poke.nickname + ' was hurt by ' + poke.binding_type + '!')
                poke.v_status[BINDING_COUNT] -= 1
                if not poke.v_status[BINDING_COUNT]:
                    poke.binding_type = None
        if poke.v_status[LEECH_SEED] and poke.is_alive:
            heal_amt = poke.take_damage(max(1, poke.max_hp // 8))
            self._add_text(poke.nickname + '\'s health is sapped by Leech Seed!')
            other = self.t2.current_poke if poke is self.t1.current_poke else self.t1.current_poke
            if other.is_alive:
                other.heal(heal_amt)
        if poke.v_status[NIGHTMARE] and poke.is_alive:
            poke.take_damage(max(1, poke.max_hp // 4))
            self._add_text(poke.nickname + ' is locked in a nightmare!')
        if poke.v_status[CURSE] and poke.is_alive:
            poke.take_damage(max(1, poke.max_hp // 4))
            self._add_text(poke.nickname + ' is afflicted by the curse!')

    def _victory(self, winner: tr.Trainer, loser: tr.Trainer):
        self._process_end_battle()
        self.winner = winner
        self._add_text(winner.name + " has defeated " + loser.name + "!")

    def _process_other(self, attacker: tr.Trainer, defender: tr.Trainer, a_move: tuple[str, str]):
        if a_move[ACTION_VALUE] == 'recharging':
            self._add_text(attacker.current_poke.nickname + ' must recharge!')
            attacker.current_poke.recharging = False
        if a_move[ACTION_VALUE] == 'biding':
            self._add_text(attacker.current_poke.nickname + ' is storing energy!')

    def _process_selection(self, selector: tr.Trainer):
        if selector.selection:
            selector.selection(self)
        if not selector.current_poke.is_alive:
            for p in selector.poke_list:
                if p.is_alive:
                    selector.current_poke = p
                    break
        self._add_text(selector.name + ' sent out ' + selector.current_poke.nickname + '!')

        if selector.spikes and 'flying' not in selector.current_poke.types:
            if spikes == 1:
                mult = 8
            elif spikes == 2:
                mult = 6
            else:
                mult = 4
            selector.current_poke.take_damage(selector.current_poke.max_hp // mult)
            self._add_text(selector.current_poke.nickname + ' was hurt by the spikes!')


    def _faint_check(self):
        if not self.t1_fainted and not self.t1.current_poke.is_alive:
            self._add_text(self.t1.current_poke.nickname + " fainted!")
            self.t1_fainted = True
        if not self.t2_fainted and not self.t2.current_poke.is_alive:
            self._add_text(self.t2.current_poke.nickname + " fainted!")
            self.t2_fainted = True

    def _process_end_battle(self):
        for poke in self.t1.poke_list:
            poke.battle_end_reset()
        for poke in self.t2.poke_list:
            poke.battle_end_reset()
        self.t1.in_battle = False
        self.t2.in_battle = False

    def _add_text(self, txt: str):
        self.all_text.append(txt)
        self.cur_text.append(txt)

    def _pop_text(self):
        self.all_text.pop()
        self.cur_text.pop()

    def is_finished(self) -> bool:
        return not not self.winner