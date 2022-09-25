from __future__ import annotations
from random import randrange

from poke_battle_sim.poke_sim import PokeSim
from poke_battle_sim.core.move import Move

import poke_battle_sim.core.pokemon as pk
import poke_battle_sim.core.battle as bt
import poke_battle_sim.core.battlefield as bf

import poke_battle_sim.util.process_move as pm

import poke_battle_sim.conf.global_settings as gs
import poke_battle_sim.conf.global_data as gd


def selection_abilities(
    poke: pk.Pokemon, battlefield: bf.Battlefield, battle: bt.Battle
):
    if poke.has_ability("drizzle") and battlefield.weather != gs.RAIN:
        battlefield.change_weather(gs.RAIN)
        battlefield.weather_count = 999
        battle.add_text("It started to rain!")
    elif poke.has_ability("drought") and battlefield.weather != gs.HARSH_SUNLIGHT:
        battlefield.change_weather(gs.HARSH_SUNLIGHT)
        battlefield.weather_count = 999
        battle.add_text("The sunlight turned harsh!")
    elif poke.has_ability("snow-warning") and battlefield.weather != gs.HAIL:
        battlefield.change_weather(gs.HAIL)
        battlefield.weather_count = 999
        battle.add_text("It started to hail!")
    elif poke.has_ability("sand-stream") and battlefield.weather != gs.SANDSTORM:
        battlefield.change_weather(gs.SANDSTORM)
        battlefield.weather_count = 999
        battle.add_text("A sandstorm brewed")
    elif poke.has_ability("water-veil") and poke.nv_status == gs.BURNED:
        pm.cure_nv_status(gs.BURNED, poke, battle)
    elif poke.has_ability("magma-armor") and poke.nv_status == gs.FROZEN:
        pm.cure_nv_status(gs.FROZEN, poke, battle)
    elif poke.has_ability("limber") and poke.nv_status == gs.PARALYZED:
        pm.cure_nv_status(gs.PARALYZED, poke, battle)
    elif poke.has_ability("insomnia") and poke.nv_status == gs.ASLEEP:
        pm.cure_nv_status(gs.ASLEEP, poke, battle)
    elif poke.has_ability("immunity"):
        if poke.nv_status == gs.POISONED or poke.nv_status == gs.BADLY_POISONED:
            pm.cure_nv_status(gs.POISONED, poke, battle)
    elif (
        poke.has_ability("cloud-nine") or poke.has_ability("air-lock")
    ) and battlefield.weather != gs.CLEAR:
        battle.add_text("The effects of weather disappeared.")
        battlefield.change_weather(gs.CLEAR)
    elif poke.has_ability("own-tempo") and poke.v_status[gs.CONFUSED]:
        battle.add_text(poke.nickname + " snapped out of its confusion!")
        poke.v_status[gs.CONFUSED] = 0
    elif (
        poke.has_ability("trace")
        and poke.enemy.current_poke.is_alive
        and poke.enemy.current_poke.ability
        and not poke.enemy.current_poke.has_ability("trace")
    ):
        battle.add_text(
            poke.nickname
            + " copied "
            + poke.enemy.current_poke.nickname
            + "'s "
            + poke.enemy.current_poke.ability
            + "!"
        )
        poke.give_ability(poke.enemy.current_poke.ability)
    elif poke.has_ability("forecast"):
        _forecast_check(poke, battle, battlefield)
    elif (
        poke.has_ability("download")
        and not poke.ability_activated
        and poke.enemy.current_poke.is_alive
    ):
        poke.enemy.current_poke.calculate_stats_effective()
        if (
            poke.enemy.current_poke.stats_effective[gs.DEF]
            < poke.enemy.current_poke.stats_effective[gs.SP_DEF]
        ):
            pm.give_stat_change(poke, battle, gs.ATK, 1)
        else:
            pm.give_stat_change(poke, battle, gs.SP_ATK, 1)
        poke.ability_activated = True
    elif poke.has_ability("anticipation") and poke.enemy.current_poke.is_alive:
        if any(
            [
                pm._calculate_type_ef(poke, move) > 1 or move.id in [20, 55, 62]
                for move in poke.enemy.current_poke.moves
            ]
        ):
            battle.add_text(poke.nickname + " shuddered!")
    elif poke.has_ability("forewarn") and poke.enemy.current_poke.is_alive:
        alert = _rand_max_power(poke.enemy.current_poke)
        battle.add_text(poke.nickname + "'s Forewarn alerted it to " + alert.name)
    elif (
        poke.has_ability("frisk")
        and poke.enemy.current_poke.ability
        and poke.enemy.current_poke.item
    ):
        battle.add_text(
            poke.nickname
            + " frisked "
            + poke.enemy.current_poke.nickname
            + " and found its "
            + poke.enemy.current_poke.item
            + "!"
        )
    elif poke.has_ability("multitype") and poke.item in gd.PLATE_DATA:
        poke.types = (gd.PLATE_DATA[poke.item], None)
        battle.add_text(
            poke.nickname + " transformed into the " + poke.types[0].upper() + " type!"
        )


