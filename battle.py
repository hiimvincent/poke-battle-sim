from __future__ import annotations
import random
import pokemon as pk
import trainer as tr
import move
import battlefield as bf
import process_move as pm
import global_settings as gs
import global_data as gd
import process_ability as pa
import process_item as pi

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
        self.battlefield = bf.Battlefield(self)
        self.battle_started = True
        self.winner = None
        self.last_move = None
        self.last_move_next = None
        self.turn_count = 0
        self._add_text(self.t1.name + ' sent out ' + self.t1.current_poke.nickname + '!')
        self._add_text(self.t2.name + ' sent out ' + self.t2.current_poke.nickname + '!')

    def turn(self, t1_turn: list[str], t2_turn: list[str]) -> bool | None:
        self.turn_count += 1
        if not self.battle_started:
            raise Exception
        if self.is_finished():
            return

        t1_move = t1_turn.copy()
        t2_move = t2_turn.copy()
        t1_move_data = None
        t2_move_data = None
        t1_mv_check_bypass = False
        t2_mv_check_bypass = False
        t1_first = None

        if self.t1.current_poke.recharging:
            t1_move = gd.RECHARGING
        elif self.t1.current_poke.bide_count:
            t1_move = gd.BIDING
        elif self.t1.current_poke.rage:
            t1_move = gd.RAGE
            t1_mv_check_bypass = True
        elif self.t1.current_poke.uproar:
            t1_move = gd.UPROAR
            t1_mv_check_bypass = True
        elif not self.t1.current_poke.next_moves.empty():
            t1_move_data = self.t1.current_poke.next_moves.get()
            t1_move = [gd.MOVE, t1_move_data.name]
            t1_mv_check_bypass = True
        elif self.t1.current_poke.encore_count:
            t1_move_data = self.t1.current_poke.encore_move
            t1_move = [gd.MOVE, t1_move_data.name]
            if t1_move_data.disabled:
                t1_move = gd.STRUGGLE
                t1_move_data = None
                t1_mv_check_bypass = True
        elif t1_move[gs.ACTION_TYPE] == gd.MOVE and self.t1.current_poke.no_pp():
            t1_move = gd.STRUGGLE
            t1_mv_check_bypass = True
        if self.t2.current_poke.recharging:
            t2_move = gd.RECHARGING
        elif self.t2.current_poke.bide_count:
            t2_move = gd.BIDING
        elif self.t2.current_poke.rage:
            t2_move = gd.RAGE
            t2_mv_check_bypass = True
        elif self.t2.current_poke.uproar:
            t2_move = gd.UPROAR
            t2_mv_check_bypass = True
        elif not self.t2.current_poke.next_moves.empty():
            t2_move_data = self.t2.current_poke.next_moves.get()
            t2_move = [gd.MOVE, t2_move_data.name]
            t2_mv_check_bypass = True
        elif self.t2.current_poke.encore_count:
            t2_move_data = self.t2.current_poke.encore_move
            t2_move = [gd.MOVE, t2_move_data.name]
            if t2_move_data.disabled:
                t2_move = gd.STRUGGLE
                t2_move_data = None
                t2_mv_check_bypass = True
        elif t2_move[gs.ACTION_TYPE] == gd.MOVE and self.t2.current_poke.no_pp():
            t2_move = gd.STRUGGLE
            t2_mv_check_bypass = True

        if not isinstance(t1_move, list) or not all(isinstance(t1_move[i], str) for i in range(len(t1_move))) or len(t1_move) < 2:
            raise Exception
        if not isinstance(t2_move, list) or not all(isinstance(t2_move[i], str) for i in range(len(t2_move))) or len(t2_move) < 2:
            raise Exception

        self.t1.has_moved = False
        self.t2.has_moved = False
        t1_move = [e.lower() for e in t1_move]
        t2_move = [e.lower() for e in t2_move]
        self.t1_fainted = False
        self.t2_fainted = False
        self.t1.current_poke.turn_damage = False
        self.t2.current_poke.turn_damage = False

        if t1_move[gs.ACTION_TYPE] not in gs.ACTION_PRIORITY or t2_move[gs.ACTION_TYPE] not in gs.ACTION_PRIORITY:
            raise Exception
        if t1_move[gs.ACTION_TYPE] == gd.MOVE and not t1_mv_check_bypass and not self.t1.current_poke.is_move(t1_move[gs.ACTION_VALUE]):
            raise Exception
        if t2_move[gs.ACTION_TYPE] == gd.MOVE and not t2_mv_check_bypass and not self.t2.current_poke.is_move(t2_move[gs.ACTION_VALUE]):
            raise Exception

        if not t1_move_data and t1_move[gs.ACTION_TYPE] == gd.MOVE:
            t1_move_data = self.t1.current_poke.get_move_data(t1_move[gs.ACTION_VALUE])
        if not t2_move_data and t2_move[gs.ACTION_TYPE] == gd.MOVE:
            t2_move_data = self.t2.current_poke.get_move_data(t2_move[gs.ACTION_VALUE])

        t1_prio = gs.ACTION_PRIORITY[t1_move[gs.ACTION_TYPE]]
        t2_prio = gs.ACTION_PRIORITY[t2_move[gs.ACTION_TYPE]]
        t1_first = t1_prio >= t2_prio
        if t1_prio == 1 and t2_prio == 1:
            if t1_move_data.prio != t2_move_data.prio:
                t1_first = t1_move_data.prio > t2_move_data.prio
            else:
                spd_dif = self.t1.current_poke.stats_effective[gs.SPD] - self.t2.current_poke.stats_effective[gs.SPD]
                if spd_dif == 0:
                    t1_first = random.randrange(2) < 1
                else:
                    t1_first = spd_dif > 0
                    if self.battlefield.trick_room_count:
                        t1_first = not t1_first
                    if self._stall_check():
                        t1_first = self._calculate_stall()

        self._add_text("Turn " + str(self.turn_count) + ":")

        if self._pursuit_check(t1_move, t2_move, t1_move_data, t2_move_data, t1_first):
            t1_first = t1_move == gd.PURSUIT

        if self._me_first_check(t1_move_data, t2_move_data):
            t1_first = t1_move == gd.ME_FIRST

        self._focus_punch_check(t1_move, t2_move)

        if t1_first:
            if self.t1.current_poke.is_alive:
                # trainer 1 turn
                self._half_turn(self.t1, self.t2, t1_move, t1_move_data)
            self._faint_check()
            if self.t2.current_poke.is_alive:
                # trainer 2 turn
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

        if self.winner:
            return
        self.battlefield.update()

        dif = self.t1.current_poke.stats_effective[gs.SPD] - self.t2.current_poke.stats_effective[gs.SPD]
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
        if self.winner:
            return
        if not faster.current_poke.is_alive:
            self._process_selection(faster)
        if slower.current_poke.is_alive:
            self._post_process_status(slower, faster)
        self._faint_check()
        if self.winner:
            return
        if not slower.current_poke.is_alive:
            self._process_selection(slower)

    def get_cur_text(self) -> list:
        cur_t = self.cur_text
        self.cur_text = []
        return cur_t

    def get_all_text(self) -> list:
        return self.all_text

    def _half_turn(self, attacker: tr.Trainer, defender: tr.Trainer, a_move: list[str], a_move_data: Move = None):
        if self.winner:
            return
        if a_move[gs.ACTION_TYPE] == 'other':
            self._process_other(attacker, defender, a_move)
        elif a_move[gs.ACTION_TYPE] == 'item':
            if len(a_move) >= 4:
                pi.use_item(a_move[gs.ACTION_VALUE], a_move[gs.ITEM_POKE_TARGET], a_move[gs.ITEM_MOVE_TARGET])
            elif len(a_move) == 3:
                pi.use_item(a_move[gs.ACTION_VALUE], a_move[gs.ITEM_POKE_TARGET])
            else:
                raise Exception
        elif self._process_pp(attacker.current_poke, a_move_data):
            pm.process_move(attacker.current_poke, defender.current_poke, self.battlefield, self, a_move_data.get_tcopy(), not defender.has_moved)
            if self.last_move_next:
                self.last_move, self.last_move_next = self.last_move_next, None
            attacker.current_poke.update_last_moves()
        attacker.has_moved = True

    def _process_pp(self, attacker: pk.Pokemon, move_data: Move) -> bool:
        if move_data.name == 'struggle':
            return True
        if move_data.cur_pp <= 0:
            raise Exception
        is_disabled = move_data.disabled
        attacker.reduce_disabled_count()
        if is_disabled:
            self._add_text(move_data.name + ' is disabled!')
            return False
        move_data.cur_pp -= 1
        self._pressure_check(attacker, move_data)
        if move_data.cur_pp == 0 and attacker.copied and move_data.name == attacker.copied.name:
            attacker.copied = None
        return True

    def _post_process_status(self, trainer: tr.Trainer, other: tr.Trainer):
        poke = trainer.current_poke
        if trainer.wish:
            trainer.wish -= 1
            if not trainer.wish:
                self._add_text(trainer.wish_poke + '\'s wish came true!')
                trainer.current_poke.heal(trainer.current_poke.max_hp // 2)
                trainer.wish_poke = None
        if poke.v_status[gs.INGRAIN]:
            self._add_text(poke.nickname + ' absorbed nutrients with its roots!')
            poke.heal(poke.max_hp // 16, text_skip=True)
        if poke.v_status[gs.AQUA_RING]:
            self._add_text('A veil of water restored ' + poke.nickname + '\'s HP!')
            poke.heal(poke.max_hp // 16, text_skip=True)
        if self.battlefield.weather == gs.RAIN and poke.has_ability('rain-dish'):
            poke.heal(poke.max_hp // 16)
        if trainer.fs_count and poke.is_alive:
            trainer.fs_count -= 1
            if not trainer.fs_count:
                poke.take_damage(trainer.fs_dmg)
                self._add_text(poke.nickname + ' took the Future Sight attack!')
        if trainer.dd_count and poke.is_alive:
            trainer.dd_count -= 1
            if not trainer.dd_count:
                poke.take_damage(trainer.dd_dmg)
                self._add_text(poke.nickname + ' took the Doom Desire attack!')
        if trainer.reflect:
            trainer.reflect -= 1
        if trainer.light_screen:
            trainer.light_screen -= 1
            self._add_text(trainer.name + '\'s Light Screen wore off.')
        if trainer.safeguard:
            trainer.safeguard -= 1
            if not trainer.safeguard:
                self._add_text(trainer.name + ' is no longer protected by Safeguard.')
        if trainer.mist:
            trainer.mist -= 1
            if not trainer.mist:
                self._add_text(trainer.name + ' is no longer protected by mist!')
        if trainer.tailwind_count:
            trainer.tailwind_count -= 1
            if not trainer.tailwind_count:
                self._add_text(trainer.name + '\'s ' + 'tailwind petered out!')
                for poke in trainer.poke_list:
                    poke.stats_actual[gs.SPD] //= 2
        if trainer.lucky_chant:
            trainer.lucky_chant -= 1
            if not trainer.lucky_chant:
                self._add_text(trainer.name + '\'s Lucky Chant wore off!')
        if trainer.imprisoned_poke and not trainer.imprisoned_poke is other.current_poke:
            trainer.imprisoned_poke = None
        if poke.perish_count and poke.is_alive:
            poke.perish_count -= 1
            if not poke.perish_count:
                poke.faint()
                return

        if not poke.is_alive:
            return

        if poke.nv_status and ((poke.has_ability('shed-skin') and random.randrange(10) < 3) \
                or (poke.has_ability('hydration') and self.battlefield.weather == gs.RAIN)):
            pm._cure_nv_status(poke.nv_status, poke, battle)
        if poke.nv_status == gs.BURNED and poke.is_alive:
            self._add_text(poke.nickname + ' was hurt by its burn!')
            if not poke.has_ability('heatproof'):
                poke.take_damage(max(1, poke.max_hp // 8))
            else:
                poke.take_damage(max(1, poke.max_hp // 16))
        if poke.nv_status == gs.POISONED and poke.is_alive:
            if not poke.has_ability('poison-heal'):
                self._add_text(poke.nickname + ' was hurt by poison!')
                poke.take_damage(max(1, poke.max_hp // 8))
            else:
                self._add_text(poke.nickname + ' was healed by its Poison Heal!')
                poke.heal(max(1, poke.max_hp // 8))
        if poke.nv_status == gs.BADLY_POISONED and poke.is_alive:
            if not poke.has_ability('poison-heal'):
                self._add_text(poke.nickname + ' was hurt by poison!')
                poke.take_damage(max(1, poke.max_hp * poke.nv_counter // 16))
            else:
                self._add_text(poke.nickname + ' was healed by its Poison Heal!')
                poke.heal(max(1, poke.max_hp // 8))
            poke.nv_counter += 1
        if poke.v_status[gs.BINDING_COUNT] and poke.is_alive:
            if poke.binding_poke is other.current_poke and poke.binding_type:
                self._add_text(poke.nickname + ' is hurt by ' + poke.binding_type + '!')
                poke.take_damage(max(1, poke.max_hp // 16))
                if not poke.is_alive:
                    return
                poke.v_status[gs.BINDING_COUNT] -= 1
                if not poke.v_status[gs.BINDING_COUNT]:
                    poke.binding_type = None
                    poke.binding_poke = None
            else:
                poke.v_status[gs.BINDING_COUNT] = 0
                poke.binding_type = None
                poke.binding_poke = None
        if poke.v_status[gs.LEECH_SEED] and poke.is_alive:
            self._add_text(poke.nickname + '\'s health is sapped by Leech Seed!')
            heal_amt = poke.take_damage(max(1, poke.max_hp // 8))
            other = self.t2.current_poke if poke is self.t1.current_poke else self.t1.current_poke
            if other.is_alive:
                if not poke.has_ability('liquid-ooze'):
                    other.heal(heal_amt)
                else:
                    other.take_damage(heal_amt)
                    self._add_text(other.nickname + ' sucked up the liquid ooze!')
        if poke.v_status[gs.NIGHTMARE] and poke.is_alive:
            self._add_text(poke.nickname + ' is locked in a nightmare!')
            poke.take_damage(max(1, poke.max_hp // 4))
        if poke.v_status[gs.CURSE] and poke.is_alive:
            self._add_text(poke.nickname + ' is afflicted by the curse!')
            poke.take_damage(max(1, poke.max_hp // 4))
        if poke.has_ability('solar-power'):
            self._add_text(poke.nickname + 'was hurt by its Solar Power!')
            poke.take_damage(max(1, poke.max_hp // 8))
        if not poke.is_alive:
            return

        if self.battlefield.weather == gs.SANDSTORM and poke.is_alive and not poke.has_ability('sand-veil') and \
                not poke.in_ground and not poke.in_water and not any(type in poke.types for type in ['ground', 'steel', 'rock']):
            self._add_text(poke.nickname + ' is buffeted by the Sandstorm!')
            poke.take_damage(max(1, poke.max_hp // 16))
        if self.battlefield.weather == gs.HAIL and poke.is_alive and not poke.has_ability('ice-body'):
            if not poke.in_ground and not poke.in_water and not any(type in poke.types for type in ['ice']):
                self._add_text(poke.nickname + ' is buffeted by the Hail!')
                poke.take_damage(max(1, poke.max_hp // 16))
        if self.battlefield.weather == gs.HAIL and poke.is_alive and poke.has_ability('ice-body'):
            self._add_text(poke.nickname + ' was healed by its Ice Body!')
            poke.heal(max(1, poke.max_hp // 16), text_skip=True)
        if self.battlefield.weather == gs.RAIN and poke.is_alive and poke.has_ability('dry-skin'):
            self._add_text(poke.nickname + ' was healed by its Dry Skin!')
            poke.heal(max(1, poke.max_hp // 8), text_skip=True)
        if self.battlefield.weather == gs.HARSH_SUNLIGHT and poke.is_alive and poke.has_ability('dry-skin'):
            self._add_text(poke.nickname + ' was hurt by its Dry Skin!')
            poke.take_damage(max(1, poke.max_hp // 8))

        if not poke.is_alive:
            return

        pa.end_turn_abilities(poke, self)

        if poke.v_status[gs.FLINCHED]:
            poke.v_status[gs.FLINCHED] = 0
        if poke.foresight_target and not poke.foresight_target is other.current_poke:
            poke.foresight_target = None
        if poke.bide_count:
            poke.bide_count -= 1
        if poke.mr_count:
            poke.mr_count -= 1
        if poke.db_count:
            poke.db_count -= 1
            if not poke.mr_count:
                poke.mr_target = None
        if poke.charged:
            poke.charged -= 1
        if poke.taunt:
            poke.taunt -= 1
        if poke.r_types:
            poke.types = poke.r_types
            poke.r_types = None
        if poke.encore_count:
            poke.encore_count -= 1
            if not poke.encore_count:
                poke.encore_move = None
                for move in poke.moves:
                    move.encore_blocked = False
                    self._add_text(poke.nickname + '\'s encore ended.')
        if poke.embargo_count:
            poke.embargo_count -= 1
            if not poke.encore_count:
                self._add_text(poke.nickname + ' can use items again!')
        if poke.hb_count:
            poke.hb_count -= 1
            if not poke.hb_count:
                self._add_text(poke.nickname + '\'s Heal Block wore off!')
        if poke.uproar:
            poke.uproar -= 1
            if not poke.uproar:
                self._add_text(poke.nickname + ' calmed down.')
        if poke.protect:
            poke.protect = False
            poke.invulnerable = False
            if poke.last_successful_move not in ['protect', 'detect', 'endure']:
                poke.protect_count = 0
        if poke.endure:
            poke.endure = False
            if poke.last_successful_move not in ['protect', 'detect', 'endure']:
                poke.protect_count = 0
        if poke.magic_coat:
            poke.magic_coat = False
        if poke.snatch:
            poke.snatch = False
        if poke.sp_check:
            poke.sp_check = False
        if not poke.has_moved:
            poke.has_moved = True
        if poke.v_status[gs.DROWSY]:
            poke.v_status[gs.DROWSY] -= 1
            if not poke.v_status[gs.DROWSY] and not poke.nv_status:
                poke.nv_status = gs.ASLEEP
                self._add_text(poke.nickname + ' fell asleep!')

    def _victory(self, winner: tr.Trainer, loser: tr.Trainer):
        self._process_end_battle()
        self._add_text(winner.name + ' has defeated ' + loser.name + '!')
        self.winner = winner

    def _process_other(self, attacker: tr.Trainer, defender: tr.Trainer, a_move: list[str]):
        if a_move[gs.ACTION_VALUE] == 'recharging':
            self._add_text(attacker.current_poke.nickname + ' must recharge!')
            attacker.current_poke.recharging = False
        if a_move[gs.ACTION_VALUE] == 'biding':
            self._add_text(attacker.current_poke.nickname + ' is storing energy!')

    def _process_selection(self, selector: tr.Trainer) -> bool:
        old_poke = selector.current_poke
        if selector.selection:
            selector.selection(self)
        if not selector.current_poke.is_alive or selector.current_poke is old_poke:
            for p in selector.poke_list:
                if p.is_alive and not p is old_poke:
                    selector.current_poke = p
                    break
        if not selector.current_poke.is_alive or selector.current_poke is old_poke:
            return True
        self._add_text(selector.name + ' sent out ' + selector.current_poke.nickname + '!')

        if self.battlefield.gravity_count:
            selector.current_poke.grounded = True
        if selector.spikes and (selector.current_poke.grounded or ('flying' not in selector.current_poke.types \
                and not selector.current_poke.magnet_rise and not selector.current_poke.has_ability('levitate') \
                and not selector.current_poke.has_ability('magic-guard'))):
            if selector.spikes == 1:
                mult = 8
            elif selector.spikes == 2:
                mult = 6
            else:
                mult = 4
            selector.current_poke.take_damage(selector.current_poke.max_hp // mult)
            self._add_text(selector.current_poke.nickname + ' was hurt by the spikes!')
        if selector.toxic_spikes and 'poison' in selector.current_poke.types:
            selector.toxic_spikes = 0
            self._add_text('The poison spikes disappeared from the ground around ' + selector.name + '.')
        if selector.toxic_spikes and not selector.current_poke.nv_status and (selector.current_poke.grounded \
                    or (not 'flying' in selector.current_poke.types and not 'steel' in selector.current_poke.types \
                    and not selector.current_poke.magnet_rise and not selector.current_poke.has_ability('immunity') \
                    and not selector.current_poke.has_ability('levitate') and not selector.current_poke.has_ability('magic-guard') \
                    and not (selector.current_poke.has_ability('leaf-guard') and battlefield.weather == gs.HARSH_SUNLIGHT))):
            if selector.toxic_spikes == 1:
                selector.current_poke.nv_status = gs.POISONED
                self._add_text(selector.current_poke.nickname + ' was poisoned!')
            else:
                selector.current_poke.nv_status = gs.BADLY_POISONED
                selector.current_pokenv_counter = 1
                self._add_text(selector.current_poke.nickname + ' was badly poisoned!')
        if selector.stealth_rock and not selector.current_poke.has_ability('magic-guard'):
            t_mult = PokeSim.get_type_effectiveness('rock', selector.current_poke.types[0])
            if selector.current_poke.types[1]:
                t_mult *= PokeSim.get_type_effectiveness('rock', selector.current_poke.types[1])
            if t_mult:
                selector.current_poke.take_damage(int(selector.current_poke.max_hp * 0.125 * t_mult))
                self._add_text('Pointed stones dug into ' + selector.current_poke.nickname + '!')

        pa.enemy_selection_abilities(selector.current_poke, self.battlefield, self)
        pa.selection_abilities(selector.current_poke, self.battlefield, self)
        return False

    def _faint_check(self):
        if self.winner:
            return
        if not self.t1_fainted and not self.t1.current_poke.is_alive:
            self._add_text(self.t1.current_poke.nickname + " fainted!")
            self.t1_fainted = True
            self.t1.num_fainted += 1
            if self.t1.num_fainted == len(self.t1.poke_list):
                self._victory(self.t2, self.t1)
                return
        if not self.t2_fainted and not self.t2.current_poke.is_alive:
            self._add_text(self.t2.current_poke.nickname + " fainted!")
            self.t2_fainted = True
            self.t2.num_fainted += 1
            if self.t2.num_fainted == len(self.t2.poke_list):
                self._victory(self.t1, self.t2)
                return

    def _process_end_battle(self):
        for poke in self.t1.poke_list:
            poke.battle_end_reset()
        for poke in self.t2.poke_list:
            poke.battle_end_reset()
        self.t1.in_battle = False
        self.t2.in_battle = False

    def _pursuit_check(self, t1_move: list[str], t2_move: list[str], t1_move_data: Move, t2_move_data: Move, t1_first: bool) -> bool:
        if t1_move == gd.PURSUIT and (t2_move == gd.SWITCH or (t2_move[gs.ACTION_TYPE] == gd.MOVE and t2_move[gs.ACTION_VALUE] in gd.PURSUIT_CHECK and not t1_first)):
            t1_move_data.cur_pp -= 1
            self._pressure_check(t1.current_poke, t1_move_data)
            t1_move_data = t1_move_data.get_tcopy()
            t1_move_data.power *= 2
            return True
        elif t2_move == gd.PURSUIT and (t1_move == gd.SWITCH or (t1_move[gs.ACTION_TYPE] == gd.MOVE and t1_move[gs.ACTION_VALUE] in gd.PURSUIT_CHECK and t1_first)):
            t2_move_data.cur_pp -= 1
            self._pressure_check(t2.current_poke, t2_move_data)
            t2_move_data = t2_move_data.get_tcopy()
            t2_move_data.power *= 2
            return True
        return False

    def _me_first_check(self, t1_move_data: Move, t2_move_data: Move) -> bool:
        if not t1_move_data or not t2_move_data:
            return False
        if t1_move_data.name == 'me-first' and t2_move_data.category != gs.STATUS:
            self.t1.current_poke.mf_move = t2_move_data.get_tcopy()
            return True
        if t2_move_data.name == 'me-first' and t1_move_data.category != gs.STATUS:
            self.t2.current_poke.mf_move = t1_move_data.get_tcopy()
            return True
        return False

    def _focus_punch_check(self, t1_move: list[str], t2_move: list[str]):
        if t1_move == gd.FOCUS_PUNCH:
            self._add_text(self.t1.current_poke.nickname + ' is tightening its focus!')
        if t2_move == gd.FOCUS_PUNCH:
            self._add_text(self.t2.current_poke.nickname + ' is tightening its focus!')

    def _stall_check(self) -> bool:
        return self.t1.current_poke.has_ability('stall') or self.t2.current_poke.has_ability('stall')

    def _calculate_stall(self) -> bool:
        if self.t1.current_poke.has_ability('stall') and self.t2.current_poke.has_ability('stall'):
            if self.t1.current_poke.stats_effective[gs.SPD] != self.t2.current_poke.stats_effective[gs.SPD]:
                return self.t1.current_poke.stats_effective[gs.SPD] < self.t2.current_poke.stats_effective[gs.SPD]
            else:
                return random.randrange(2) < 1
        return self.t2.current_poke.has_ability('stall')

    def _sucker_punch_check(self, t1_move_data: Move, t2_move_data: Move):
        if not t1_move_data or not t2_move_data:
            return
        if t1_move_data.name == 'sucker-punch' and t2_move_data.category != gs.STATUS:
            self.t1.current_poke.sp_check = True
        if t2_move_data.name == 'sucker-punch' and t1_move_data.category != gs.STATUS:
            self.t1.current_poke.sp_check = True

    def _pressure_check(self, attacker: pk.Pokemon, move_data: Move):
        if move_data.cur_pp and attacker.enemy.current_poke.is_alive and attacker.enemy.current_poke.has_ability('pressure'):
            move_data.cur_pp -= 1

    def _add_text(self, txt: str):
        if not self.winner:
            self.all_text.append(txt)
            self.cur_text.append(txt)

    def _pop_text(self):
        self.all_text.pop()
        self.cur_text.pop()

    def is_finished(self) -> bool:
        return not not self.winner