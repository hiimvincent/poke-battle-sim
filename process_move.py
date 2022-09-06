from __future__ import annotations
import pokemon as pk
import battlefield as bf
import battle as bt
from poke_sim import PokeSim
from move import Move
import random

STATUS = 1
PHYSICAL = 2
SPECIAL = 3

BURNED = 1
FROZEN = 2
PARALYZED = 3
POISONED = 4
ASLEEP = 5
BADLY_POISONED = 5

CONFUSED = 0
FLINCHED = 1
LEECH_SEED = 2

BINDING_COUNT = 3
BIND = 1
WRAP = 2
FIRE_SPIN = 3
CLAMP = 4
WHIRLPOOL = 5

NIGHTMARE = 4
CURSE = 5
DROWSY = 6

CLEAR = 0
HARSH_SUNLIGHT = 1
RAIN = 2
SANDSTORM = 3
HAIL = 4
FOG = 5

# STAT_ORDERING_FORMAT
HP = 0
ATK = 1
DEF = 2
SP_ATK = 3
SP_DEF = 4
SPD = 5
STAT_NUM = 6
ACC = 6
EVA = 7

STAT_TO_NAME = {
    0: 'Health',
    1: 'Attack',
    2: 'Defense',
    3: 'Sp. Atk',
    4: 'Sp. Def',
    5: 'Speed',
    6: 'accuracy',
    7: 'evasion'
}

METRONOME_CHECK = ['assist', 'chatter', 'copycat', 'counter', 'covet', 'destiny-bond', 'detect', 'endure', 'feint',
                   'focus-punch', 'follow-me', 'helping-hand', 'me-first', 'mimic', 'mirror-coat', 'mirror-move',
                   'protect', 'sketch', 'sleep-talk', 'snatch', 'struggle', 'switcheroo', 'thief', 'trick']

ENCORE_CHECK = ['transform', 'mimic', 'sketch', 'mirror-move', 'sleep-talk', 'encore', 'struggle']

ASSIST_CHECK = ['chatter', 'copycat', 'counter', 'covet', 'destiny-bond', 'detect', 'endure', 'feint', 'focus-punch',
                'follow-me', 'helping-hand', 'me-first', 'metronome', 'mimic', 'mirror-coat', 'mirror-move', 'protect'
                'sketch', 'sleep-talk', 'snatch', 'struggle', 'switcheroo', 'thief', 'trick']

MAGIC_COAT_CHECK = ['attract', 'block', 'captivate', 'charm', 'confuse-ray', 'cotton-spore', 'dark-void', 'fake-tears',
                    'feather-dance', 'flash', 'flatter', 'gastro-acid', 'glare', 'grass-whistle', 'growl', 'hypnosis',
                    'kinesis', 'leech-seed', 'leer', 'lovely-kiss', 'mean-look', 'metal-sound', 'poison-gas', 'poison-powder',
                    'sand-attack', 'scary-face', 'screech', 'sing', 'sleep-powder', 'smokescreen', 'spider-web', 'spore',
                    'string-shot', 'stun-spore', 'supersonic', 'swagger', 'sweet-kiss', 'sweet-scent', 'tail-whip',
                    'thunder-wave', 'tickle', 'toxic', 'will-o-wisp', 'worry-seed', 'yawn']

SNATCH_CHECK = ['acid-armor', 'acupressure', 'agility', 'amnesia', 'aromatherapy', 'barrier', 'belly-drum', 'bulk-up',
                'calm-mind', 'camouflage', 'charge', 'cosmic-power', 'defender-order', 'defender-curl', 'double-team',
                'dragon-dance', 'focus-energy', 'growth', 'harden', 'heal-bell', 'heal-order', 'howl', 'ingrain',
                'iron-defense', 'light-screen', 'meditate', 'milk-drink', 'minimize', 'mist', 'moonlight', 'morning-sun',
                'nasty-plot', 'psych-up', 'recover', 'reflect', 'refresh', 'rest', 'rock-polish', 'roost', 'safeguard',
                'sharpen', 'slack-off', 'soft-boiled', 'stockpile', 'substitute', 'swallow', 'swords-dance', 'synthesis',
                'tail-glow', 'tailwind', 'withdraw']


PROTECT_TARGETS = [8, 9, 10, 11]

def process_move(attacker: pk.Pokemon, defender: pk.Pokemon, battlefield: bf.Battlefield, battle: bt.Battle, move_data: Move, is_first: bool):
    if _pre_process_status(attacker, defender, battlefield, battle, move_data):
        return
    battle._add_text(attacker.nickname + ' used ' + _cap_name(move_data.name) + '!')
    attacker.last_move_next = move_data
    if not _calculate_hit_or_miss(attacker, defender, battlefield, battle, move_data):
        return
    attacker.last_successful_move_next = move_data
    if _magic_coat_check(attacker, defender, battlefield, battle, move_data, is_first):
        return
    if _snatch_check(attacker, defender, battlefield, battle, move_data, is_first):
        return
    if _protect_check(defender, battle, move_data):
        return
    _process_effect(attacker, defender, battlefield, battle, move_data, is_first)
    battle._faint_check()

def _calculate_type_ef(defender: pokemon.Pokemon, move_data: list):
    if move_data.type == 'typeless':
        return 1
    if move_data.type == 'ground' and 'flying' in defender.types and defender.grounded:
        return 1
    t_mult = PokeSim.get_type_effectiveness(move_data.type, defender.types[0])
    if defender.types[1]:
        t_mult *= PokeSim.get_type_effectiveness(move_data.type, defender.types[1])
    return t_mult

def _calculate_damage(attacker: pokemon.Pokemon, defender: pokemon.Pokemon, battlefield: bf.Battlefield, battle: bt.Battle,
                      move_data: Move, crit_chance: int = None, inv_bypass: bool = False, skip_fc: bool = False, skip_dmg: bool = False) -> int:
    if move_data.category == STATUS:
        return
    if not defender.is_alive:
        _missed(attacker, battle)
        return
    if not inv_bypass and _invulnerability_check(attacker, defender, battlefield, battle, move_data):
        return
    if not move_data.power:
        return
    t_mult = _calculate_type_ef(defender, move_data)
    if t_mult == 0:
        battle._add_text("It doesn't affect " + defender.nickname)
        return

    cc = crit_chance + attacker.crit_stage if crit_chance else attacker.crit_stage
    if _calculate_crit(cc):
        crit_mult = 2
        battle._add_text("A critical hit!")
    else:
        crit_mult = 1

    if t_mult < 1:
        battle._add_text("It's not very effective...")
    elif t_mult > 1:
        battle._add_text("It's super effective!")

    attacker.calculate_stats_effective()
    defender.calculate_stats_effective()

    if move_data.category == PHYSICAL:
        if crit_mult == 1:
            ad_ratio = attacker.stats_effective[ATK] / defender.stats_effective[DEF]
            if defender.trainer.reflect:
                ad_ratio /= 2
        else:
            atk_ig = max(attacker.stats_actual[ATK], attacker.stats_effective[ATK])
            def_ig = min(defender.stats_actual[DEF], defender.stats_effective[DEF])
            ad_ratio = atk_ig / def_ig
    else:
        if crit_mult == 1:
            ad_ratio = attacker.stats_effective[SP_ATK] / defender.stats_effective[SP_DEF]
            if defender.trainer.light_screen:
                ad_ratio /= 2
        else:
            sp_atk_ig = max(attacker.stats_actual[SP_ATK], attacker.stats_effective[SP_ATK])
            sp_def_ig = min(defender.stats_actual[SP_DEF], defender.stats_effective[SP_DEF])
            ad_ratio = sp_atk_ig / sp_def_ig
    if attacker.nv_status == BURNED:
        burn = 0.5
    else:
        burn = 1
    if attacker.charged and move_data.type == 'electric':
        move_data.power *= 2
    screen = 1
    targets = 1
    weather_mult = 1
    ff = 1
    if move_data.type == attacker.types[0] or move_data.type == attacker.types[1]:
        stab = 1.5
    else:
        stab = 1
    random_mult = random.randrange(85, 101) / 100

    eb = 1
    tl = 1
    srf = 1
    berry_mult = 1
    item_mult = 1
    first = 1

    damage = ((2 * attacker.level / 5 + 2) * move_data.power * ad_ratio) / 50 * burn * screen * targets * weather_mult * ff + 2
    damage *= crit_mult * item_mult * first * random_mult * stab * t_mult * srf * eb * tl * berry_mult
    damage = int(damage)
    if skip_dmg:
        return damage
    damage_done = defender.take_damage(damage, move_data)
    if not skip_fc:
        battle._faint_check()
    return damage_done