def enemy_selection_abilities(
    enemy_poke: pk.Pokemon, battlefield: bf.Battlefield, battle: bt.Battle
):
    poke = enemy_poke.enemy.current_poke
    if not poke.is_alive:
        return
    if poke.has_ability("intimidate"):
        pm.give_stat_change(enemy_poke, battle, gs.ATK, -1, forced=True)
    elif poke.has_ability("trace") and enemy_poke.ability:
        battle.add_text(
            poke.nickname
            + " copied "
            + enemy_poke.nickname
            + "'s "
            + enemy_poke.ability
            + "!"
        )
        poke.give_ability(enemy_poke.ability)
    elif poke.has_ability("download") and not poke.ability_activated:
        enemy_poke.calculate_stats_effective()
        if enemy_poke.stats_effective[gs.DEF] < enemy_poke.stats_effective[gs.SP_DEF]:
            pm.give_stat_change(poke, battle, gs.ATK, 1)
        else:
            pm.give_stat_change(poke, battle, gs.SP_ATK, 1)
        poke.ability_activated = True
    elif poke.has_ability("anticipation") and poke.enemy.current_poke.is_alive:
        if any(
            [
                pm._calculate_type_ef(poke, move) > 1 or move.id in [20, 55, 62]
                for move in poke.enemy.current_poke.moves
            ]
        ):
            battle.add_text(poke.nickname + " shuddered!")
    elif poke.has_ability("forewarn"):
        alert = _rand_max_power(enemy_poke)
        battle.add_text(poke.nickname + "'s Forewarn alerted it to " + alert.name)
    elif (
        poke.has_ability("frisk")
        and poke.enemy.current_poke.ability
        and poke.enemy.current_poke.item
    ):
        battle.add_text(
            poke.nickname
            + " frisked "
            + poke.enemy.current_poke.nickname
            + " and found its "
            + poke.enemy.current_poke.item
            + "!"
        )


