from __future__ import annotations
import pokemon as pk
import battlefield as bf
import battle as bt
from poke_sim import PokeSim
from move import Move
import random
import global_settings as gs
import global_data as gd
import process_move as pm

def selection_abilities(poke: pokemon.Pokemon, battlefield: bf.Battlefield, battle: bt.Battle):
    if poke.has_ability('drizzle') and battlefield.weather != gs.RAIN:
        battlefield.change_weather(gs.RAIN)
        battlefield.weather_count = 999
        battle._add_text('It started to rain!')
    elif poke.has_ability('drought') and battlefield.weather != gs.HARSH_SUNLIGHT:
        battlefield.change_weather(gs.HARSH_SUNLIGHT)
        battlefield.weather_count = 999
        battle._add_text('The sunlight turned harsh!')
    elif poke.has_ability('sand-stream') and battlefield.weather != gs.SANDSTORM:
        battlefield.change_weather(gs.SANDSTORM)
        battlefield.weather_count = 999
        battle._add_text('A sandstorm brewed')
    elif poke.has_ability('water-veil') and poke.nv_status == gs.BURNED:
        pm._cure_nv_status(gs.BURNED, poke, battle)
    elif poke.has_ability('magma-armor') and poke.nv_status == gs.FROZEN:
        pm._cure_nv_status(gs.FROZEN, poke, battle)
    elif poke.has_ability('limber') and poke.nv_status == gs.PARALYZED:
        pm._cure_nv_status(gs.PARALYZED, poke, battle)
    elif poke.has_ability('insomnia') and poke.nv_status == gs.ASLEEP:
        pm._cure_nv_status(gs.ASLEEP, poke, battle)
    elif poke.has_ability('immunity'):
        if poke.nv_status == gs.POISONED:
            pm._cure_nv_status(gs.POISONED, poke, battle)
        if poke.nv_status == gs.BADLY_POISONED:
            pm._cure_nv_status(gs.BADLY_POISONED, poke, battle)
    elif poke.has_ability('cloud-nine') and battlefield.weather != gs.CLEAR:
            battle._add_text('The effects of weather disappeared.')
            battlefield.change_weather(gs.CLEAR)
    elif poke.has_ability('own-tempo') and poke.v_status[gs.CONFUSED]:
        battle._add_text(attacker.nickname + ' snapped out of its confusion!')
        poke.v_status[gs.CONFUSED] = 0
    elif poke.has_ability('trace') and poke.enemy.current_poke.is_alive and poke.enemy.current_poke.ability:
        battle._add_text(poke.nickname + ' copied ' + poke.enemy.current_poke.nickname + '\'s ' + poke.enemy.current_poke.ability + '!')
        poke.give_ability(poke.enemy.current_poke.ability)
    elif poke.has_ability('forecast'):
        _forecast_check(poke, battle, battlefield)

def enemy_selection_abilities(enemy_poke: pokemon.Pokemon, battlefield: bf.Battlefield, battle: bt.Battle):
    poke = enemy_poke.enemy.current_poke
    if not poke.is_alive:
        return
    if poke.has_ability('intimidate'):
        pm._give_stat_change(enemy_poke, battle, gs.ATK, -1, forced=True)
    elif poke.has_ability('trace') and enemy_poke.ability:
        battle._add_text(poke.nickname + ' copied ' + enemy_poke.nickname + '\'s ' + enemy_poke.ability + '!')
        poke.give_ability(enemy_poke.ability)

def end_turn_abilities(poke: pk.Pokemon, battle: bt.Battle):
    if poke.has_ability('speed-boost'):
        pm._give_stat_change(poke, battle, gs.SPD, 1)

def type_protection_abilities(defender: pk.Pokemon, move_data: Move, battle: bt.Battle) -> bool:
    if defender.has_ability('volt-absorb') and move_data.type == 'electric':
        battle._add_text(defender.nickname + ' absorbed ' + move_data.name + ' with Volt Absorb!')
        if not defender.cur_hp == defender.max_hp:
            defender.heal(defender.max_hp // 4)
        return True
    if defender.has_ability('water-absorb') and move_data.type == 'water':
        battle._add_text(defender.nickname + ' absorbed ' + move_data.name + ' with Water Absorb!')
        if not defender.cur_hp == defender.max_hp:
            defender.heal(defender.max_hp // 4)
        return True
    if defender.has_ability('flash-fire') and move_data.type == 'fire':
        battle._add_text('It doesn\'t affect ' + defender.nickname)
        defender.ability_activated = True
        return True
    return False

def on_hit_abilities(attacker: pk.Pokemon, defender: pk.Pokemon, battle: bt.Battle, move_data: Move) -> bool:
    made_contact = move_data.name in gd.CONTACT_CHECK
    if defender.has_ability('static') and made_contact and random.randrange(10) < 3:
        pm._paralyze(attacker, battle)
    elif defender.has_ability('rough-skin') and made_contact:
        attacker.take_damage(attacker.max_hp // 16)
        battle._add_text(attacker.nickname + ' was hurt!')
    elif defender.has_ability('effect-spore') and made_contact and random.randrange(10) < 3:
        pm._give_nv_status(random.randrange(3, 6), attacker, battle)
    elif defender.has_ability('color-change') and move_data.type not in defender.types:
        defender.types = (move_data.type, None)
        battle._add_text(defender.nickname + ' transformed into the ' + move_data.type.upper() + ' type!')
    elif defender.has_ability('wonder-guard') and pm._calculate_type_ef(defender, move_data) < 2:
        battle._add_text('It doesn\'t affect ' + defender.nickname)
        return True
    elif defender.has_ability('flame-body') and made_contact and random.randrange(10) < 3:
        pm._burn(attacker, battle)
    elif defender.has_ability('poison-point') and made_contact and not 'steel' in attacker.types \
            and not 'poison' in attacker.types and random.randrange(10) < 3:
        pm._poison(attacker, battle)
    elif defender.has_ability('cute-charm') and made_contact and random.randrange(10) < 3:
        pm._infatuate(defender, attacker, battle)

    return False

def pre_move_abilities(attacker: pk.Pokemon, defender: pk.Pokemon, battle: bt.Battle, move_data: Move):
    if attacker.has_ability('serene-grace') and move_data.ef_chance:
        move_data.ef_chance *= 2

def weather_change_abilities(battle: bt.Battle, battlefield: bf.Battlefield):
    _forecast_check(battle.t1.current_poke, battle, battlefield)
    _forecast_check(battle.t2.current_poke, battle, battlefield)

def _forecast_check(poke: pk.Pokemon, battle: bt.Battle, battlefield: bf.Battlefield):
    if poke.is_alive and poke.has_ability('forecast') and poke.name == 'castform':
        if battlefield.weather == gs.HARSH_SUNLIGHT:
            poke.types = ('fire', None)
        elif battlefield.weather == gs.RAIN:
            poke.types = ('water', None)
        elif battlefield.weather == gs.HAIL:
            poke.types = ('ice', None)
        else:
            poke.types = ('normal', None)
        battle._add_text(poke.nickname + ' transformed into the ' + poke.types[0].upper() + ' type!')