def _calculate_hit_or_miss(attacker: pokemon.Pokemon, defender: pokemon.Pokemon, battlefield: bf.Battlefield, battle: bt.Battle, move_data: Move):
    d_eva_stage = defender.evasion_stage
    if attacker.foresight_target and attacker.foresight_target is defender:
         if defender.evasion_stage > 0:
             d_eva_stage = 0
    stage = attacker.accuracy_stage - d_eva_stage
    stage_mult = max(3, 3 + stage) / max(3, 3 - stage)

    item_mult = 1
    ability_mult = 1
    ma = move_data.acc
    if _special_move_acc(attacker, defender, battlefield, battle, move_data):
        return True
    if not ma:
        return True
    if defender.mr_count and defender.mr_target and attacker is defender.mr_target:
        return True
    if ma == -1:
        res = random.randrange(1, 101) <= attacker.level - defender.level + 30
    else:
        hit_threshold = ma * stage_mult * battlefield.acc_modifier * item_mult * ability_mult
        res = random.randrange(1, 101) <= hit_threshold
    if not res:
        if defender.evasion_stage > 0:
            battle._add_text(defender.nickname + ' avoided the attack!')
        else:
            _missed(attacker, battle)
    return res


def _process_effect(attacker: pokemon.Pokemon, defender: pokemon.Pokemon, battlefield: bf.Battlefield, battle: bt.Battle, move_data: Move, is_first: bool):
    if move_data.ef_chance:
        ef_pr = move_data.ef_chance
    else:
        ef_pr = 100
    if random.randrange(1, 101) > ef_pr:
        return True

    ef_id = move_data.ef_id

    if ef_id & 1:
        recipient = defender
    else:
        recipient = attacker

    crit_chance = None
    inv_bypass = False

    if ef_id == 0 or ef_id == 1:
        _calculate_damage(attacker, defender, battlefield, battle, move_data)
        return
    elif ef_id == 2 or ef_id == 3:
        _calculate_damage(attacker, defender, battlefield, battle, move_data)
        if not recipient.is_alive:
            return
        _give_stat_change(recipient, battle, move_data.ef_stat, move_data.ef_amount)
    elif ef_id == 4 or ef_id == 5:
        _calculate_damage(attacker, defender, battlefield, battle, move_data)
        if recipient.is_alive:
            _give_nv_status(move_data.ef_stat, recipient, battle)
        return
    elif ef_id == 6 or ef_id == 7:
        if not recipient.is_alive:
            _failed(battle)
            return
        if move_data.ef_stat == FLINCHED:
            _flinch(recipient, is_first)
        else:
            _confuse(recipient, battle)
    elif ef_id == 8:
        crit_chance = move_data.ef_amount
    elif ef_id == 10:
        if not defender.is_alive:
            _missed(attacker, battle)
        num_hits = _generate_2_to_5()
        nh = num_hits
        while nh and defender.is_alive:
            _calculate_damage(attacker, defender, battlefield, battle, move_data, skip_fc=True)
            nh -= 1
        battle._add_text("Hit " + str(num_hits) + " time(s)!")
        return
    elif ef_id == 11:
        if not defender.is_alive:
            _missed(attacker, battle)
        _calculate_damage(attacker, defender, battlefield, battle, move_data, skip_fc=True)
        if defender.is_alive:
            _calculate_damage(attacker, defender, battlefield, battle, move_data, skip_fc=True)
        else:
            battle._add_text("Hit 1 time(s)!")
            return
        battle._add_text("Hit 2 time(s)!")
        return
    elif ef_id == 13:
        if recipient.is_alive:
            _give_nv_status(move_data.ef_stat, recipient, battle, True)
        else:
            _failed(battle)
        return
    elif ef_id == 14:
        if not defender.is_alive:
            return
        if move_data.ef_stat == CONFUSED:
            _confuse(defender, battle, True)
    elif ef_id == 16 or ef_id == 17:
        if ef_id == 17 and defender.mist_count:
            battle._add_text(defender.nickname + '\'s protected by mist.')
            return
        _give_stat_change(recipient, battle, move_data.ef_stat, move_data.ef_amount)
    elif ef_id == 18:
        if defender.in_water:
            move_data.power *= 2
            inv_bypass = True
    elif ef_id == 19:
        if defender.minimized:
            move_data.power *= 2
        _calculate_damage(attacker, defender, battlefield, battle, move_data)
        if random.randrange(10) < 3:
            _flinch(defender, is_first)
    elif ef_id == 20:
        if not defender.is_alive:
            _missed(attacker, battle)
        if _calculate_type_ef(defender, move_data) != 0:
            defender.take_damage(65535, move_data)
            if not defender.is_alive:
                battle._add_text('It\'s a one-hit KO!')
        else:
            battle._add_text('It doesn\'t affect ' + defender.nickname)
        return
    elif ef_id == 21:
        if not move_data.ef_stat:
            move_data.ef_stat = 1
            attacker.next_moves.put(move_data)
            battle._add_text(attacker.nickname + ' whipped up a whirlwind!')
            return
        crit_chance = move_data.ef_amount
    elif ef_id == 22:
        if defender.in_air:
            inv_bypass = True
            move_data.power *= 2
    elif ef_id == 23:
        if not move_data.ef_stat:
            move_data.ef_stat = 1
            attacker.next_moves.put(move_data)
            attacker.in_air = True
            attacker.invulnerable = True
            battle._pop_text()
            battle._add_text(attacker.nickname + ' flew up high!')
            return
        attacker.in_air = False
        attacker.invulnerable = False
    elif ef_id == 24:
        _calculate_damage(attacker, defender, battlefield, battle, move_data)
        if defender.is_alive and not defender.substitute and not defender.v_status[BINDING_COUNT]:
            defender.v_status[BINDING_COUNT] = _generate_2_to_5()
            defender.binding_poke = attacker
            if move_data.ef_stat == BIND:
                defender.binding_type = 'Bind'
                battle._add_text(defender.nickname + ' was squeezed by ' + attacker.nickname + '!')
            elif move_data.ef_stat == WRAP:
                defender.binding_type = 'Wrap'
                defender.v_status[WRAP] = _generate_2_to_5()
                battle._add_text(defender.nickname + ' was wrapped by ' + attacker.nickname + '!')
            elif move_data.ef_stat == FIRE_SPIN:
                defender.binding_type = 'Fire Spin'
                battle._add_text(defender.nickname + ' was trapped in the vortex!')
            elif move_data.ef_stat == CLAMP:
                defender.binding_type = 'Clamp'
                battle._add_text(attacker.nickname + ' clamped ' + defender.nickname + '!')
            elif move_data.ef_stat == WHIRLPOOL:
                defender.binding_type = 'Whirlpool'
                battle._add_text(defender.nickname + ' was trapped in the vortex!')
        return
    elif ef_id == 25:
        if not defender.is_alive:
            return
        dmg = _calculate_damage(attacker, defender, battlefield, battle, move_data) // 2
        if dmg and dmg == 0 and _calculate_type_ef(defender, move_data) == 0:
            dmg = defender.max_hp // 2
        if not dmg:
            return
        battle._add_text(attacker.nickname + ' kept going and crashed!')
        attacker.take_damage(dmg)
        return
    elif ef_id == 26:
        if defender.in_ground:
            move_data.power *= 2
            inv_bypass = True
    elif ef_id == 27 or ef_id == 29:
        dmg = _calculate_damage(attacker, defender, battlefield, battle, move_data)
        if dmg and dmg > 0:
            recoil = dmg // 4 if ef_id == 27 else dmg // 3
            attacker.take_damage(recoil)
            battle._add_text(attacker.nickname + ' is hit with recoil!')
        return
    elif ef_id == 28:
        if not move_data.ef_stat:
            num_turns = random.randrange(1,3)
            move_data.ef_stat = num_turns
            attacker.next_moves.put(move_data)
        else:
            move_data.ef_stat -= 1
            if move_data.ef_stat == 0:
                _calculate_damage(attacker, defender, battlefield, battle, move_data)
                _confuse(attacker, battle)
                return
            else:
                attacker.next_moves.put(move_data)
    elif ef_id == 30:
        _calculate_damage(attacker, defender, battlefield, battle, move_data)
        if not defender.is_alive:
            return
        if random.randrange(1,6) < 2:
            _poison(defender, battle)
        _calculate_damage(attacker, defender, battlefield, battle, move_data)
        if defender.is_alive and random.randrange(5) < 1:
            _poison(defender, battle)
        return
    elif ef_id == 31:
        if defender.is_alive and _calculate_type_ef(defender, move_data) != 0:
            defender.take_damage(move_data.ef_amount, move_data)
        else:
            _missed(attacker, battle)
        return
    elif ef_id == 32:
        has_disabled = not all([not move.disabled for move in defender.moves])
        if not defender.last_move or not defender.last_move.cur_pp or has_disabled:
            _failed(battle)
        else:
            disabled_move = defender.last_move
            disabled_move.disabled = random.randrange(4, 8)
            battle._add_text(defender.trainer.name + '\'s ' + defender.nickname + '\'s ' + disabled_move.name + ' was disabled!')
    elif ef_id == 33:
        if attacker.mist_count:
            _failed(battle)
        else:
            battle._add_text(attacker.trainer.name + '\'s team became shrouded in mist!')
            attacker.mist_count = 5
    elif ef_id == 34:
        attacker.recharging = True
    elif ef_id == 35:
        if defender.weight < 100:
            move_data.power = 20
        elif defender.weight < 250:
            move_data.power = 40
        elif defender.weight < 500:
            move_data.power = 60
        elif defender.weight < 1000:
            move_data.power = 80
        elif defender.weight < 2000:
            move_data.power = 100
        else:
            move_data.power = 120
    elif ef_id == 36:
        if defender.is_alive and attacker.last_move_hit_by and defender.last_move and attacker.last_move_hit_by.name == defender.last_move.name \
                and attacker.last_move_hit_by.category == PHYSICAL and _calculate_type_ef(defender, move_data):
                defender.take_damage(attacker.last_damage_taken * 2, move_data)
        else:
            _failed(battle)
        return
    elif ef_id == 37:
        if _calculate_type_ef(defender, move_data):
            if defender.is_alive:
                defender.take_damage(attacker.level, move_data)
            else:
                _missed(attacker, battle)
        return
    elif ef_id == 38:
        dmg = _calculate_damage(attacker, defender, battlefield, battle, move_data)
        if dmg:
            heal_amount = dmg // 2 if dmg != 1 else 1
            attacker.heal(heal_amount)
            battle._add_text(defender.nickname + ' had it\'s energy drained!')
        return
    elif ef_id == 39:
        if defender.is_alive and not defender.substitute and not defender.v_status[LEECH_SEED]:
            defender.v_status[LEECH_SEED] = 1
            battle._add_text(defender.nickname + ' was seeded!')
    elif ef_id == 40:
        if not move_data.ef_stat and battlefield.weather != HARSH_SUNLIGHT:
            battle._pop_text()
            battle._add_text(attacker.nickname + ' absorbed light!')
            move_data.ef_stat = 1
            attacker.next_moves.put(move_data)
            return
    elif ef_id == 41:
        if defender.is_alive and random.randrange(10) < 3:
            _paralyze(defender, battle)
    elif ef_id == 42:
        if not move_data.ef_stat:
            move_data.ef_stat = 1
            attacker.next_moves.put(move_data)
            attacker.in_ground = True
            attacker.invulnerable = True
            battle._pop_text()
            battle._add_text(attacker.nickname + ' burrowed its way under the ground!')
            return
        attacker.in_ground = False
        attacker.invulnerable = False
    elif ef_id == 43:
        if not attacker.rage:
            attacker.rage = True
            for move in attacker.moves:
                if move.name != 'rage':
                    move.disabled = True
    elif ef_id == 44:
        if defender.is_alive and defender.last_move and not attacker.copied and not attacker.is_move(defender.last_move.md):
            attacker.copied = Move(defender.last_move.md)
            attacker.copied.max_pp = min(5, attacker.copied.max_pp)
            attacker.copied.cur_pp = attacker.copied.max_pp
            battle._add_text(attacker.nickname + ' learned ' + _cap_name(attacker.copied.name))
        else:
            _failed(battle)
    elif ef_id == 45:
        # ability check
        _give_stat_change(defender, battle, DEF, -2)
    elif ef_id == 46:
        attacker.heal(attacker.max_hp // 2)
        battle._add_text(attacker.nickname + ' recovered health!')
    elif ef_id == 47:
        attacker.minimized = True
        _give_stat_change(attacker, battle, EVA, 1)
    elif ef_id == 48:
        attacker.df_curl = True
        _give_stat_change(attacker, battle, DEF, 1)
    elif ef_id == 49:
        t = attacker.trainer
        if move_data.ef_stat == 1:
            if t.light_screen:
                _failed(battle)
                return
            t.light_screen = 5
            battle._add_text('Light Screen raised ' + t.name + '\'s team\'s Special Defense!')
        elif move_data.ef_stat == 2:
            if t.reflect:
                _failed(battle)
                return
            t.reflect = 5
            battle._add_text('Light Screen raised ' + t.name + '\'s team\'s Defense!')
    elif ef_id == 50:
        attacker.reset_stages()
        defender.reset_stages()
        battle._add_text('All stat changes were eliminated!')
    elif ef_id == 51:
        attacker.crit_stage += 2
        if attacker.crit_stage > 4:
            attacker.crit_stage = 4
        battle._add_text(attacker.nickname + ' is getting pumped!')
    elif ef_id == 52:
        if not move_data.ef_stat:
            attacker.trapped = True
            move_data.ef_stat = 1
            attacker.bide_count = 2 if is_first else 3
            attacker.next_moves.put(move_data)
            attacker.bide_dmg = 0
            battle._add_text(attacker.nickname + ' is storing energy!')
        else:
            battle._pop_text()
            battle._add_text(attacker.nickname + ' unleashed energy!')
            if defender.is_alive:
                defender.take_damage(2 * attacker.bide_dmg, move_data)
            else:
                _missed(attacker, battle)
            attacker.bide_dmg = 0
        return
    elif ef_id == 53:
        move_names = [move.name for move in attacker.moves]
        rand_move = PokeSim.get_rand_move()
        # counter check for loop
        while rand_move in move_names or rand_move in METRONOME_CHECK:
            rand_move = PokeSim.get_rand_move()
        rand_move = Move(rand_move)
        battle._add_text(attacker.nickname + ' used ' + _cap_name(rand_move.name) + '!')
        _process_effect(attacker, defender, battlefield, battle, rand_move, is_first)
        return
    elif ef_id == 54:
        if defender.is_alive and defender.last_move:
            battle._add_text(attacker.nickname + ' used ' + _cap_name(defender.last_move.name) + '!')
            _process_effect(attacker, defender, battlefield, battle, defender.last_move, is_first)
        else:
            _failed(battle)
        return
    elif ef_id == 55:
        attacker.faint()
        _calculate_damage(attacker, defender, battlefield, battle, move_data)
        return
    elif ef_id == 56:
        if not move_data.ef_stat:
            battle._pop_text()
            battle._add_text(attacker.nickname + ' tucked in its head!')
            _give_stat_change(attacker, battle, DEF, 1)
            move_data.ef_stat = 1
            attacker.next_moves.put(move_data)
            return
    elif ef_id == 57:
        if not defender.is_alive:
            _missed(attacker, battle)
        elif defender.nv_status == ASLEEP:
            dmg = _calculate_damage(attacker, defender, battlefield, battle, move_data)
            if dmg:
                heal_amount = dmg // 2 if dmg != 1 else 1
                attacker.heal(heal_amount)
            battle._add_text(defender.nickname + '\'s dream was eaten!')
        else:
            _failed(battle)
        return
    elif ef_id == 58:
        if not move_data.ef_stat:
            move_data.ef_stat = 1
            defender.next_moves.put(move_data)
            battle._pop_text()
            battle._add_text(attacker.nickname + ' became clocked in a harsh light!')
        else:
            _calculate_damage(attacker, defender, battlefield, battle, move_data, crit_chance=1)
            if random.randrange(10) < 3:
                _flinch(defender, is_first)
        return
    elif ef_id == 59:
        if defender.is_alive and not defender.transformed and not attacker.transformed:
            attacker.transform(defender)
            battle._add_text(attacker.nickname + ' transformed into ' + defender.name + '!')
        else:
            _failed(battle)
        return
    elif ef_id == 60:
        dmg = attacker.level * (random.randrange(0, 11) * 10 + 50) // 100
        if defender.is_alive:
            defender.take_damage(dmg if dmg != 0 else 1, move_data)
        else:
            _missed(attacker, battle)
        return
    elif ef_id == 61:
        battle._add_text('But nothing happened!')
        return
    elif ef_id == 62:
        if not defender.is_alive:
            _failed(battle)
            return
        attacker.faint()
        old_def = defender.stats_actual[DEF]
        defender.stats_actual[DEF] //= 2
        _calculate_damage(attacker, defender, battlefield, battle, move_data)
        defender.stats_actual[DEF] = old_def
        return
    elif ef_id == 63:
        attacker.nv_status = ASLEEP
        attacker.nv_counter = 3
        battle._add_text(attacker.nickname + ' went to sleep!')
        attacker.heal(attacker.max_hp)
    elif ef_id == 64:
        move_types = [move.type for move in attacker.moves if move.type not in attacker.types]
        if not len(move_types):
            _failed(battle)
            return
        attacker.types = (move_types[random.randrange(len(move_types))], None)
    elif ef_id == 65:
        _calculate_damage(attacker, defender, battlefield, battle, move_data)
        if defender.is_alive and random.randrange(5) < 1:
            _give_nv_status(random.randrange(1, 4), defender, battle)
        return
    elif ef_id == 66:
        if not defender.is_alive or _calculate_type_ef(defender, move_data) == 0:
            _failed(battle)
            return
        else:
            dmg = defender.max_hp // 2
            defender.take_damage(dmg if dmg > 0 else 1, move_data)
        return
    elif ef_id == 67:
        if attacker.substitute:
            _failed(battle)
            return
        if attacker.cur_hp - attacker.max_hp // 4 < 0:
            battle._add_text('But it does not have enough HP left to make a substitute!')
            return
        attacker.substitute = attacker.take_damage(attacker.max_hp // 4) + 1
        battle._add_text(attacker.nickname + ' made a substitute!')
    elif ef_id == 68:
        battle._pop_text()
        battle._add_text(attacker.nickname + ' has no moves left!')
        battle._add_text(attacker.nickname + ' used Struggle!')
        _calculate_damage(attacker, defender, battlefield, battle, move_data)
        struggle_dmg = attacker.max_hp // 4
        attacker.take_damage(struggle_dmg if struggle_dmg > 0 else 1)
        battle._add_text(attacker.nickname + ' is hit with recoil!')
    elif ef_id == 69:
        if attacker.transformed or not move_data in attacker.o_moves or not defender.is_alive or \
                not defender.last_move or attacker.is_move(defender.last_move.name):
            _failed(battle)
            return
        attacker.moves[move_data.pos] = Move(defender.last_move.md)
    elif ef_id == 70:
        if not defender.is_alive:
            _missed(attacker, battle)
        num_hits = 0
        while num_hits < 3 and defender.is_alive:
            _calculate_damage(attacker, defender, battlefield, battle, move_data, skip_fc=True)
            move_data.power += 10
            num_hits += 1
        battle._add_text('Hit' + str(num_hits) +  'time(s)!')
        return
    elif ef_id == 71:
        _calculate_damage(attacker, defender, battlefield, battle, move_data)
        if defender.item and not attacker.item:
            battle._add_text(attacker.nickname + ' stole ' + defender.nickname + '\'s ' + _cap_name(defender.item) + '!')
            attacker.give_item(defender.item)
            defender.give_item(None)
        return
    elif ef_id == 72:
        if defender.is_alive and not defender.invulnerable:
            defender.perma_trapped = True
            battle._add_text(defender.nickname + ' can no longer escape!')
        else:
            _failed(battle)
    elif ef_id == 73:
        if defender.is_alive:
            attacker.mr_count = 2
            attacker.mr_target = defender
            battle._add_text(attacker.nickname + ' took aim at ' + defender.nickname + '!')
        else:
            _failed(battle)
    elif ef_id == 74:
        if defender.is_alive and defender.nv_status == ASLEEP and not defender.substitute:
            defender.v_status[NIGHTMARE] = 1
            battle._add_text(defender.nickname + ' began having a nightmare!')
        else:
            _failed(battle)
    elif ef_id == 75:
        _calculate_damage(attacker, defender, battlefield, battle, move_data)
        if defender.is_alive and random.randrange(100) < move_data.ef_amount:
            _burn(defender, battle)
        return
    elif ef_id == 76:
        if defender.is_alive and attacker.nv_status == ASLEEP:
            _calculate_damage(attacker, defender, battlefield, battle, move_data)
            if random.randrange(10) < 3:
                _flinch(defender, is_first)
        else:
            _failed(battle)
        return
    elif ef_id == 77:
        if 'ghost' not in attacker.types:
            if attacker.stat_stages[ATK] == 6 and attacker.stat_stages[DEF] == 6 and attacker.stat_stages[SPD] == -6:
                _failed(battle)
                return
            if attacker.stat_stages[ATK] < 6:
                _give_stat_change(attacker, battle, ATK, 1)
            if attacker.stat_stages[DEF] < 6:
                _give_stat_change(attacker, battle, DEF, 1)
            if attacker.stat_stages[SPD] > -6:
                _give_stat_change(attacker, battle, SPD, -1)
        else:
            if not defender.is_alive or defender.v_status[CURSE] or defender.substitute:
                _failed(battle)
                return
            attacker.take_damage(attacker.max_hp // 2)
            defender.v_status[CURSE] = 1
            battle._add_text(attacker.nickname + ' cut its own HP and laid a curse on ' + defender.nickname + '!')
    elif ef_id == 78:
        hp_ratio = int((float(attacker.cur_hp) / attacker.max_hp) * 10000)
        if hp_ratio >= 6719:
            move_data.power = 20
        elif hp_ratio >= 3438:
            move_data.power = 40
        elif hp_ratio >= 2031:
            move_data.power = 80
        elif hp_ratio >= 938:
            move_data.power = 100
        elif hp_ratio >= 313:
            move_data.power = 150
        else:
            move_data.power = 200
    elif ef_id == 79:
        if not attacker.last_move_hit_by:
            _failed(battle)
            return
        last_move_type = attacker.last_move_hit_by.type
        types = PokeSim.get_all_types()
        poss_types = []
        for type in types:
            if type and PokeSim.get_type_effectiveness(last_move_type, type) < 1:
                poss_types.append(type)
        poss_types = [type for type in poss_types if type not in attacker.types]
        if len(poss_types):
            new_type = poss_types[random.randrange(len(poss_types))]
            attacker.types = (new_type, None)
            battle._add_text(attacker.nickname + ' transformed into the ' + new_type.upper() + ' type!')
        else:
            _failed(battle)
    elif ef_id == 80:
        if defender.is_alive and defender.last_move and defender.last_move.cur_pp:
            if defender.last_move.cur_pp < 4:
                amt_reduced = defender.last_move.cur_pp
            else:
                amt_reduced = 4
            defender.last_move.cur_pp -= amt_reduced
            battle._add_text('It reduced the pp of ' + defender.nickname + '\'s ' + _cap_name(defender.last_move.name) + ' by ' + str(amt_reduced) + '!')
        else:
            _failed(battle)
    elif ef_id == 81:
        if attacker.substitute:
            _failed(battle)
        p_chance = min(8, 2 ** attacker.protect_count)
        if random.randrange(p_chance) < 1:
            attacker.invulnerable = True
            attacker.protect = True
            attacker.protect_count += 1
        else:
            _failed(battle)
    elif ef_id == 82:
        if attacker.max_hp // 2 > attacker.cur_hp or attacker.stat_stages[ATK] == 6:
            _failed(battle)
            return
        battle._add_text(attacker.nickname + ' cut its own HP and maximized its Attack!')
        attacker.stat_stages[ATK] = 6
    elif ef_id == 83:
        enemy = defender.trainer
        if enemy.spikes < 3:
            enemy.spikes += 1
            battle._add_text('Spikes were scattered all around the feet of ' + enemy.name + '\'s team!')
        else:
            _failed(battle)
    elif ef_id == 84:
        if defender.is_alive and not attacker.foresight_target:
            attacker.foresight_target = defender
            battle._add_text(attacker.nickname + ' identified ' + defender.nickname + '!')
        else:
            _failed(battle)
    elif ef_id == 85:
        battle._add_text(attacker.nickname + ' is trying to take its foe with it!')
        attacker.db_count = 1 if is_first else 2
    elif ef_id == 86:
        if not attacker.perish_count:
            attacker.perish_count = 4
        if defender.is_alive and not defender.perish_count:
            defender.perish_count = 4
        battle._add_text('All pokemon hearing the song will faint in three turns!')
    elif ef_id == 87:
        if battlefield.weather != SANDSTORM:
            battlefield.weather = SANDSTORM
            battlefield.weather_count = 5
            battle._add_text('A sandstorm brewed')
        else:
            _failed(battle)
    elif ef_id == 88:
        if attacker.substitute:
            _failed(battle)
        p_chance = min(8, 2 ** attacker.protect_count)
        if random.randrange(p_chance) < 1:
            attacker.endure = True
            attacker.protect_count += 1
        else:
            _failed(battle)
    elif ef_id == 89:
        if not move_data.ef_stat:
            if attacker.df_curl and move_data.power == move_data.o_power:
                move_data.power *= 2
            move_data.ef_stat = 1
        else:
            move_data.ef_stat += 1
        _calculate_damage(attacker, defender, battlefield, battle, move_data, crit_chance, inv_bypass)
        move_data.power *= 2
        if move_data.ef_stat < 5:
            attacker.next_moves.put(move_data)
        return
    elif ef_id == 90:
        dmg = _calculate_damage(attacker, defender, battlefield, battle, move_data, skip_dmg=True)
        if not dmg:
            return
        if not defender.substitute and dmg >= defender.cur_hp:
            dmg = defender.cur_hp - 1
        defender.take_damage(dmg, move_data)
        return
    elif ef_id == 91:
        if defender.is_alive:
            _give_stat_change(defender, battle, ATK, 2)
            _confuse(defender, battle, forced=True)
        else:
            _failed(battle)
    elif ef_id == 92:
        if attacker.last_move and attacker.last_move is attacker.last_successful_move and attacker.last_move.name == move_data.name:
            move_data.ef_stat = min(5, int(attacker.last_move.ef_stat) + 1)
            move_data.power = move_data.o_power * (2 ** (move.data.ef_stat - 1))
        else:
            move_data.ef_stat = 1
    elif ef_id == 93:
        _infatuate(attacker, defender, battle)
    elif ef_id == 94:
        if attacker.nv_status != ASLEEP:
            _failed(battle)
            return
        pos_moves = [move for move in attacker.moves if move.name != 'sleep-talk']
        sel_move = Move(pos_moves[random.randrange(len(pos_moves))].md)
        battle._add_text(attacker.nickname + ' used ' + _cap_name(sel_move.name) + '!')
        _process_effect(attacker, defender, battlefield, battle, sel_move, is_first)
        return
    elif ef_id == 95:
        battle._add_text('A bell chimed!')
        t = attacker.trainer
        for poke in t.poke_list:
            poke.nv_status = 0
    elif ef_id == 96:
        move_data.power = max(1, int(attacker.friendship / 2.5))
    elif ef_id == 97:
        res = random.randrange(10)
        if res < 2:
            if not defender.is_alive:
                _missed(attacker, battle)
                return
            if defender.cur_hp == defender.max_hp:
                battle._add_text(defender.nickname + ' can\'t receive the gift!')
                return
            defender.heal(defender.max_hp // 4)
            return
        elif res < 6:
            move_data.power = 40
        elif res < 9:
            move_data.power = 80
        elif res < 10:
            move_data.power = 120
    elif ef_id == 98:
        move_data.power = max(1, int((255 - attacker.friendship) / 2.5))
    elif ef_id == 99:
        t = attacker.trainer
        if not t.safeguard:
            t.safeguard = 5
            battle._add_text(t.name + '\'s team became cloaked in a mystical veil!')
        else:
            _failed(battle)
    elif ef_id == 100:
        if defender.is_alive:
            new_hp = (attacker.cur_hp + defender.cur_hp) // 2
            battle._add_text('The battlers shared their pain!')
            attacker.cur_hp = min(new_hp, attacker.max_hp)
            defender.cur_hp = min(new_hp, defender.max_hp)
        else:
            _failed(battle)
        return
    elif ef_id == 101:
        res = random.randrange(20)
        if res < 1:
            mag = 4
            move_data.power = 10
        elif res < 3:
            mag = 5
            move_data.power = 30
        elif res < 7:
            mag = 6
            move_data.power = 50
        elif res < 13:
            mag = 7
            move_data.power = 70
        elif res < 17:
            mag = 8
            move_data.power = 90
        elif res < 19:
            mag = 9
            move_data.power = 110
        else:
            mag = 10
            move_data.power = 150
        if defender.in_ground:
            inv_bypass = True
            move_data.power *= 2
        battle._add_text('Magnitude ' + str(mag) + '!')
    elif ef_id == 102:
        t = attacker.trainer
        if t.num_fainted >= len(t.poke_list) - 1 or battle._process_selection(t):
            _failed(battle)
    elif ef_id == 103:
        if defender.is_alive and not defender.encore_count and defender.last_move and defender.last_move.cur_pp \
                and defender.last_move not in ENCORE_CHECK and any([move.name == defender.last_move.name for move in defender.moves]):
            defender.next_moves.clear()
            defender.encore_count = min(random.randrange(2, 7), defender.last_move.pp)
            for move in defender.moves:
                if move.name != defender.last_move.name:
                    move.encore_blocked = True
                else:
                    defender.encore_move = move
            battle._add_text(defender.nickname + ' received an encore!')
        else:
            _failed(battle)
    elif ef_id == 104:
        _calculate_damage(attacker, defender, battlefield, battle, move_data)
        if attacker.is_alive:
            attacker.v_status[BINDING_COUNT] = 0
            attacker.binding_type = None
            attacker.binding_poke = None
            attacker.v_status[LEECH_SEED] = 0
            t = attacker.trainer
            t.spikes = 0
        return
    elif ef_id == 105:
        if battlefield.weather == CLEAR:
            heal_amount = 2
        elif battlefield.weather == HARSH_SUNLIGHT:
            heal_amount = 1.5
        else:
            heal_amount = 4
        attacker.heal(int(attacker.max_hp / heal_amount))
    elif ef_id == 106:
        hp_stats = attacker.hidden_power_stats()
        if hp_stats:
            move_data.type, move_data.power = hp_stats
        else:
            move_data.power = random.randrange(30, 71)
            move_data.type = attacker.types[0]
    elif ef_id == 107:
        if defender.in_air:
            inv_bypass = True
            move_data.power *= 2
        _calculate_damage(attacker, defender, battlefield, battle, move_data, crit_chance, inv_bypass)
        if defender.is_alive and random.randrange(5) < 1:
            _flinch(defender, is_first)
        return
    elif ef_id == 108:
        if battlefield.weather != RAIN:
            battlefield.weather = RAIN
            battlefield.weather_count = 5
            battle._add_text('It started to rain!')
        else:
            _failed(battle)
    elif ef_id == 109:
        if battlefield.weather != HARSH_SUNLIGHT:
            battlefield.weather = HARSH_SUNLIGHT
            battlefield.weather_count = 5
            battle._add_text('The sunlight turned harsh!')
        else:
            _failed(battle)
    elif ef_id == 110:
        if defender.is_alive and attacker.last_move_hit_by and defender.last_move and attacker.last_move_hit_by.name == defender.last_move.name \
                and attacker.last_move_hit_by.category == SPECIAL and _calculate_type_ef(defender, move_data):
            defender.take_damage(attacker.last_damage_taken * 2, move_data)
        else:
            _failed(battle)
        return
    elif ef_id == 111:
        if defender.is_alive:
            attacker.stat_stages = [stat for stat in defender.stat_stages]
            attacker.accuracy_stage = defender.accuracy_stage
            attacker.evasion_stage = defender.evasion_stage
            attacker.crit_stage = defender.crit_stage
            battle._add_text(attacker.nickname + ' copied ' + defender.nickname + '\'s stat changes!')
        else:
            _failed(battle)
    elif ef_id == 112:
        _calculate_damage(attacker, defender, battlefield, battle, move_data)
        if random.randrange(10) < 1:
            _give_stat_change(attacker, battle, ATK, 1)
            _give_stat_change(attacker, battle, DEF, 1)
            _give_stat_change(attacker, battle, SP_ATK, 1)
            _give_stat_change(attacker, battle, SP_DEF, 1)
            _give_stat_change(attacker, battle, SPD, 1)
        return
    elif ef_id == 113:
        t = defender.trainer
        if defender.is_alive and not t.fs_count:
            move_data.type = 'typeless'
            t.fs_dmg = _calculate_damage(attacker, defender, battlefield, battle, move_data, crit_chance=0, skip_dmg=True)
            t.fs_count = 3
            battle._add_text(attacker.nickname + ' foresaw an attack!')
        else:
            _failed(battle)
        return
    elif ef_id == 114:
        if not defender.is_alive:
            _failed(battle)
            return
        poke_hits = [poke for poke in attacker.trainer.poke_list if not poke.nv_status]
        num_hits = 0
        move_data.power = 10
        while defender.is_alive and num_hits < len(poke_hits):
            _calculate_damage(attacker, defender, battlefield, battle, move_data)
            battle._add_text(poke_hits[num_hits].nickname + '\'s attack!')
            num_hits += 1
        return
    elif ef_id == 115:
        _calculate_damage(attacker, defender, battlefield, battle, move_data)
        if not attacker.uproar:
            attacker.uproar = random.randrange(1, 5)
            battle._add_text(attacker.nickname + ' caused an uproar!')
        return
    elif ef_id == 116:
        if attacker.stockpile < 3:
            attacker.stockpile += 1
            battle._add_text(attacker.nickname + ' stockpiled ' + str(attacker.stockpile) + '!')
            _give_stat_change(attacker, battle, DEF, 1)
            _give_stat_change(attacker, battle, SP_DEF, 1)
        else:
            _failed(battle)
    elif ef_id == 117:
        if attacker.stockpile:
            _calculate_damage(attacker, defender, battlefield, battle, move_data)
            move_data.power = 100 * attacker.stockpile
            attacker.stockpile = 0
            attacker.stat_stages[DEF] -= attacker.stockpile
            attacker.stat_stages[SP_DEF] -= attacker.stockpile
            battle._add_text(attacker.nickname + '\'s stockpile effect wore off!')
        else:
            _failed(battle)
    elif ef_id == 118:
        if attacker.stockpile:
            attacker.heal(attacker.max_hp * (2 ** (attacker.stockpile - 1)) // 4)
            attacker.stockpile = 0
            attacker.stat_stages[DEF] -= attacker.stockpile
            attacker.stat_stages[SP_DEF] -= attacker.stockpile
            battle._add_text(attacker.nickname + '\'s stockpile effect wore off!')
        else:
            _failed(battle)
    elif ef_id == 119:
        if battlefield.weather != HAIL:
            battlefield.weather = HAIL
            battlefield.weather_count = 5
            battle._add_text('It started to hail!')
        else:
            _failed(battle)
    elif ef_id == 120:
        if defender.is_alive and not defender.tormented:
            defender.tormented = True
            battle._add_text(defender.nickname + ' was subjected to Torment!')
        else:
            _failed(battle)
    elif ef_id == 121:
        if defender.is_alive and not defender.substitute and (not defender.v_status[CONFUSED] or defender.stat_stages[SP_ATK] < 6):
            _give_stat_change(defender, battle, SP_ATK, 1)
            _confuse(defender, battle)
        else:
            _failed(battle)
    elif ef_id == 122:
        if defender.is_alive and not defender.substitute:
            attacker.faint()
            _give_stat_change(defender, battle, ATK, -2)
            _give_stat_change(defender, battle, SP_ATK, -2)
        return
    elif ef_id == 123:
        if attacker.nv_status == BURNED or attacker.nv_status == PARALYZED or attacker.nv_status == POISONED:
            move_data.power *= 2
    elif ef_id == 124:
        if not defender.is_alive:
            _failed(battle)
            return
        if attacker.turn_damage:
            battle._pop_text()
            battle._add_text(attacker.nickname + ' lost its focus and couldn\'t move!')
            return
    elif ef_id == 125:
        if not defender.is_alive:
            _failed(battle)
            return
        if defender.nv_status == PARALYZED:
            move_data.power *= 2
        _calculate_damage(attacker, defender, battlefield, battle, move_data)
        if defender.is_alive and defender.nv_status == PARALYZED:
            defender.nv_status = 0
            battle._add_text(defender.nickname + ' was cured of paralysis!')
        return
    elif ef_id == 126:
        move_data = Move(PokeSim.get_move_data(['swift'])[0])
    elif ef_id == 127:
        attacker.charged = 2
        battle._add_text(attacker.nickname + ' began charging power!')
        _give_stat_change(attacker, battle, SP_DEF, 1)
    elif ef_id == 128:
        if defender.is_alive and not defender.taunt:
            defender.taunt = random.randrange(3, 6)
            battle._add_text(defender.nickname + ' fell for the taunt!')
        else:
            _failed(battle)
    elif ef_id == 129:
        _failed(battle)
    elif ef_id == 130:
        if attacker.item and defender.is_alive and defender.item and not defender.substitute:
            a_item = attacker.item
            attacker.give_item(defender.item)
            defender.give_item(a_item)
            battle._add_text(attacker.nickname + ' switched items with its target!')
            battle._add_text(attacker.nickname + ' obtained one ' + _cap_name(attacker.item) + '.')
            battle._add_text(defender.nickname + ' obtained one ' + _cap_name(defender.item) + '.')
        else:
            _failed(battle)
    elif ef_id == 131:
        if defender.is_alive and defender.ability and defender.ability not in ['wonder-guard', 'multitype']:
            attacker.ability = defender.ability
            battle._add_text(attacker.nickname + ' copied ' + defender.nickname + '\'s ' + defender.ability + '!')
        else:
            _failed(battle)
    elif ef_id == 132:
        t = attacker.trainer
        if not t.wish:
            t.wish = 2
            t.wish_poke = attacker.nickname
        else:
            _failed(battle)
    elif ef_id == 133:
        possible_moves = [move for poke in attacker.trainer.poke_list for move in poke.moves if move.name not in ASSIST_CHECK]
        if len(possible_moves):
            _process_effect(attacker, defender, battlefield, battle, Move(possible_moves[random.randrange(len(possible_moves))].md), is_first)
        else:
            _failed(battle)
        return
    elif ef_id == 134:
        if not attacker.ingrain:
            battle._add_text(attacker.nickname + ' planted its roots!')
            attacker.ingrain = True
            attacker.trapped = True
        else:
            _failed(battle)
    elif ef_id == 135:
        _calculate_damage(attacker, defender, battlefield, battle, move_data)
        if defender.is_alive:
            _give_stat_change(defender, battle, ATK, -1)
            _give_stat_change(defender, battle, DEF, -1)
        return
    elif ef_id == 136:
        if is_first:
            attacker.magic_coat = True
            battle._add_text(attacker.nickname + ' shrouded itself with Magic Coat!')
        else:
            _failed(battle)
    elif ef_id == 137:
        if not attacker.item and not attacker.h_item and attacker.last_consumed_item:
            attacker.give_item(attacker.last_consumed_item)
            attacker.last_consumed_item = None
            battle._add_text(attacker.nickname + ' found one ' + _cap_name(attacker.item) + '!')
        else:
            _failed(battle)
    elif ef_id == 138:
        if attacker.turn_damage:
            move_data.power *= 2
    elif ef_id == 139:
        if defender.is_alive and not defender.invulnerable and not defender.protect:
            t = defender.trainer
            if t.light_screen or t.reflect:
                t.light_screen = 0
                t.reflect = 0
                battle._add_text('It shattered the barrier!')
            _calculate_damage(attacker, defender, battlefield, battle, move_data)
        else:
            _failed(battle)
        return
    elif ef_id == 140:
        if defender.is_alive and not defender.v_status[DROWSY] and not defender.substitute \
                and not defender.nv_status == FROZEN and not defender.nv_status == ASLEEP and defender.ability != 'insomnia' \
                and defender.ability != 'vital-spirit' and not defender.trainer \
                and not (defender.ability == 'leaf-guard' and battlefield.weather == HARSH_SUNLIGHT) \
                and not (defender.ability != 'soundproof' and defender.uproar):
            defender.v_status[DROWSY] = 2
            battle._add_text(attacker.nickname + ' made ' + defender.nickname + ' drowsy!')
        else:
            _failed(battle)
    elif ef_id == 141:
        _calculate_damage(attacker, defender, battlefield, battle, move_data)
        if defender.is_alive and defender.item and defender.h_item:
            defender.item = None
            battle._add_text(attacker.nickname + ' knocked off ' + defender.nickname + '\'s ' + _cap_name(defender.item) + '!')
        return
    elif ef_id == 142:
        if defender.is_alive and attacker.cur_hp < defender.cur_hp and _calculate_type_ef(defender, move_data):
            defender.take_damage(defender.cur_hp - attacker.cur_hp)
        else:
            _failed(battle)
        return
    elif ef_id == 143:
        move_data.power = max(1, (150 * attacker.cur_hp) // attacker.max_hp)
    elif ef_id == 144:
        if defender.is_alive and defender.ability and defender.ability not in ['wonder-guard', 'multitype'] \
                and attacker.ability not in ['wonder-guard', 'multitype']:
            attacker.ability, defender.ability = defender.ability, attacker.ability
            battle._add_text(attacker.nickname + ' swapped abilities with its target!')
        else:
            _failed(battle)
    elif ef_id == 145:
        a_moves = [move.name for move in attacker.moves]
        t = defender.trainer
        if not t.imprisoned_poke and any([move.name in a_moves for poke in t.poke_list for move in poke.moves]):
            battle._add_text(attacker.nickname + ' sealed the opponent\'s move(s)!')
            t.imprisoned_poke = attacker
        else:
            _failed(battle)
    elif ef_id == 146:
        if attacker.nv_status == BURNED or attacker.nv_status == PARALYZED or attacker.nv_status == POISONED:
            attacker.nv_status = 0
            battle._add_text(attacker.nickname + '\'s status returned to normal!')
        else:
            _failed(battle)
    elif ef_id == 147:
        battle._add_text(attacker.nickname + ' wants ' + attacker.enemy.name + ' to bear a grudge!')
    elif ef_id == 148:
        if is_first:
            attacker.snatch = True
            battle._add_text(attacker.nickname + ' waits for a target to make a move!')
        else:
            _failed(battle)
    elif ef_id == 149:
        _calculate_damage(attacker, defender, battlefield, battle, move_data)
        if defender.is_alive and random.randrange(10) < 3:
            _paralyze(defender, battle)
        return
    elif ef_id == 150:
        if not move_data.ef_stat:
            move_data.ef_stat = 1
            attacker.next_moves.put(move_data)
            attacker.in_ground = True
            attacker.invulnerable = True
            battle._pop_text()
            battle._add_text(attacker.nickname + ' hid underwater!')
            return
        attacker.in_ground = False
        attacker.invulnerable = False




    _calculate_damage(attacker, defender, battlefield, battle, move_data, crit_chance, inv_bypass)

def _calculate_crit(crit_chance: int = None):
    if not crit_chance:
        return random.randrange(16) < 1
    elif crit_chance == 1:
        return random.randrange(9) < 1
    elif crit_chance == 2:
        return random.randrange(5) < 1
    elif crit_chance == 3:
        return random.randrange(4) < 1
    elif crit_chance == 4:
        return random.randrange(3) < 1
    else:
        return random.randrange(1000) < crit_chance

def _invulnerability_check(attacker: pokemon.Pokemon, defender: pokemon.Pokemon, battlefield: bf.Battlefield, battle: bt.Battle, move_data: Move) -> bool:
    if defender.invulnerable:
        if defender.in_air or defender.in_ground or defender.in_water:
            _missed(attacker, battle)
        return True
    return False

def _pre_process_status(attacker: pokemon.Pokemon, defender: pokemon.Pokemon, battlefield: bf.Battlefield, battle: bt.Battle, move_data: Move) -> bool:
    if attacker.nv_status == FROZEN:
        if move_data.ef_id == 75 or random.randrange(5) < 1:
            attacker.nv_status = 0
            battle._add_text(attacker.nickname + ' thawed out!')
        else:
            battle._add_text(attacker.nickname + ' is frozen solid!')
            return True
    if attacker.nv_status == ASLEEP:
        if not attacker.nv_counter:
            attacker.nv_status = 0
        attacker.nv_counter -= 1
        if attacker.nv_counter:
            battle._add_text(attacker.nickname + ' is fast asleep!')
            if move_data.name == 'snore' or move_data.name == 'sleep-talk':
                return False
            return True
        battle._add_text(attacker.nickname + ' woke up!')
    if attacker.v_status[FLINCHED]:
        attacker.v_status[FLINCHED] = 0
        battle._add_text(attacker.nickname + ' flinched and couldn\'t move')
        return True
    if attacker.nv_status == PARALYZED:
        if random.randrange(4) < 1:
            battle._add_text(attacker.nickname + ' is paralyzed! It can\'t move!')
            return True
    if attacker.infatuation:
        if not attacker.infatuation is defender:
            attacker.infatuation = None
            battle._add_text(attacker.nickname + ' got over its infatuation!')
        elif random.randrange(2) < 1:
            battle._add_text(attacker.nickname + ' is immobilized by love!')
            return True
    if attacker.v_status[CONFUSED]:
        attacker.v_status[CONFUSED] -= 1
        if attacker.v_status[CONFUSED]:
            battle._add_text(attacker.nickname + ' is confused!')
            if random.randrange(2) < 1:
                battle._add_text('It hurt itself in its confusion!')
                self_attack = Move([0, 'self-attack', 1, 'typeless', 40, 1, 999, 0, 10, 2, 1, '', '', ''])
                _calculate_damage(attacker, attacker, battlefield, battle, self_attack, crit_chance=0)
                return True
    return False

def _generate_2_to_5() -> int:
    n = random.randrange(8)
    if n < 3:
        num_hits = 2
    elif n < 6:
        num_hits = 3
    elif n < 7:
        num_hits = 4
    else:
        num_hits = 5
    return num_hits

def _confuse(recipient: pk.Pokemon, battle: bt.Battle, forced: bool = False):
    if _safeguard_check(recipient, battle):
        return
    if recipient.substitute:
        if forced:
            _failed(battle)
        return
    if forced and recipient.v_status[CONFUSED]:
        battle._add_text(recipient.nickname + ' is already confused!')
        return
    recipient.v_status[CONFUSED] = _generate_2_to_5()
    battle._add_text(recipient.nickname + ' became confused!')


def _flinch(recipient: pk.Pokemon, is_first: bool):
    if recipient.substitute:
        return
    if is_first and recipient.is_alive and not recipient.v_status[FLINCHED]:
        recipient.v_status[FLINCHED] = 1

def _infatuate(attacker: pk.Pokemon, defender: pk.Pokemon, battle: bt.Battle):
    if not defender.is_alive or defender.infatuation:
        _failed(battle)
    elif (attacker.gender == 'male' and defender.gender == 'female') or (attacker.gender == 'female' and defender.gender == 'male'):
        defender.infatuation = attacker
        battle._add_text(defender.nickname + ' fell in love with ' + attacker.nickname + '!')

def _give_stat_change(recipient: pokemon.Pokemon, battle: bt.Battle, stat: int, amount: int, forced: bool = False):
    if not recipient.is_alive:
        if forced:
            _failed(battle)
        return
    if recipient.substitute and amount < 0:
        if forced:
            _failed(battle)
        return
    battle._add_text(_stat_text(recipient, stat, amount))
    if stat == 6:
        recipient.accuracy_stage = _fit_stat_bounds(recipient.accuracy_stage + amount)
    elif stat == 7:
        recipient.evasion_stage = _fit_stat_bounds(recipient.evasion_stage + amount)
    else:
        recipient.stat_stages[stat] = _fit_stat_bounds(recipient.stat_stages[stat] + amount)
    return

def _fit_stat_bounds(stage: int):
    if stage >= 0:
        return min(6, stage)
    else:
        return max(-6, stage)

def _stat_text(recipient: pk.Pokemon, stat: int, amount: int) -> str:
    if stat == ACC:
        cur_stage = recipient.accuracy_stage
    elif stat == EVA:
        cur_stage = recipient.evasion_stage
    else:
        cur_stage = recipient.stat_stages[stat]
    if not amount:
        return
    base = recipient.nickname + '\'s ' + STAT_TO_NAME[stat]
    if amount > 0:
        if cur_stage >= 6:
            base += ' won\'t go any higher!'
        elif amount == 1:
            base += ' rose!'
        elif amount == 2:
            base += ' rose sharply!'
        else:
            base += ' rose drastically!'
    else:
        if cur_stage <= -6:
            base += ' won\'t go any lower!'
        elif amount == -1:
            base += ' fell!'
        elif amount == -2:
            base += ' fell harshly!'
        else:
            base += ' fell severely!'
    return base

def _give_nv_status(status: int, recipient: pk.Pokemon, battle: bt.Battle, forced: bool = False):
    if status == BURNED:
        _burn(recipient, battle, forced)
    elif status == FROZEN:
        _freeze(recipient, battle, forced)
    elif status == PARALYZED:
        _paralyze(recipient, battle, forced)
    elif status == POISONED:
        _poison(recipient, battle, forced)
    elif status == ASLEEP:
        _sleep(recipient, battle, forced)
    elif status == BADLY_POISONED:
        _badly_poison(recipient, battle, forced)

def _burn(recipient: pk.Pokemon, battle: bt.Battle, forced: bool = False):
    if _safeguard_check(recipient, battle):
        return
    if recipient.substitute:
        if forced:
            _failed(battle)
        return
    if 'fire' in recipient.types:
        if forced:
            _failed(battle)
        return
    if forced and recipient.nv_status == BURNED:
        battle._add_text(recipient.nickname + ' is already burned!')
    elif not recipient.nv_status:
        recipient.nv_status = BURNED
        recipient.nv_counter = 0
        battle._add_text(recipient.nickname + ' was burned!')

def _freeze(recipient: pk.Pokemon, battle: bt.Battle, forced: bool = False):
    if _safeguard_check(recipient, battle):
        return
    if recipient.substitute:
        if forced:
            _failed(battle)
        return
    if 'ice' in recipient.types:
        if forced:
            _failed(battle)
        return
    if forced and recipient.nv_status == FROZEN:
        battle._add_text(recipient.nickname + ' is already frozen!')
    elif not recipient.nv_status:
        recipient.nv_status = FROZEN
        recipient.nv_counter = 0
        battle._add_text(recipient.nickname + ' was frozen solid!')

def _paralyze(recipient: pk.Pokemon, battle: bt.Battle, forced: bool = False):
    if _safeguard_check(recipient, battle):
        return
    if recipient.substitute:
        if forced:
            _failed(battle)
        return
    if forced and recipient.nv_status == PARALYZED:
        battle._add_text(recipient.nickname + ' is already paralyzed!')
    elif not recipient.nv_status:
        recipient.nv_status = PARALYZED
        recipient.nv_counter = 0
        battle._add_text(recipient.nickname + ' is paralyzed! It may be unable to move!')

def _poison(recipient: pk.Pokemon, battle: bt.Battle, forced: bool = False):
    if _safeguard_check(recipient, battle):
        return
    if recipient.substitute:
        if forced:
            _failed(battle)
        return
    if forced and recipient.nv_status == POISONED:
        battle._add_text(recipient.nickname + ' is already poisoned!')
    elif not recipient.nv_status:
        recipient.nv_status = POISONED
        recipient.nv_counter = 0
        battle._add_text(recipient.nickname + ' was poisoned!')

def _sleep(recipient: pk.Pokemon, battle: bt.Battle, forced: bool = False):
    if _safeguard_check(recipient, battle):
        return
    if recipient.substitute:
        if forced:
            _failed(battle)
        return
    if forced and recipient.nv_status == ASLEEP:
        battle._add_text(recipient.nickname + ' is already asleep!')
    elif not recipient.nv_status:
        recipient.nv_status = ASLEEP
        recipient.nv_counter = random.randrange(2, 6)
        battle._add_text(recipient.nickname + ' fell asleep!')
    
def _badly_poison(recipient: pk.Pokemon, battle: bt.Battle, forced: bool = False):
    if _safeguard_check(recipient, battle):
        return
    if recipient.substitute:
        if forced:
            _failed(battle)
        return
    if forced and recipient.nv_status == BADLY_POISONED:
        battle._add_text(recipient.nickname + ' is already badly poisoned!')
    elif not recipient.nv_status:
        recipient.nv_status = BADLY_POISONED
        recipient,nv_counter = 1
        battle._add_text(recipient.nickname + ' was badly poisoned!')

def _magic_coat_check(attacker: pokemon.Pokemon, defender: pokemon.Pokemon, battlefield: bf.Battlefield, battle: bt.Battle, move_data: Move, is_first: bool) -> bool:
    if defender.is_alive and defender.magic_coat and move_data.name in MAGIC_COAT_CHECK:
        battle._add_text(attacker.nickname + '\'s ' + move_data.name + ' was bounced back by Magic Coat!')
        _process_effect(defender, attacker, battlefield, battle, move_data, is_first)
        return True
    return False

def _snatch_check(attacker: pokemon.Pokemon, defender: pokemon.Pokemon, battlefield: bf.Battlefield, battle: bt.Battle, move_data: Move, is_first: bool) -> bool:
    if defender.is_alive and defender.snatch and move_data.name in SNATCH_CHECK:
        battle._add_text(defender.nickname + ' snatched ' + attacker.nickname + '\'s move!')
        _process_effect(defender, attacker, battlefield, battle, move_data, is_first)
        return True
    return False

def _protect_check(defender: pokemon.Pokemon, battle: bt.Battle, move_data: Move) -> bool:
    if defender.is_alive and defender.protect and move_data.target in PROTECT_TARGETS:
        battle._add_text(defender.nickname + ' protected itself!')
        return True
    return False

def _special_move_acc(attacker: pokemon.Pokemon, defender: pokemon.Pokemon, battlefield: bf.Battlefield, battle: bt.Battle, move_data: Move) -> bool:
    if move_data.name == 'thunder':
        if battlefield.weather == RAIN and not defender.in_ground:
            return True
        if battlefield.weather == HARSH_SUNLIGHT:
            move_data.acc = 50
    return False

def _cap_name(move_name: str) -> str:
    move_name = move_name.replace('-', ' ')
    words = move_name.split()
    words = [word.capitalize() for word in words]
    return ' '.join(words)

def _failed(battle: bt.Battle):
    battle._add_text('But, it failed!')

def _missed(attacker: pk.Pokemon, battle: bt.Battle):
    battle._add_text(attacker.nickname + '\'s attack missed!')

def _safeguard_check(poke: pk.Pokemon, battle: bt.Battle) -> bool:
    if poke.trainer.safeguard:
        battle._add_text(poke.nickname + ' is protected by Safeguard!')
        return True
    return False