def end_turn_abilities(poke: pk.Pokemon, battle: bt.Battle):
    if poke.has_ability("speed-boost"):
        pm.give_stat_change(poke, battle, gs.SPD, 1)
    elif poke.has_ability("slow-start"):
        poke.ability_count += 1
    elif (
        poke.has_ability("bad-dreams")
        and poke.enemy.current_poke.is_alive
        and poke.enemy.current_poke.nv_status == gs.ASLEEP
    ):
        battle.add_text(poke.enemy.current_poke.nickname + " is tormented!")
        poke.enemy.current_poke.take_damage(max(1, poke.enemy.current_poke.max_hp // 8))


def type_protection_abilities(
    defender: pk.Pokemon, move_data: Move, battle: bt.Battle
) -> bool:
    if defender.has_ability("volt-absorb") and move_data.type == "electric":
        battle.add_text(
            defender.nickname + " absorbed " + move_data.name + " with Volt Absorb!"
        )
        if not defender.cur_hp == defender.max_hp:
            defender.heal(defender.max_hp // 4)
        return True
    elif defender.has_ability("water-absorb") and move_data.type == "water":
        battle.add_text(
            defender.nickname + " absorbed " + move_data.name + " with Water Absorb!"
        )
        if not defender.cur_hp == defender.max_hp:
            defender.heal(defender.max_hp // 4)
        return True
    elif defender.has_ability("flash-fire") and move_data.type == "fire":
        battle.add_text("It doesn't affect " + defender.nickname)
        defender.ability_activated = True
        return True
    return False


def on_hit_abilities(
    attacker: pk.Pokemon, defender: pk.Pokemon, battle: bt.Battle, move_data: Move
) -> bool:
    made_contact = move_data.name in gd.CONTACT_CHECK
    if defender.has_ability("static") and made_contact and randrange(10) < 3:
        pm.paralyze(attacker, battle)
    elif defender.has_ability("rough-skin") and made_contact:
        attacker.take_damage(max(1, attacker.max_hp // 16))
        battle.add_text(attacker.nickname + " was hurt!")
    elif defender.has_ability("effect-spore") and made_contact and randrange(10) < 3:
        pm.give_nv_status(randrange(3, 6), attacker, battle)
    elif (
        defender.has_ability("color-change")
        and move_data.type not in defender.types
        and PokeSim.is_valid_type(move_data.type)
    ):
        defender.types = (move_data.type, None)
        battle.add_text(
            defender.nickname
            + " transformed into the "
            + move_data.type.upper()
            + " type!"
        )
    elif (
        defender.has_ability("wonder-guard")
        and pm._calculate_type_ef(defender, move_data) < 2
    ):
        battle.add_text("It doesn't affect " + defender.nickname)
        return True
    elif defender.has_ability("flame-body") and made_contact and randrange(10) < 3:
        pm.burn(attacker, battle)
    elif (
        defender.has_ability("poison-point")
        and made_contact
        and not "steel" in attacker.types
        and not "poison" in attacker.types
        and randrange(10) < 3
    ):
        pm.poison(attacker, battle)
    elif defender.has_ability("cute-charm") and made_contact and randrange(10) < 3:
        pm.infatuate(defender, attacker, battle)
    elif defender.has_ability("motor-drive") and move_data.type == "electric":
        pm.give_stat_change(defender, battle, gs.SPD, 1)
        return True
    return False


def stat_calc_abilities(poke: pk.Pokemon):
    if (
        poke.has_ability("swift-swim")
        and poke.cur_battle.battlefield.weather == gs.RAIN
    ):
        poke.stats_effective[gs.SPD] *= 2
    elif (
        poke.has_ability("chlorophyll")
        and poke.cur_battle.battlefield.weather == gs.HARSH_SUNLIGHT
    ):
        poke.stats_effective[gs.SPD] *= 2
    elif poke.has_ability("huge-power") or poke.has_ability("pure-power"):
        poke.stats_effective[gs.ATK] *= 2
    elif poke.has_ability("hustle") or (poke.has_ability("guts") and poke.nv_status):
        poke.stats_effective[gs.ATK] = int(poke.stats_effective[gs.ATK] * 1.5)
    elif poke.has_ability("marvel-scale") and poke.nv_status:
        poke.stats_effective[gs.DEF] = int(poke.stats_effective[gs.DEF] * 1.5)
    elif (
        poke.has_ability("solar-power")
        and poke.cur_battle.battlefield.weather == gs.HARSH_SUNLIGHT
    ):
        poke.stats_effective[gs.SP_ATK] = int(poke.stats_effective[gs.SP_ATK] * 1.5)
    elif poke.has_ability("quick-feet") and poke.nv_status:
        poke.stats_effective[gs.SPD] = int(poke.stats_effective[gs.SPD] * 1.5)
    elif poke.has_ability("slow-start") and poke.ability_count < 5:
        poke.stats_effective[gs.ATK] //= 2
        poke.stats_effective[gs.SPD] //= 2
    elif (
        poke.has_ability("flower-gift")
        and poke.cur_battle.battlefield.weather == gs.HARSH_SUNLIGHT
    ):
        poke.stats_effective[gs.ATK] = int(poke.stats_effective[gs.ATK] * 1.5)
        poke.stats_effective[gs.SP_DEF] = int(poke.stats_effective[gs.SP_DEF] * 1.5)
    elif poke.has_ability("unburden") and poke.unburden:
        poke.stats_effective[gs.SPD] *= 2


def damage_calc_abilities(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battle: bt.Battle,
    move_data: Move,
    t_mult: int,
):
    if (
        attacker.has_ability("flash-fire")
        and attacker.ability_activated
        and move_data.type == "fire"
    ):
        move_data.power = int(move_data.power * 1.5)
    elif (
        attacker.has_ability("overgrow")
        and move_data.type == "grass"
        and attacker.cur_hp <= attacker.max_hp // 3
    ):
        move_data.power = int(move_data.power * 1.5)
    elif (
        attacker.has_ability("blaze")
        and move_data.type == "fire"
        and attacker.cur_hp <= attacker.max_hp // 3
    ):
        move_data.power = int(move_data.power * 1.5)
    elif (
        attacker.has_ability("torrent")
        and move_data.type == "water"
        and attacker.cur_hp <= attacker.max_hp // 3
    ):
        move_data.power = int(move_data.power * 1.5)
    elif (
        attacker.has_ability("swarm")
        and move_data.type == "bug"
        and attacker.cur_hp <= attacker.max_hp // 3
    ):
        move_data.power = int(move_data.power * 1.5)
    elif attacker.has_ability("rivalry"):
        if attacker.gender == defender.gender and (
            attacker.gender == "male" or attacker.gender == "female"
        ):
            move_data.power = int(move_data.power * 1.25)
        elif (attacker.gender == "female" and defender.gender == "male") or (
            attacker.gender == "male" and defender.gender == "female"
        ):
            move_data.power = int(move_data.power * 0.75)
    elif attacker.has_ability("iron-fist") and move_data.name in gd.PUNCH_CHECK:
        move_data.power *= int(move_data.power * 1.2)
    elif attacker.has_ability("normalize"):
        move_data.type = "normal"
    elif attacker.has_ability("technician") and move_data.power <= 60:
        move_data.power = int(move_data.power * 1.5)
    elif attacker.has_ability("tinted-lens") and t_mult < 1:
        move_data.power *= 2
    elif attacker.has_ability("reckless") and move_data.name in gd.RECOIL_CHECK:
        move_data.power = int(move_data.power * 1.2)

    if defender.has_ability("heatproof") and move_data.type == "fire":
        move_data.power //= 2
    elif (
        defender.has_ability("filter") or defender.has_ability("solid-rock")
    ) and t_mult > 1:
        move_data.power *= 0.75


def homc_abilities(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
) -> float:
    ability_mult = 1
    if defender.has_ability("sand-veil") and battlefield.weather == gs.SANDSTORM:
        ability_mult *= 0.8
    elif defender.has_ability("snow-cloak") and battlefield.weather == gs.HAIL:
        ability_mult *= 0.8
    elif defender.has_ability("compound-eyes"):
        ability_mult *= 1.3
    elif defender.has_ability("hustle") and move_data.category == gs.PHYSICAL:
        ability_mult *= 0.8
    elif defender.has_ability("tangled-feet") and defender.v_status[gs.CONFUSED]:
        ability_mult *= 0.5
    elif defender.has_ability("thick-fat") and (
        move_data.type == "fire" or move_data.type == "ice"
    ):
        ability_mult *= 0.5
    return ability_mult


def pre_move_abilities(
    attacker: pk.Pokemon, defender: pk.Pokemon, battle: bt.Battle, move_data: Move
):
    if attacker.has_ability("serene-grace") and move_data.ef_chance:
        move_data.ef_chance *= 2


def weather_change_abilities(battle: bt.Battle, battlefield: bf.Battlefield):
    _forecast_check(battle.t1.current_poke, battle, battlefield)
    _forecast_check(battle.t2.current_poke, battle, battlefield)


def _forecast_check(poke: pk.Pokemon, battle: bt.Battle, battlefield: bf.Battlefield):
    if poke.is_alive and poke.has_ability("forecast") and poke.name == "castform":
        if battlefield.weather == gs.HARSH_SUNLIGHT:
            poke.types = ("fire", None)
        elif battlefield.weather == gs.RAIN:
            poke.types = ("water", None)
        elif battlefield.weather == gs.HAIL:
            poke.types = ("ice", None)
        else:
            poke.types = ("normal", None)
        battle.add_text(
            poke.nickname + " transformed into the " + poke.types[0].upper() + " type!"
        )


def _rand_max_power(poke: pk.Pokemon) -> Move:
    p_max, p_moves = None, []
    for move in poke.moves:
        if not move.power and not p_max:
            p_moves.append(move)
        elif not move.power and p_max:
            continue
        elif (move.power and not p_max) or move.power > p_max:
            p_max = move.power
            p_moves = [move]
        elif move.power == p_max:
            p_moves.append(move)
    return p_moves[randrange(len(p_moves))]
