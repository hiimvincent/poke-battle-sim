from __future__ import annotations
from random import randrange

from poke_battle_sim.poke_sim import PokeSim
from poke_battle_sim.core.move import Move

import poke_battle_sim.core.pokemon as pk
import poke_battle_sim.core.battle as bt
import poke_battle_sim.core.battlefield as bf

import poke_battle_sim.util.process_ability as pa
import poke_battle_sim.util.process_item as pi

import poke_battle_sim.conf.global_settings as gs
import poke_battle_sim.conf.global_data as gd


def process_move(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
):
    if _pre_process_status(attacker, defender, battlefield, battle, move_data):
        return
    battle.add_text(attacker.nickname + " used " + cap_name(move_data.name) + "!")
    battle.last_move_next = attacker.last_move_next = move_data
    if not _calculate_hit_or_miss(
        attacker, defender, battlefield, battle, move_data, is_first
    ):
        return
    attacker.last_successful_move_next = move_data
    if _meta_effect_check(attacker, defender, battlefield, battle, move_data, is_first):
        return
    _process_effect(attacker, defender, battlefield, battle, move_data, is_first)
    _post_process_status(attacker, defender, battlefield, battle, move_data)
    battle._faint_check()


def _calculate_type_ef(defender: pk.Pokemon, move_data: Move) -> float:
    if move_data.type == "typeless":
        return 1
    if (
        move_data.type == "ground"
        and not defender.grounded
        and (defender.magnet_rise or defender.has_ability("levitate"))
    ):
        return 0

    vulnerable_types = []
    if move_data.type == "ground" and "flying" in defender.types and defender.grounded:
        vulnerable_types.append("flying")
    if (
        (
            defender.foresight_target
            or defender.enemy.current_poke.has_ability("scrappy")
        )
        and move_data.type in ("normal", "fighting")
        and "ghost" in defender.types
    ):
        vulnerable_types.append("ghost")
    if defender.me_target and move_data.type == "psychic" and "dark" in defender.types:
        vulnerable_types.append("dark")

    if defender.types[0] in vulnerable_types:
        t_mult = 1
    else:
        t_mult = PokeSim.get_type_ef(move_data.type, defender.types[0])
    if defender.types[1]:
        if defender.types[1] not in vulnerable_types:
            t_mult *= PokeSim.get_type_ef(move_data.type, defender.types[1])
    return t_mult


def _calculate_damage(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    crit_chance: int = None,
    inv_bypass: bool = False,
    skip_fc: bool = False,
    skip_dmg: bool = False,
    skip_txt: bool = False
) -> int:
    if battle.winner or move_data.category == gs.STATUS:
        return
    if not defender.is_alive:
        _missed(attacker, battle)
        return
    if not inv_bypass and _invulnerability_check(
        attacker, defender, battlefield, battle, move_data
    ):
        return
    if not move_data.power:
        return
    t_mult = _calculate_type_ef(defender, move_data)
    if not skip_txt and not t_mult or (t_mult < 2 and defender.has_ability("wonder-guard")):
        battle.add_text("It doesn't affect " + defender.nickname)
        return
    if pa.type_protection_abilities(defender, move_data, battle):
        return

    cc = crit_chance + attacker.crit_stage if crit_chance else attacker.crit_stage
    if attacker.has_ability("super-luck"):
        cc += 1
    if attacker.item == "scope-lens" or attacker.item == "razor-claw":
        cc += 1
    elif attacker.item == "lucky-punch" and attacker.name == "chansey":
        cc += 2
    if (
        not defender.trainer.lucky_chant
        and not defender.has_ability("battle-armor")
        and not defender.has_ability("shell-armor")
        and _calculate_crit(cc)
    ):
        crit_mult = 2 if not attacker.has_ability("sniper") else 3
        battle.add_text("A critical hit!")
    else:
        crit_mult = 1

    if not skip_txt and t_mult < 1:
        battle.add_text("It's not very effective...")
    elif not skip_txt and t_mult > 1:
        battle.add_text("It's super effective!")

    attacker.calculate_stats_effective(ignore_stats=defender.has_ability("unaware"))
    defender.calculate_stats_effective(ignore_stats=attacker.has_ability("unaware"))

    a_stat = gs.ATK if move_data.category == gs.PHYSICAL else gs.SP_ATK
    d_stat = gs.DEF if move_data.category == gs.PHYSICAL else gs.SP_DEF

    if crit_mult == 1:
        atk_ig = attacker.stats_effective[a_stat]
        def_ig = defender.stats_effective[d_stat]
    else:
        def_ig = min(defender.stats_actual[d_stat], defender.stats_effective[d_stat])
        atk_ig = max(attacker.stats_actual[a_stat], attacker.stats_effective[a_stat])
    ad_ratio = atk_ig / def_ig

    if attacker.nv_status == gs.BURNED and not attacker.has_ability("guts"):
        burn = 0.5
    else:
        burn = 1
    if attacker.charged and move_data.type == "electric":
        move_data.power *= 2
    if move_data.type == "electric" and (attacker.mud_sport or defender.mud_sport):
        move_data.power //= 2
    if move_data.type == "fire" and (attacker.water_sport or defender.water_sport):
        move_data.power //= 2
    pa.damage_calc_abilities(attacker, defender, battle, move_data, t_mult)
    pi.damage_calc_items(attacker, defender, battle, move_data)

    if (
        t_mult <= 1
        and (move_data.category == gs.PHYSICAL and defender.trainer.reflect)
        or (move_data.category == gs.SPECIAL and defender.trainer.light_screen)
    ):
        screen = 0.5
    else:
        screen = 1
    weather_mult = 1
    if battlefield.weather == gs.HARSH_SUNLIGHT:
        if move_data.type == "fire":
            weather_mult = 1.5
        elif move_data.type == "water":
            weather_mult = 0.5
    elif battlefield.weather == gs.RAIN:
        if move_data.type == "fire":
            weather_mult = 0.5
        elif move_data.type == "water":
            weather_mult = 1.5

    if move_data.type == attacker.types[0] or move_data.type == attacker.types[1]:
        stab = 1.5 if not attacker.has_ability("adaptability") else 2
    else:
        stab = 1
    random_mult = randrange(85, 101) / 100

    berry_mult = pi.pre_hit_berries(attacker, defender, battle, move_data, t_mult)
    item_mult = pi.damage_mult_items(attacker, defender, battle, move_data, t_mult)

    damage = (
        (2 * attacker.level / 5 + 2) * move_data.power * ad_ratio
    ) / 50 * burn * screen * weather_mult + 2
    damage *= crit_mult * item_mult * random_mult * stab * t_mult * berry_mult
    damage = int(damage)
    if skip_dmg:
        return damage
    damage_done = defender.take_damage(damage, move_data)
    if not skip_fc:
        battle._faint_check()
    if (
        crit_mult > 1
        and defender.is_alive
        and defender.has_ability("anger-point")
        and defender.stat_stages[gs.ATK] < 6
    ):
        battle.add_text(defender.nickname + " maxed it's Attack!")
        defender.stat_stages[gs.ATK] = 6
    pi.post_damage_items(attacker, battle, damage_done)
    return damage_done


def _calculate_hit_or_miss(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
):
    d_eva_stage = defender.evasion_stage
    a_acc_stage = attacker.accuracy_stage
    if defender.foresight_target or defender.me_target:
        if defender.evasion_stage > 0:
            d_eva_stage = 0
    if attacker.has_ability("unaware"):
        d_eva_stage = 0
    if defender.has_ability("unaware"):
        a_acc_stage = 0
    stage = a_acc_stage - d_eva_stage
    stage_mult = max(3, 3 + stage) / max(3, 3 - stage)
    ability_mult = pa.homc_abilities(attacker, defender, battlefield, battle, move_data)
    item_mult = pi.homc_items(
        attacker, defender, battlefield, battle, move_data, is_first
    )

    ma = move_data.acc
    if _special_move_acc(attacker, defender, battlefield, battle, move_data):
        return True
    if not ma:
        return True
    if defender.mr_count and defender.mr_target and attacker is defender.mr_target:
        return True
    if attacker.has_ability("no-guard") or defender.has_ability("no-guard"):
        return True
    if attacker.next_will_hit:
        attacker.next_will_hit = False
        return True

    if ma == -1:
        res = randrange(1, 101) <= attacker.level - defender.level + 30
    else:
        hit_threshold = (
            ma * stage_mult * battlefield.acc_modifier * item_mult * ability_mult
        )
        res = randrange(1, 101) <= hit_threshold
    if not res:
        if defender.evasion_stage > 0:
            battle.add_text(defender.nickname + " avoided the attack!")
        else:
            _missed(attacker, battle)
    return res


def _meta_effect_check(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
) -> bool:
    if _magic_coat_check(attacker, defender, battlefield, battle, move_data, is_first):
        return True
    if _snatch_check(attacker, defender, battlefield, battle, move_data, is_first):
        return True
    if _protect_check(defender, battle, move_data):
        return True
    if _soundproof_check(defender, battle, move_data):
        return True
    if _grounded_check(attacker, battle, move_data):
        return True
    if _truant_check(attacker, battle, move_data):
        return True
    _normalize_check(attacker, move_data)
    _extra_flinch_check(attacker, defender, battle, move_data, is_first)
    return False


def _process_effect(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
):
    pa.pre_move_abilities(attacker, defender, battle, move_data)
    ef_id = move_data.ef_id

    crit_chance = None
    inv_bypass = False
    cc_ib = [crit_chance, inv_bypass]

    if _MOVE_EFFECTS[ef_id](
        attacker, defender, battlefield, battle, move_data, is_first, cc_ib
    ):
        _calculate_damage(
            attacker,
            defender,
            battlefield,
            battle,
            move_data,
            crit_chance=cc_ib[0],
            inv_bypass=cc_ib[0],
        )


def _calculate_crit(crit_chance: int = None) -> bool:
    if not crit_chance:
        return randrange(16) < 1
    elif crit_chance == 1:
        return randrange(9) < 1
    elif crit_chance == 2:
        return randrange(5) < 1
    elif crit_chance == 3:
        return randrange(4) < 1
    elif crit_chance == 4:
        return randrange(3) < 1
    else:
        return randrange(1000) < crit_chance


def _invulnerability_check(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
) -> bool:
    if attacker.has_ability("no-guard") or defender.has_ability("no-guard"):
        return False
    if defender.invulnerable:
        if defender.in_air or defender.in_ground or defender.in_water:
            _missed(attacker, battle)
        return True
    return False


def _pre_process_status(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
) -> bool:
    _mold_breaker_check(attacker, defender, end_turn=False)
    if attacker.inv_count:
        attacker.inv_count -= 1
        if not attacker.inv_count:
            attacker.invulnerable = False
            attacker.in_ground = False
            attacker.in_air = False
            attacker.in_water = False
    if attacker.prio_boost:
        attacker.prio_boost = False
    if attacker.nv_status == gs.FROZEN:
        if move_data.name in gd.FREEZE_CHECK or randrange(5) < 1:
            cure_nv_status(gs.FROZEN, attacker, battle)
        else:
            battle.add_text(attacker.nickname + " is frozen solid!")
            return True
    if attacker.nv_status == gs.ASLEEP:
        if not attacker.nv_counter:
            attacker.nv_status = 0
        else:
            attacker.nv_counter -= 1
        if attacker.nv_counter and attacker.has_ability("early-bird"):
            attacker.nv_counter -= 1
        if attacker.nv_counter > 0:
            battle.add_text(attacker.nickname + " is fast asleep!")
            if move_data.name != "snore" and move_data.name != "sleep-talk":
                return True
        battle.add_text(attacker.nickname + " woke up!")
    if attacker.v_status[gs.FLINCHED]:
        attacker.v_status[gs.FLINCHED] = 0
        battle.add_text(attacker.nickname + " flinched and couldn't move")
        if attacker.has_ability("steadfast"):
            give_stat_change(attacker, battle, gs.ATK, 1)
        return True
    if attacker.nv_status == gs.PARALYZED:
        if randrange(4) < 1:
            battle.add_text(attacker.nickname + " is paralyzed! It can't move!")
            return True
    if attacker.infatuation:
        if not attacker.infatuation is defender:
            attacker.infatuation = None
            battle.add_text(attacker.nickname + " got over its infatuation!")
        elif randrange(2) < 1:
            battle.add_text(attacker.nickname + " is immobilized by love!")
            return True
    if attacker.v_status[gs.CONFUSED]:
        attacker.v_status[gs.CONFUSED] -= 1
        if attacker.v_status[gs.CONFUSED]:
            battle.add_text(attacker.nickname + " is confused!")
            if randrange(2) < 1:
                battle.add_text("It hurt itself in its confusion!")
                self_attack = Move(
                    [0, "self-attack", 1, "typeless", 40, 1, 999, 0, 10, 2, 1, "", "", ""]
                )
                _calculate_damage(
                    attacker, attacker, battlefield, battle, self_attack, crit_chance=0
                )
                return True
        else:
            battle.add_text(attacker.nickname + " snapped out of its confusion!")
    return False


def _post_process_status(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
):
    _mold_breaker_check(attacker, defender)


def _generate_2_to_5() -> int:
    n = randrange(8)
    if n < 3:
        num_hits = 2
    elif n < 6:
        num_hits = 3
    elif n < 7:
        num_hits = 4
    else:
        num_hits = 5
    return num_hits


def confuse(
    recipient: pk.Pokemon, battle: bt.Battle, forced: bool = False, bypass: bool = False
):
    if (
        not recipient.is_alive
        or recipient.substitute
        or recipient.has_ability("own-tempo")
    ):
        if forced:
            _failed(battle)
        return
    if _safeguard_check(recipient, battle):
        return
    if not forced and not bypass and recipient.has_ability("shield-dust"):
        return
    if forced and recipient.v_status[gs.CONFUSED]:
        battle.add_text(recipient.nickname + " is already confused!")
        return
    recipient.v_status[gs.CONFUSED] = _generate_2_to_5()
    battle.add_text(recipient.nickname + " became confused!")
    pi.status_items(recipient, battle)


def _flinch(
    recipient: pk.Pokemon, battle: bt.Battle, is_first: bool, forced: bool = False
):
    if (
        not recipient.is_alive
        or recipient.substitute
        or recipient.has_ability("shield-dust")
    ):
        return
    if is_first and recipient.is_alive and not recipient.v_status[gs.FLINCHED]:
        if not recipient.has_ability("inner-focus"):
            recipient.v_status[gs.FLINCHED] = 1
        elif forced:
            battle.add_text(
                recipient.nickname + " won't flinch because of its Inner Focus!"
            )


def infatuate(
    attacker: pk.Pokemon, defender: pk.Pokemon, battle: bt.Battle, forced: bool = False
):
    if (
        not defender.is_alive
        or defender.infatuation
        or defender.has_ability("oblivious")
    ):
        if forced:
            _failed(battle)
        return
    if (attacker.gender == "male" and defender.gender == "female") or (
        attacker.gender == "female" and defender.gender == "male"
    ):
        defender.infatuation = attacker
        battle.add_text(
            defender.nickname + " fell in love with " + attacker.nickname + "!"
        )
        pi.status_items(defender, battle)


def give_stat_change(
    recipient: pk.Pokemon,
    battle: bt.Battle,
    stat: int,
    amount: int,
    forced: bool = False,
    bypass: bool = False,
):
    if not recipient.is_alive:
        if forced:
            _failed(battle)
        return
    if (
        amount < 0
        and not bypass
        and (
            recipient.substitute
            or recipient.has_ability("clear-body")
            or recipient.has_ability("white-smoke")
        )
    ):
        if forced:
            _failed(battle)
        return
    if (
        amount < 0
        and not forced
        and not bypass
        and recipient.has_ability("shield-dust")
    ):
        return
    if recipient.has_ability("simple"):
        amount *= 2
    if stat == 6:
        r_stat = recipient.accuracy_stage
        if amount < 0 and recipient.has_ability("keen-eye"):
            if forced:
                _failed(battle)
            return
        recipient.accuracy_stage = _fit_stat_bounds(recipient.accuracy_stage + amount)
    elif stat == 7:
        r_stat = recipient.evasion_stage
        recipient.evasion_stage = _fit_stat_bounds(recipient.evasion_stage + amount)
    else:
        r_stat = recipient.stat_stages[stat]
        if stat == gs.ATK and amount < 0 and recipient.has_ability("hyper-cutter"):
            if forced:
                _failed(battle)
            return
        recipient.stat_stages[stat] = _fit_stat_bounds(
            recipient.stat_stages[stat] + amount
        )
    if -6 < r_stat < 6 or forced:
        battle.add_text(_stat_text(recipient, stat, amount))
    return


def _fit_stat_bounds(stage: int):
    if stage >= 0:
        return min(6, stage)
    else:
        return max(-6, stage)


def _stat_text(recipient: pk.Pokemon, stat: int, amount: int) -> str:
    if stat == gs.ACC:
        cur_stage = recipient.accuracy_stage
    elif stat == gs.EVA:
        cur_stage = recipient.evasion_stage
    else:
        cur_stage = recipient.stat_stages[stat]
    if not amount:
        return
    base = recipient.nickname + "'s " + gs.STAT_TO_NAME[stat]
    if amount > 0:
        dif = min(6 - cur_stage, amount)
        if dif <= 0:
            base += " won't go any higher!"
        elif dif == 1:
            base += " rose!"
        elif dif == 2:
            base += " rose sharply!"
        else:
            base += " rose drastically!"
    else:
        dif = max(-6 - cur_stage, amount)
        if dif >= 0:
            base += " won't go any lower!"
        elif dif == -1:
            base += " fell!"
        elif dif == -2:
            base += " fell harshly!"
        else:
            base += " fell severely!"
    return base


def give_nv_status(
    status: int, recipient: pk.Pokemon, battle: bt.Battle, forced: bool = False
):
    if status == gs.BURNED:
        burn(recipient, battle, forced)
    elif status == gs.FROZEN:
        freeze(recipient, battle, forced)
    elif status == gs.PARALYZED:
        paralyze(recipient, battle, forced)
    elif status == gs.POISONED:
        poison(recipient, battle, forced)
    elif status == gs.ASLEEP:
        sleep(recipient, battle, forced)
    elif status == gs.BADLY_POISONED:
        badly_poison(recipient, battle, forced)


def burn(recipient: pk.Pokemon, battle: bt.Battle, forced: bool = False):
    if (
        not recipient.is_alive
        or recipient.substitute
        or recipient.has_ability("water-veil")
        or (
            recipient.has_ability("leaf-guard")
            and battle.battlefield.weather == gs.HARSH_SUNLIGHT
        )
    ):
        if forced:
            _failed(battle)
        return
    if _safeguard_check(recipient, battle):
        return
    if "fire" in recipient.types:
        if forced:
            _failed(battle)
        return
    if not forced and recipient.has_ability("shield-dust"):
        return
    if forced and recipient.nv_status == gs.BURNED:
        battle.add_text(recipient.nickname + " is already burned!")
    elif not recipient.nv_status:
        recipient.nv_status = gs.BURNED
        recipient.nv_counter = 0
        battle.add_text(recipient.nickname + " was burned!")
        if recipient.has_ability("synchronize"):
            burn(recipient.enemy.current_poke, battle)
        pi.status_items(recipient, battle)


def freeze(recipient: pk.Pokemon, battle: bt.Battle, forced: bool = False):
    if (
        not recipient.is_alive
        or recipient.substitute
        or recipient.has_ability("magma-armor")
        or (
            recipient.has_ability("leaf-guard")
            and battle.battlefield.weather == gs.HARSH_SUNLIGHT
        )
    ):
        if forced:
            _failed(battle)
        return
    if _safeguard_check(recipient, battle):
        return
    if "ice" in recipient.types:
        if forced:
            _failed(battle)
        return
    if not forced and recipient.has_ability("shield-dust"):
        return
    if forced and recipient.nv_status == gs.FROZEN:
        battle.add_text(recipient.nickname + " is already frozen!")
    elif not recipient.nv_status:
        recipient.nv_status = gs.FROZEN
        recipient.nv_counter = 0
        battle.add_text(recipient.nickname + " was frozen solid!")
        if recipient.has_ability("synchronize"):
            freeze(recipient.enemy.current_poke, battle)
        pi.status_items(recipient, battle)


def paralyze(recipient: pk.Pokemon, battle: bt.Battle, forced: bool = False):
    if (
        not recipient.is_alive
        or recipient.substitute
        or recipient.has_ability("limber")
        or (
            recipient.has_ability("leaf-guard")
            and battle.battlefield.weather == gs.HARSH_SUNLIGHT
        )
    ):
        if forced:
            _failed(battle)
        return
    if _safeguard_check(recipient, battle):
        return
    if not forced and recipient.has_ability("shield-dust"):
        return
    if forced and recipient.nv_status == gs.PARALYZED:
        battle.add_text(recipient.nickname + " is already paralyzed!")
    elif not recipient.nv_status:
        recipient.nv_status = gs.PARALYZED
        recipient.nv_counter = 0
        battle.add_text(recipient.nickname + " is paralyzed! It may be unable to move!")
        if recipient.has_ability("synchronize"):
            paralyze(recipient.enemy.current_poke, battle)
        pi.status_items(recipient, battle)


def poison(recipient: pk.Pokemon, battle: bt.Battle, forced: bool = False):
    if (
        not recipient.is_alive
        or recipient.substitute
        or recipient.has_ability("immunity")
        or (
            recipient.has_ability("leaf-guard")
            and battle.battlefield.weather == gs.HARSH_SUNLIGHT
        )
    ):
        if forced:
            _failed(battle)
        return
    if _safeguard_check(recipient, battle):
        return
    if not forced and recipient.has_ability("shield-dust"):
        return
    if forced and recipient.nv_status == gs.POISONED:
        battle.add_text(recipient.nickname + " is already poisoned!")
    elif not recipient.nv_status:
        recipient.nv_status = gs.POISONED
        recipient.nv_counter = 0
        battle.add_text(recipient.nickname + " was poisoned!")
        if recipient.has_ability("synchronize"):
            poison(recipient.enemy.current_poke, battle)
        pi.status_items(recipient, battle)


def sleep(recipient: pk.Pokemon, battle: bt.Battle, forced: bool = False):
    if (
        not recipient.is_alive
        or recipient.substitute
        or recipient.has_ability("insomnia")
        or recipient.has_ability("vital-spirit")
        or (
            recipient.has_ability("leaf-guard")
            and battle.battlefield.weather == gs.HARSH_SUNLIGHT
        )
    ):
        if forced:
            _failed(battle)
        return
    if _safeguard_check(recipient, battle):
        return
    if not forced and recipient.has_ability("shield-dust"):
        return
    if forced and recipient.nv_status == gs.ASLEEP:
        battle.add_text(recipient.nickname + " is already asleep!")
    elif not recipient.nv_status:
        recipient.nv_status = gs.ASLEEP
        recipient.nv_counter = randrange(2, 6)
        battle.add_text(recipient.nickname + " fell asleep!")
        if recipient.has_ability("synchronize"):
            sleep(recipient.enemy.current_poke, battle)
        pi.status_items(recipient, battle)


def badly_poison(recipient: pk.Pokemon, battle: bt.Battle, forced: bool = False):
    if (
        not recipient.is_alive
        or recipient.substitute
        or recipient.has_ability("immunity")
        or (
            recipient.has_ability("leaf-guard")
            and battle.battlefield.weather == gs.HARSH_SUNLIGHT
        )
    ):
        if forced:
            _failed(battle)
        return
    if _safeguard_check(recipient, battle):
        return
    if not forced and recipient.has_ability("shield-dust"):
        return
    if forced and recipient.nv_status == gs.BADLY_POISONED:
        battle.add_text(recipient.nickname + " is already badly poisoned!")
    elif not recipient.nv_status:
        recipient.nv_status = gs.BADLY_POISONED
        recipient.nv_counter = 1
        battle.add_text(recipient.nickname + " was badly poisoned!")
        if recipient.has_ability("synchronize"):
            poison(recipient.enemy.current_poke, battle)
        pi.status_items(recipient, battle)


def cure_nv_status(status: int, recipient: pk.Pokemon, battle: bt.Battle):
    if not recipient.is_alive or not status:
        return
    if recipient.nv_status != status and not (
        status == gs.POISONED and recipient.nv_status == gs.BADLY_POISONED
    ):
        return
    if status == gs.BURNED:
        text = "'s burn was healed!"
    elif status == gs.FROZEN:
        text = " thawed out!"
    elif status == gs.PARALYZED:
        text = " was cured of paralysis!"
    elif status == gs.ASLEEP:
        text = " woke up!"
    else:
        text = " was cured of poison!"

    recipient.nv_status = 0
    battle.add_text(recipient.nickname + text)


def cure_confusion(recipient: pk.Pokemon, battle: bt.Battle):
    if recipient.is_alive and recipient.v_status[gs.CONFUSED]:
        recipient.v_status[gs.CONFUSED] = 0
        battle.add_text(recipient.nickname + " snapped out of its confusion!")


def cure_infatuation(recipient: pk.Pokemon, battle: bt.Battle):
    if recipient.is_alive and recipient.infatuation:
        recipient.infatuation = None
        battle.add_text(recipient.nickname + " got over its infatuation!")


def _magic_coat_check(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
) -> bool:
    if (
        defender.is_alive
        and defender.magic_coat
        and move_data.name in gd.MAGIC_COAT_CHECK
    ):
        battle.add_text(
            attacker.nickname
            + "'s "
            + move_data.name
            + " was bounced back by Magic Coat!"
        )
        _process_effect(defender, attacker, battlefield, battle, move_data, is_first)
        return True
    return False


def _snatch_check(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
) -> bool:
    if defender.is_alive and defender.snatch and move_data.name in gd.SNATCH_CHECK:
        battle.add_text(
            defender.nickname + " snatched " + attacker.nickname + "'s move!"
        )
        _process_effect(defender, attacker, battlefield, battle, move_data, is_first)
        return True
    return False


def _protect_check(defender: pk.Pokemon, battle: bt.Battle, move_data: Move) -> bool:
    if (
        defender.is_alive
        and defender.protect
        and not move_data.name in ["feint", "shadow-force"]
        and move_data.target in gd.PROTECT_TARGETS
    ):
        battle.add_text(defender.nickname + " protected itself!")
        return True
    return False


def _soundproof_check(defender: pk.Pokemon, battle: bt.Battle, move_data: Move) -> bool:
    if (
        defender.is_alive
        and defender.has_ability("soundproof")
        and move_data in gd.SOUNDPROOF_CHECK
    ):
        battle.add_text("It doesn't affect " + defender.nickname)
        return True
    return False


def _grounded_check(attacker: pk.Pokemon, battle: bt.Battle, move_data: Move) -> bool:
    if attacker.grounded and move_data.name in gd.GROUNDED_CHECK:
        _failed(battle)
        return True
    return False


def _truant_check(attacker: pk.Pokemon, battle: bt.Battle, move_data: Move) -> bool:
    if (
        attacker.has_ability("truant")
        and attacker.last_move
        and move_data.name == attacker.last_move.name
    ):
        battle.add_text(attacker.nickname + " loafed around!")
        return True
    return False


def _normalize_check(attacker: pk.Pokemon, move_data: Move):
    if attacker.has_ability("normalize"):
        move_data.type = "normal"


def _extra_flinch_check(
    attacker: pk.Pokemon, defender: pk.Pokemon, battle: bt.Battle, move_data: Move, is_first: bool
):
    if attacker.item == "king's-rock" or attacker.item == "razor-fang":
        if (
            move_data in gd.EXTRA_FLINCH_CHECK
            and not defender.v_status[gs.FLINCHED]
            and is_first
            and randrange(10) < 1
        ):
            _flinch(defender, battle, is_first)


def _mold_breaker_check(
    attacker: pk.Pokemon, defender: pk.Pokemon, end_turn: bool = True
):
    if not attacker.has_ability("mold-breaker"):
        return
    if not end_turn and not defender.ability_suppressed:
        defender.ability_suppressed = True
        attacker.ability_count = 1
    elif end_turn and attacker.ability_count:
        defender.ability_suppressed = False
        attacker.ability_count = 0


def _power_herb_check(attacker: pk.Pokemon, battle: bt.Battle) -> bool:
    if attacker.item == "power-herb":
        battle.add_text(
            attacker.nickname + " became fully charged due to its Power Herb!"
        )
        attacker.give_item(None)
        return True
    return False


def _special_move_acc(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
) -> bool:
    if move_data.name == "thunder":
        if battlefield.weather == gs.RAIN and not defender.in_ground:
            return True
        if battlefield.weather == gs.HARSH_SUNLIGHT:
            move_data.acc = 50
    return False


def _recoil(attacker: pk.Pokemon, battle: bt.Battle, damage: int, move_data: Move):
    if not attacker.is_alive or not damage:
        return
    if attacker.has_ability("rock-head") and move_data.name in gd.RECOIL_CHECK:
        return
    attacker.take_damage(damage)
    battle.add_text(attacker.nickname + " is hit with recoil!")


def cap_name(move_name: str) -> str:
    move_name = move_name.replace("-", " ")
    words = move_name.split()
    words = [word.capitalize() for word in words]
    return " ".join(words)


def _failed(battle: bt.Battle):
    battle.add_text("But, it failed!")


def _missed(attacker: pk.Pokemon, battle: bt.Battle):
    battle.add_text(attacker.nickname + "'s attack missed!")


def _safeguard_check(poke: pk.Pokemon, battle: bt.Battle) -> bool:
    if poke.trainer.safeguard:
        battle.add_text(poke.nickname + " is protected by Safeguard!")
        return True
    return False


def _ef_000(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    _calculate_damage(attacker, defender, battlefield, battle, move_data)
    return True


def _ef_001(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    _calculate_damage(attacker, defender, battlefield, battle, move_data)
    return True


def _ef_002(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    dmg = _calculate_damage(attacker, defender, battlefield, battle, move_data)
    if attacker.is_alive and dmg and randrange(1, 101) < move_data.ef_chance:
        give_stat_change(
            attacker, battle, move_data.ef_stat, move_data.ef_amount, bypass=True
        )
    return True


def _ef_003(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    dmg = _calculate_damage(attacker, defender, battlefield, battle, move_data)
    if defender.is_alive and dmg and randrange(1, 101) < move_data.ef_chance:
        give_stat_change(defender, battle, move_data.ef_stat, move_data.ef_amount)
    return True


def _ef_004(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    dmg = _calculate_damage(attacker, defender, battlefield, battle, move_data)
    if attacker.is_alive and dmg and randrange(1, 101) < move_data.ef_chance:
        give_nv_status(move_data.ef_stat, attacker, battle)
    return True


def _ef_005(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    dmg = _calculate_damage(attacker, defender, battlefield, battle, move_data)
    if defender.is_alive and dmg and randrange(1, 101) < move_data.ef_chance:
        give_nv_status(move_data.ef_stat, defender, battle)
    return True


def _ef_006(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    dmg = _calculate_damage(attacker, defender, battlefield, battle, move_data)
    if defender.is_alive and dmg and randrange(1, 101) < move_data.ef_chance:
        confuse(defender, battle)
    return True


def _ef_007(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    dmg = _calculate_damage(attacker, defender, battlefield, battle, move_data)
    if defender.is_alive and dmg and randrange(1, 101) < move_data.ef_chance:
        _flinch(defender, battle, is_first)
    return True


def _ef_008(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    cc_ib[0] = 1


def _ef_009(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if attacker.has_moved:
        _failed(battle)
        return True
    dmg = _calculate_damage(attacker, defender, battlefield, battle, move_data)
    if defender.is_alive and dmg:
        _flinch(defender, battle, is_first, forced=True)
    return True


def _ef_010(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if not defender.is_alive:
        _missed(attacker, battle)
    if not attacker.has_ability("skill-link"):
        num_hits = _generate_2_to_5()
    else:
        num_hits = 5
    nh = num_hits
    dmg = _calculate_damage(attacker, defender, battlefield, battle, move_data, skip_fc=True)
    if not dmg:
        nh = 0
    else:
        nh -= 1
    while nh and defender.is_alive:
        _calculate_damage(
            attacker, defender, battlefield, battle, move_data, skip_fc=True, skip_txt=True
        )
        nh -= 1
    battle.add_text("Hit " + str(num_hits) + " time(s)!")
    return True


def _ef_011(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    dmg = _calculate_damage(
        attacker, defender, battlefield, battle, move_data, skip_fc=True
    )
    if not dmg:
        return True
    elif defender.is_alive:
        _calculate_damage(
            attacker, defender, battlefield, battle, move_data, skip_fc=True, skip_txt=True
        )
    else:
        battle.add_text("Hit 1 time(s)!")
        return True
    battle.add_text("Hit 2 time(s)!")
    return True


def _ef_013(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    give_nv_status(move_data.ef_stat, defender, battle, True)
    return True


def _ef_014(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    confuse(defender, battle, True)
    return True


def _ef_016(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    give_stat_change(attacker, battle, move_data.ef_stat, move_data.ef_amount)


def _ef_017(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if defender.is_alive and defender.trainer.mist:
        battle.add_text(defender.nickname + "'s protected by mist.")
        return True
    give_stat_change(defender, battle, move_data.ef_stat, move_data.ef_amount)


def _ef_018(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if defender.in_water:
        move_data.power *= 2
        cc_ib[1] = True


def _ef_019(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if defender.minimized:
        move_data.power *= 2
    dmg = _calculate_damage(attacker, defender, battlefield, battle, move_data)
    if dmg and randrange(10) < 3:
        _flinch(defender, battle, is_first)


def _ef_020(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if not defender.is_alive:
        _missed(attacker, battle)
    if defender.has_ability("sturdy"):
        battle.add_text(defender.nickname + " endured the hit!")
        return True
    if _calculate_type_ef(defender, move_data) != 0:
        defender.take_damage(65535, move_data)
        if not defender.is_alive:
            battle.add_text("It's a one-hit KO!")
    else:
        battle.add_text("It doesn't affect " + defender.nickname)
    return True


def _ef_021(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if not move_data.ef_stat and not _power_herb_check(attacker, battle):
        move_data.ef_stat = 1
        attacker.next_moves.put(move_data)
        battle.add_text(attacker.nickname + " whipped up a whirlwind!")
        return True
    cc_ib[0] = 1


def _ef_022(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if defender.in_air:
        cc_ib[1] = True
        move_data.power *= 2


def _ef_023(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if not move_data.ef_stat and not _power_herb_check(attacker, battle):
        move_data.ef_stat = 1
        attacker.next_moves.put(move_data)
        attacker.in_air = True
        attacker.invulnerable = True
        attacker.inv_count = 1
        battle._pop_text()
        battle.add_text(attacker.nickname + " flew up high!")
        return True


def _ef_024(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    dmg = _calculate_damage(attacker, defender, battlefield, battle, move_data)
    if (
        defender.is_alive
        and dmg
        and not defender.substitute
        and not defender.v_status[gs.BINDING_COUNT]
    ):
        defender.v_status[gs.BINDING_COUNT] = (
            _generate_2_to_5() if attacker.item != "grip-claw" else 5
        )
        defender.binding_poke = attacker
        if move_data.ef_stat == gs.BIND:
            defender.binding_type = "Bind"
            battle.add_text(
                defender.nickname + " was squeezed by " + attacker.nickname + "!"
            )
        elif move_data.ef_stat == gs.WRAP:
            defender.binding_type = "Wrap"
            battle.add_text(
                defender.nickname + " was wrapped by " + attacker.nickname + "!"
            )
        elif move_data.ef_stat == gs.FIRE_SPIN:
            defender.binding_type = "Fire Spin"
            battle.add_text(defender.nickname + " was trapped in the vortex!")
        elif move_data.ef_stat == gs.CLAMP:
            defender.binding_type = "Clamp"
            battle.add_text(attacker.nickname + " clamped " + defender.nickname + "!")
        elif move_data.ef_stat == gs.WHIRLPOOL:
            defender.binding_type = "Whirlpool"
            battle.add_text(defender.nickname + " was trapped in the vortex!")
        elif move_data.ef_stat == gs.SAND_TOMB:
            defender.binding_type = "Sand Tomb"
            battle.add_text(defender.nickname + " was trapped by Sand Tomb!")
        elif move_data.ef_stat == gs.MAGMA_STORM:
            defender.binding_type = "Magma Storm"
            battle.add_text(defender.nickname + " became trapped by swirling magma!")
    return True


def _ef_025(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if not defender.is_alive:
        return True
    dmg = _calculate_damage(attacker, defender, battlefield, battle, move_data)
    if dmg:
        dmg //= 2
    elif dmg == 0 and attacker.enemy and _calculate_type_ef(defender, move_data) == 0:
        dmg = defender.max_hp // 2
    if not dmg:
        return True
    battle.add_text(attacker.nickname + " kept going and crashed!")
    attacker.take_damage(dmg)
    return True


def _ef_026(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if defender.in_ground:
        move_data.power *= 2
        cc_ib[1] = True


def _ef_027(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    dmg = _calculate_damage(attacker, defender, battlefield, battle, move_data)
    if dmg:
        _recoil(attacker, battle, max(1, dmg // 4), move_data)
    return True


def _ef_028(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if not move_data.ef_stat:
        num_turns = randrange(1, 3)
        move_data.ef_stat = num_turns
        attacker.next_moves.put(move_data)
    else:
        move_data.ef_stat -= 1
        if move_data.ef_stat == 0:
            dmg = _calculate_damage(attacker, defender, battlefield, battle, move_data)
            if dmg:
                confuse(attacker, battle, bypass=True)
            return True
        else:
            attacker.next_moves.put(move_data)


def _ef_029(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    dmg = _calculate_damage(attacker, defender, battlefield, battle, move_data)
    if dmg:
        _recoil(attacker, battle, max(1, dmg // 3), move_data)
    return True


def _ef_030(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    dmg = _calculate_damage(attacker, defender, battlefield, battle, move_data)
    if not defender.is_alive or not dmg:
        return True
    if randrange(1, 6) < 2:
        poison(defender, battle)
    dmg = _calculate_damage(attacker, defender, battlefield, battle, move_data)
    if dmg and randrange(5) < 1:
        poison(defender, battle)
    return True


def _ef_031(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if defender.is_alive and _calculate_type_ef(defender, move_data) != 0:
        defender.take_damage(move_data.ef_amount, move_data)
    else:
        _missed(attacker, battle)
    return True


def _ef_032(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    has_disabled = not all([not move.disabled for move in defender.moves])
    if not defender.last_move or not defender.last_move.cur_pp or has_disabled:
        _failed(battle)
    else:
        disabled_move = defender.last_move
        disabled_move.disabled = randrange(4, 8)
        battle.add_text(
            defender.trainer.name
            + "'s "
            + defender.nickname
            + "'s "
            + disabled_move.name
            + " was disabled!"
        )


def _ef_033(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if not attacker.trainer.mist:
        battle.add_text(attacker.trainer.name + "'s team became shrouded in mist!")
        attacker.trainer.mist = 5
    else:
        _failed(battle)


def _ef_034(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    attacker.recharging = True


def _ef_035(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
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


def _ef_036(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if (
        defender.is_alive
        and attacker.last_move_hit_by
        and defender.last_move
        and attacker.last_move_hit_by.name == defender.last_move.name
        and attacker.last_move_hit_by.category == gs.PHYSICAL
        and _calculate_type_ef(defender, move_data)
    ):
        defender.take_damage(attacker.last_damage_taken * 2, move_data)
    else:
        _failed(battle)
    return True


def _ef_037(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if _calculate_type_ef(defender, move_data):
        if defender.is_alive:
            defender.take_damage(attacker.level, move_data)
        else:
            _missed(attacker, battle)
    return True


def _ef_038(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    dmg = _calculate_damage(attacker, defender, battlefield, battle, move_data)
    if dmg:
        heal_amt = max(1, dmg // 2)
        if attacker.item == "big-root":
            heal_amt = int(heal_amt * 1.3)
        if not defender.has_ability("liquid-ooze"):
            attacker.heal(heal_amt, text_skip=True)
            battle.add_text(defender.nickname + " had it's energy drained!")
        else:
            attacker.take_damage(heal_amt)
            battle.add_text(attacker.nickname + " sucked up the liquid ooze!")
    return True


def _ef_039(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if (
        defender.is_alive
        and not defender.substitute
        and not defender.v_status[gs.LEECH_SEED]
    ):
        defender.v_status[gs.LEECH_SEED] = 1
        battle.add_text(defender.nickname + " was seeded!")


def _ef_040(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if (
        not move_data.ef_stat
        and battlefield.weather != gs.HARSH_SUNLIGHT
        and not _power_herb_check(attacker, battle)
    ):
        battle._pop_text()
        battle.add_text(attacker.nickname + " absorbed light!")
        move_data.ef_stat = 1
        attacker.next_moves.put(move_data)
        return True
    if battlefield.weather != gs.HARSH_SUNLIGHT and battlefield.weather != gs.CLEAR:
        move_data.power //= 2


def _ef_041(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if randrange(10) < 3:
        paralyze(defender, battle)


def _ef_042(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if not move_data.ef_stat and not _power_herb_check(attacker, battle):
        move_data.ef_stat = 1
        attacker.next_moves.put(move_data)
        attacker.in_ground = True
        attacker.invulnerable = True
        attacker.inv_count = 1
        battle._pop_text()
        battle.add_text(attacker.nickname + " burrowed its way under the ground!")
        return True


def _ef_043(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if not attacker.rage:
        attacker.rage = True
        for move in attacker.moves:
            if move.name != "rage":
                move.disabled = True


def _ef_044(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if (
        defender.is_alive
        and defender.last_move
        and not attacker.copied
        and not attacker.is_move(defender.last_move.md)
    ):
        attacker.copied = Move(defender.last_move.md)
        attacker.copied.max_pp = min(5, attacker.copied.max_pp)
        attacker.copied.cur_pp = attacker.copied.max_pp
        battle.add_text(
            attacker.nickname + " learned " + cap_name(attacker.copied.name)
        )
    else:
        _failed(battle)

def _ef_046(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    attacker.heal(attacker.max_hp // 2)


def _ef_047(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    attacker.minimized = True
    give_stat_change(attacker, battle, gs.EVA, 1)


def _ef_048(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    attacker.df_curl = True
    give_stat_change(attacker, battle, gs.DEF, 1)


def _ef_049(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    t = attacker.trainer
    num_turns = 5 if attacker.item != "light-clay" else 8
    if move_data.ef_stat == 1:
        if t.light_screen:
            _failed(battle)
            return True
        t.light_screen = num_turns
        battle.add_text("Light Screen raised " + t.name + "'s team's Special Defense!")
    elif move_data.ef_stat == 2:
        if t.reflect:
            _failed(battle)
            return True
        t.reflect = num_turns
        battle.add_text("Light Screen raised " + t.name + "'s team's Defense!")


def _ef_050(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    attacker.reset_stages()
    defender.reset_stages()
    battle.add_text("All stat changes were eliminated!")


def _ef_051(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    attacker.crit_stage += 2
    if attacker.crit_stage > 4:
        attacker.crit_stage = 4
    battle.add_text(attacker.nickname + " is getting pumped!")


def _ef_052(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if not move_data.ef_stat:
        attacker.trapped = True
        move_data.ef_stat = 1
        attacker.bide_count = 2 if is_first else 3
        attacker.next_moves.put(move_data)
        attacker.bide_dmg = 0
        battle.add_text(attacker.nickname + " is storing energy!")
    else:
        battle._pop_text()
        battle.add_text(attacker.nickname + " unleashed energy!")
        if defender.is_alive:
            defender.take_damage(2 * attacker.bide_dmg, move_data)
        else:
            _missed(attacker, battle)
        attacker.bide_dmg = 0
    return True


def _ef_053(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    move_names = [move.name for move in attacker.moves]
    rand_move = PokeSim.get_rand_move()
    attempts = 0
    while (
        attempts < 50
        and (rand_move[gs.MOVE_NAME] in move_names
        or rand_move[gs.MOVE_NAME] in gd.METRONOME_CHECK)
    ):
        rand_move = PokeSim.get_rand_move()
        attempts += 1
    rand_move = Move(rand_move)
    battle.add_text(attacker.nickname + " used " + cap_name(rand_move.name) + "!")
    _process_effect(attacker, defender, battlefield, battle, rand_move, is_first)
    return True


def _ef_054(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if defender.is_alive and defender.last_move:
        battle.add_text(
            attacker.nickname + " used " + cap_name(defender.last_move.name) + "!"
        )
        _process_effect(
            attacker, defender, battlefield, battle, defender.last_move, is_first
        )
    else:
        _failed(battle)
    return True


def _ef_055(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if not defender.is_alive:
        _failed(battle)
        return True
    if attacker.has_ability("damp") or defender.has_ability("damp"):
        battle.add_text(attacker.nickname + " cannot use Self Destruct!")
        return True
    attacker.faint()
    _calculate_damage(attacker, defender, battlefield, battle, move_data)
    return True


def _ef_056(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if not move_data.ef_stat and not _power_herb_check(attacker, battle):
        battle._pop_text()
        battle.add_text(attacker.nickname + " tucked in its head!")
        give_stat_change(attacker, battle, gs.DEF, 1)
        move_data.ef_stat = 1
        attacker.next_moves.put(move_data)
        return True


def _ef_057(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if not defender.is_alive:
        _missed(attacker, battle)
    elif defender.nv_status == gs.ASLEEP:
        dmg = _calculate_damage(attacker, defender, battlefield, battle, move_data)
        if dmg:
            heal_amt = max(1, dmg // 2)
            if attacker.item == "big-root":
                heal_amt = int(heal_amt * 1.3)
            attacker.heal(heal_amt)
        battle.add_text(defender.nickname + "'s dream was eaten!")
    else:
        _failed(battle)
    return True


def _ef_058(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if not move_data.ef_stat and not _power_herb_check(attacker, battle):
        move_data.ef_stat = 1
        defender.next_moves.put(move_data)
        battle._pop_text()
        battle.add_text(attacker.nickname + " became clocked in a harsh light!")
    else:
        dmg = _calculate_damage(
            attacker, defender, battlefield, battle, move_data, crit_chance=1
        )
        if dmg and randrange(10) < 3:
            _flinch(defender, battle, is_first)
    return True


def _ef_059(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if defender.is_alive and not defender.transformed and not attacker.transformed:
        attacker.transform(defender)
        battle.add_text(attacker.nickname + " transformed into " + defender.name + "!")
    else:
        _failed(battle)
    return True


def _ef_060(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    dmg = attacker.level * (randrange(0, 11) * 10 + 50) // 100
    if defender.is_alive:
        defender.take_damage(dmg if dmg != 0 else 1, move_data)
    else:
        _missed(attacker, battle)
    return True


def _ef_061(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    battle.add_text("But nothing happened!")
    return True


def _ef_062(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if not defender.is_alive:
        _failed(battle)
        return True
    if attacker.has_ability("damp") or defender.has_ability("damp"):
        battle.add_text(attacker.nickname + " cannot use Explosion!")
        return True
    attacker.faint()
    old_def = defender.stats_actual[gs.DEF]
    defender.stats_actual[gs.DEF] //= 2
    _calculate_damage(attacker, defender, battlefield, battle, move_data)
    defender.stats_actual[gs.DEF] = old_def
    return True


def _ef_063(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if not attacker.has_ability("insomnia") and not attacker.has_ability(
        "vital-spirit"
    ):
        attacker.nv_status = gs.ASLEEP
        attacker.nv_counter = 3
        battle.add_text(attacker.nickname + " went to sleep!")
        attacker.heal(attacker.max_hp)
    else:
        _failed(battle)


def _ef_064(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    move_types = [
        move.type for move in attacker.moves if move.type not in attacker.types
    ]
    move_types = PokeSim.filter_valid_types(move_types)
    if not len(move_types):
        _failed(battle)
        return True
    attacker.types = (move_types[randrange(len(move_types))], None)


def _ef_065(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    dmg = _calculate_damage(attacker, defender, battlefield, battle, move_data)
    if dmg and defender.is_alive and randrange(1, 101) < move_data.ef_chance:
        give_nv_status(randrange(1, 4), defender, battle)
    return True


def _ef_066(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if not defender.is_alive or _calculate_type_ef(defender, move_data) == 0:
        _failed(battle)
        return True
    else:
        dmg = defender.max_hp // 2
        defender.take_damage(dmg if dmg > 0 else 1, move_data)
    return True


def _ef_067(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if attacker.substitute:
        _failed(battle)
        return True
    if attacker.cur_hp - attacker.max_hp // 4 < 0:
        battle.add_text("But it does not have enough HP left to make a substitute!")
        return True
    attacker.substitute = attacker.take_damage(attacker.max_hp // 4) + 1
    battle.add_text(attacker.nickname + " made a substitute!")


def _ef_068(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    battle._pop_text()
    battle.add_text(attacker.nickname + " has no moves left!")
    battle.add_text(attacker.nickname + " used Struggle!")
    _calculate_damage(attacker, defender, battlefield, battle, move_data)
    struggle_dmg = max(1, attacker.max_hp // 4)
    _recoil(attacker, battle, struggle_dmg, move_data)


def _ef_069(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if (
        attacker.transformed
        or not move_data in attacker.o_moves
        or not defender.is_alive
        or not defender.last_move
        or attacker.is_move(defender.last_move.name)
    ):
        _failed(battle)
        return True
    attacker.moves[move_data.pos] = Move(defender.last_move.md)


def _ef_070(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if not defender.is_alive:
        _missed(attacker, battle)
    num_hits = 0
    while num_hits < 3 and defender.is_alive:
        _calculate_damage(
            attacker, defender, battlefield, battle, move_data, skip_fc=True
        )
        move_data.power += 10
        num_hits += 1
    battle.add_text("Hit" + str(num_hits) + "time(s)!")
    return True


def _ef_071(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    dmg = _calculate_damage(attacker, defender, battlefield, battle, move_data)
    if (
        defender.item
        and dmg
        and not attacker.item
        and not defender.substitute
        and not defender.has_ability("sticky-hold")
        and not defender.has_ability("multitype")
    ):
        battle.add_text(
            attacker.nickname
            + " stole "
            + defender.nickname
            + "'s "
            + cap_name(defender.item)
            + "!"
        )
        attacker.give_item(defender.item)
        defender.give_item(None)
    return True


def _ef_072(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if defender.is_alive and not defender.invulnerable:
        defender.perma_trapped = True
        battle.add_text(defender.nickname + " can no longer escape!")
    else:
        _failed(battle)


def _ef_073(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if defender.is_alive:
        attacker.mr_count = 2
        attacker.mr_target = defender
        battle.add_text(attacker.nickname + " took aim at " + defender.nickname + "!")
    else:
        _failed(battle)


def _ef_074(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if (
        defender.is_alive
        and defender.nv_status == gs.ASLEEP
        and not defender.substitute
    ):
        defender.v_status[gs.NIGHTMARE] = 1
        battle.add_text(defender.nickname + " began having a nightmare!")
    else:
        _failed(battle)


def _ef_075(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    dmg = _calculate_damage(attacker, defender, battlefield, battle, move_data)
    if dmg and randrange(100) < move_data.ef_amount:
        burn(defender, battle)
    return True


def _ef_076(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if defender.is_alive and attacker.nv_status == gs.ASLEEP:
        dmg = _calculate_damage(attacker, defender, battlefield, battle, move_data)
        if dmg and randrange(10) < 3:
            _flinch(defender, battle, is_first)
    else:
        _failed(battle)
    return True


def _ef_077(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if "ghost" not in attacker.types:
        if (
            attacker.stat_stages[gs.ATK] == 6
            and attacker.stat_stages[gs.DEF] == 6
            and attacker.stat_stages[gs.SPD] == -6
        ):
            _failed(battle)
            return True
        if attacker.stat_stages[gs.ATK] < 6:
            give_stat_change(attacker, battle, gs.ATK, 1)
        if attacker.stat_stages[gs.DEF] < 6:
            give_stat_change(attacker, battle, gs.DEF, 1)
        if attacker.stat_stages[gs.SPD] > -6:
            give_stat_change(attacker, battle, gs.SPD, -1, bypass=True)
    else:
        if not defender.is_alive or defender.v_status[gs.CURSE] or defender.substitute:
            _failed(battle)
            return True
        attacker.take_damage(attacker.max_hp // 2)
        defender.v_status[gs.CURSE] = 1
        battle.add_text(
            attacker.nickname
            + " cut its own HP and laid a curse on "
            + defender.nickname
            + "!"
        )


def _ef_078(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
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


def _ef_079(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if not attacker.last_move_hit_by or not PokeSim.is_valid_type(
        attacker.last_move_hit_by.type
    ):
        _failed(battle)
        return True
    last_move_type = attacker.last_move_hit_by.type
    types = PokeSim.get_all_types()
    poss_types = []
    for type in types:
        if type and PokeSim.get_type_ef(last_move_type, type) < 1:
            poss_types.append(type)
    poss_types = [type for type in poss_types if type not in attacker.types]
    poss_types = PokeSim.filter_valid_types(poss_types)
    if len(poss_types):
        new_type = poss_types[randrange(len(poss_types))]
        attacker.types = (new_type, None)
        battle.add_text(
            attacker.nickname + " transformed into the " + new_type.upper() + " type!"
        )
    else:
        _failed(battle)


def _ef_080(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if defender.is_alive and defender.last_move and defender.last_move.cur_pp:
        if defender.last_move.cur_pp < 4:
            amt_reduced = defender.last_move.cur_pp
        else:
            amt_reduced = 4
        defender.last_move.cur_pp -= amt_reduced
        battle.add_text(
            "It reduced the pp of "
            + defender.nickname
            + "'s "
            + cap_name(defender.last_move.name)
            + " by "
            + str(amt_reduced)
            + "!"
        )
    else:
        _failed(battle)


def _ef_081(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if attacker.substitute:
        _failed(battle)
    p_chance = min(8, 2**attacker.protect_count)
    if randrange(p_chance) < 1:
        attacker.invulnerable = True
        attacker.protect = True
        attacker.protect_count += 1
    else:
        _failed(battle)


def _ef_082(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if attacker.max_hp // 2 > attacker.cur_hp or attacker.stat_stages[gs.ATK] == 6:
        _failed(battle)
        return True
    battle.add_text(attacker.nickname + " cut its own HP and maximized its Attack!")
    attacker.stat_stages[gs.ATK] = 6


def _ef_083(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    enemy = defender.trainer
    if enemy.spikes < 3:
        enemy.spikes += 1
        battle.add_text(
            "Spikes were scattered all around the feet of " + enemy.name + "'s team!"
        )
    else:
        _failed(battle)


def _ef_084(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if defender.is_alive and not defender.foresight_target:
        defender.foresight_target = True
        battle.add_text(attacker.nickname + " identified " + defender.nickname + "!")
    else:
        _failed(battle)


def _ef_085(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    battle.add_text(attacker.nickname + " is trying to take its foe with it!")
    attacker.db_count = 1 if is_first else 2


def _ef_086(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if not attacker.perish_count:
        attacker.perish_count = 4
    if defender.is_alive and not defender.perish_count:
        defender.perish_count = 4
    battle.add_text("All pokemon hearing the song will faint in three turns!")


def _ef_087(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if battlefield.weather != gs.SANDSTORM:
        battlefield.change_weather(gs.SANDSTORM)
        battlefield.weather_count = 5 if attacker.item != "smooth-rock" else 8
        battle.add_text("A sandstorm brewed")
    else:
        _failed(battle)


def _ef_088(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if attacker.substitute:
        _failed(battle)
    p_chance = min(8, 2**attacker.protect_count)
    if randrange(p_chance) < 1:
        attacker.endure = True
        attacker.protect_count += 1
    else:
        _failed(battle)


def _ef_089(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if not move_data.ef_stat:
        if attacker.df_curl and move_data.power == move_data.o_power:
            move_data.power *= 2
        move_data.ef_stat = 1
    else:
        move_data.ef_stat += 1
    _calculate_damage(
        attacker, defender, battlefield, battle, move_data, cc_ib[0], cc_ib[1]
    )
    move_data.power *= 2
    if move_data.ef_stat < 5:
        attacker.next_moves.put(move_data)
    return True


def _ef_090(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    dmg = _calculate_damage(
        attacker, defender, battlefield, battle, move_data, skip_dmg=True
    )
    if not dmg:
        return True
    if not defender.substitute and dmg >= defender.cur_hp:
        dmg = defender.cur_hp - 1
    defender.take_damage(dmg, move_data)
    return True


def _ef_091(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if defender.is_alive:
        give_stat_change(defender, battle, gs.ATK, 2)
        confuse(defender, battle, forced=True)
    else:
        _failed(battle)


def _ef_092(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if (
        attacker.last_move
        and attacker.last_move is attacker.last_successful_move
        and attacker.last_move.name == move_data.name
    ):
        move_data.ef_stat = min(5, int(attacker.last_move.ef_stat) + 1)
        move_data.power = move_data.o_power * (2 ** (move_data.ef_stat - 1))
    else:
        move_data.ef_stat = 1


def _ef_093(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    infatuate(attacker, defender, battle, forced=True)


def _ef_094(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if attacker.nv_status != gs.ASLEEP:
        _failed(battle)
        return True
    pos_moves = [move for move in attacker.moves if move.name != "sleep-talk"]
    sel_move = Move(pos_moves[randrange(len(pos_moves))].md)
    battle.add_text(attacker.nickname + " used " + cap_name(sel_move.name) + "!")
    _process_effect(attacker, defender, battlefield, battle, sel_move, is_first)
    return True


def _ef_095(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if move_data.ef_stat == 1:
        battle.add_text("A bell chimed!")
    elif move_data.ef_stat == 2:
        battle.add_text("A soothing aroma wafted through the area!")
    t = attacker.trainer
    for poke in t.poke_list:
        poke.nv_status = 0


def _ef_096(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    move_data.power = max(1, int(attacker.friendship / 2.5))


def _ef_097(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    res = randrange(10)
    if res < 2:
        if not defender.is_alive:
            _missed(attacker, battle)
            return True
        if defender.cur_hp == defender.max_hp:
            battle.add_text(defender.nickname + " can't receive the gift!")
            return True
        defender.heal(defender.max_hp // 4)
        return True
    elif res < 6:
        move_data.power = 40
    elif res < 9:
        move_data.power = 80
    elif res < 10:
        move_data.power = 120


def _ef_098(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    move_data.power = max(1, int((255 - attacker.friendship) / 2.5))


def _ef_099(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    t = attacker.trainer
    if not t.safeguard:
        t.safeguard = 5
        battle.add_text(t.name + "'s team became cloaked in a mystical veil!")
    else:
        _failed(battle)


def _ef_100(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if defender.is_alive:
        new_hp = (attacker.cur_hp + defender.cur_hp) // 2
        battle.add_text("The battlers shared their pain!")
        attacker.cur_hp = min(new_hp, attacker.max_hp)
        defender.cur_hp = min(new_hp, defender.max_hp)
    else:
        _failed(battle)
    return True


def _ef_101(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    res = randrange(20)
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
        cc_ib[1] = True
        move_data.power *= 2
    battle.add_text("Magnitude " + str(mag) + "!")


def _ef_102(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    t = attacker.trainer
    old_poke = attacker
    if t.num_fainted >= len(t.poke_list) - 1 or battle._process_selection(t):
        _failed(battle)
    t.current_poke.v_status = attacker.v_status.copy()
    t.current_poke.stat_stages = attacker.stat_stages.copy()
    t.current_poke.perish_count = attacker.perish_count
    t.current_poke.trapped = attacker.trapped
    t.current_poke.perma_trapped = attacker.perma_trapped
    t.current_poke.embargo_count = attacker.embargo_count
    t.current_poke.magnetic_rise = attacker.magnet_rise
    t.current_poke.substitute = attacker.substitute
    t.current_poke.hb_count = attacker.hb_count
    t.current_poke.power_trick = attacker.power_trick
    if not attacker.has_ability("multitype"):
        t.current_poke.ability_supressed = attacker.ability_suppressed


def _ef_103(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if (
        defender.is_alive
        and not defender.encore_count
        and defender.last_move
        and defender.last_move.cur_pp
        and defender.last_move not in gd.ENCORE_CHECK
        and any([move.name == defender.last_move.name for move in defender.moves])
    ):
        defender.next_moves.clear()
        defender.encore_count = min(randrange(2, 7), defender.last_move.pp)
        for move in defender.moves:
            if move.name != defender.last_move.name:
                move.encore_blocked = True
            else:
                defender.encore_move = move
        battle.add_text(defender.nickname + " received an encore!")
    else:
        _failed(battle)


def _ef_104(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    _calculate_damage(attacker, defender, battlefield, battle, move_data)
    if attacker.is_alive:
        attacker.v_status[gs.BINDING_COUNT] = 0
        attacker.binding_type = None
        attacker.binding_poke = None
        attacker.v_status[gs.LEECH_SEED] = 0
        t = attacker.trainer
        t.spikes = 0
        t.toxic_spikes = 0
        t.steal_rock = 0
    return True


def _ef_105(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if battlefield.weather == gs.CLEAR:
        heal_amount = 2
    elif battlefield.weather == gs.HARSH_SUNLIGHT:
        heal_amount = 1.5
    else:
        heal_amount = 4
    attacker.heal(int(attacker.max_hp / heal_amount))


def _ef_106(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    hp_stats = attacker.hidden_power_stats()
    if hp_stats:
        move_data.type, move_data.power = hp_stats
    else:
        move_data.power = randrange(30, 71)
        move_data.type = attacker.types[0]


def _ef_107(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if defender.in_air:
        cc_ib[1] = True
        move_data.power *= 2
    dmg = _calculate_damage(
        attacker, defender, battlefield, battle, move_data, cc_ib[0], cc_ib[1]
    )
    if dmg and randrange(5) < 1:
        _flinch(defender, battle, is_first)
    return True


def _ef_108(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if battlefield.weather != gs.RAIN:
        battlefield.change_weather(gs.RAIN)
        battlefield.weather_count = 5 if attacker.item != "damp-rock" else 8
        battle.add_text("It started to rain!")
    else:
        _failed(battle)


def _ef_109(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if battlefield.weather != gs.HARSH_SUNLIGHT:
        battlefield.change_weather(gs.HARSH_SUNLIGHT)
        battlefield.weather_count = 5 if attacker.item != "heat-rock" else 8
        battle.add_text("The sunlight turned harsh!")
    else:
        _failed(battle)


def _ef_110(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if (
        defender.is_alive
        and attacker.last_move_hit_by
        and defender.last_move
        and attacker.last_move_hit_by.name == defender.last_move.name
        and attacker.last_move_hit_by.category == gs.SPECIAL
        and _calculate_type_ef(defender, move_data)
    ):
        defender.take_damage(attacker.last_damage_taken * 2, move_data)
    else:
        _failed(battle)
    return True


def _ef_111(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if defender.is_alive:
        attacker.stat_stages = [stat for stat in defender.stat_stages]
        attacker.accuracy_stage = defender.accuracy_stage
        attacker.evasion_stage = defender.evasion_stage
        attacker.crit_stage = defender.crit_stage
        battle.add_text(
            attacker.nickname + " copied " + defender.nickname + "'s stat changes!"
        )
    else:
        _failed(battle)


def _ef_112(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    dmg = _calculate_damage(attacker, defender, battlefield, battle, move_data)
    if dmg and randrange(1, 101) < move_data.ef_chance:
        give_stat_change(attacker, battle, gs.ATK, 1)
        give_stat_change(attacker, battle, gs.DEF, 1)
        give_stat_change(attacker, battle, gs.SP_ATK, 1)
        give_stat_change(attacker, battle, gs.SP_DEF, 1)
        give_stat_change(attacker, battle, gs.SPD, 1)
    return True


def _ef_113(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    t = defender.trainer
    if defender.is_alive and not t.fs_count:
        move_data.type = "typeless"
        t.fs_dmg = _calculate_damage(
            attacker,
            defender,
            battlefield,
            battle,
            move_data,
            crit_chance=-4,
            skip_dmg=True,
        )
        t.fs_count = 3
        battle.add_text(attacker.nickname + " foresaw an attack!")
    else:
        _failed(battle)
    return True


def _ef_114(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if not defender.is_alive:
        _failed(battle)
        return True
    poke_hits = [poke for poke in attacker.trainer.poke_list if not poke.nv_status]
    num_hits = 0
    move_data.power = 10
    while defender.is_alive and num_hits < len(poke_hits):
        _calculate_damage(attacker, defender, battlefield, battle, move_data)
        battle.add_text(poke_hits[num_hits].nickname + "'s attack!")
        num_hits += 1
    return True


def _ef_115(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    dmg = _calculate_damage(attacker, defender, battlefield, battle, move_data)
    if dmg and not attacker.uproar:
        attacker.uproar = randrange(1, 5)
        battle.add_text(attacker.nickname + " caused an uproar!")
    return True


def _ef_116(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if attacker.stockpile < 3:
        attacker.stockpile += 1
        battle.add_text(
            attacker.nickname + " stockpiled " + str(attacker.stockpile) + "!"
        )
        give_stat_change(attacker, battle, gs.DEF, 1)
        give_stat_change(attacker, battle, gs.SP_DEF, 1)
    else:
        _failed(battle)


def _ef_117(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if attacker.stockpile:
        _calculate_damage(attacker, defender, battlefield, battle, move_data)
        move_data.power = 100 * attacker.stockpile
        attacker.stockpile = 0
        attacker.stat_stages[gs.DEF] -= attacker.stockpile
        attacker.stat_stages[gs.SP_DEF] -= attacker.stockpile
        battle.add_text(attacker.nickname + "'s stockpile effect wore off!")
    else:
        _failed(battle)


def _ef_118(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if attacker.stockpile:
        attacker.heal(attacker.max_hp * (2 ** (attacker.stockpile - 1)) // 4)
        attacker.stockpile = 0
        attacker.stat_stages[gs.DEF] -= attacker.stockpile
        attacker.stat_stages[gs.SP_DEF] -= attacker.stockpile
        battle.add_text(attacker.nickname + "'s stockpile effect wore off!")
    else:
        _failed(battle)


def _ef_119(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if battlefield.weather != gs.HAIL:
        battlefield.change_weather(gs.HAIL)
        battlefield.weather_count = 5 if attacker.item != "icy-rock" else 8
        battle.add_text("It started to hail!")
    else:
        _failed(battle)


def _ef_120(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if defender.is_alive and not defender.tormented:
        defender.tormented = True
        battle.add_text(defender.nickname + " was subjected to Torment!")
    else:
        _failed(battle)


def _ef_121(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if (
        defender.is_alive
        and not defender.substitute
        and (not defender.v_status[gs.CONFUSED] or defender.stat_stages[gs.SP_ATK] < 6)
    ):
        give_stat_change(defender, battle, gs.SP_ATK, 1)
        confuse(defender, battle)
    else:
        _failed(battle)


def _ef_122(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if defender.is_alive and not defender.substitute:
        attacker.faint()
        give_stat_change(defender, battle, gs.ATK, -2)
        give_stat_change(defender, battle, gs.SP_ATK, -2)
    return True


def _ef_123(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if (
        attacker.nv_status == gs.BURNED
        or attacker.nv_status == gs.PARALYZED
        or attacker.nv_status == gs.POISONED
    ):
        move_data.power *= 2


def _ef_124(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if not defender.is_alive:
        _failed(battle)
        return True
    if attacker.turn_damage:
        battle._pop_text()
        battle.add_text(attacker.nickname + " lost its focus and couldn't move!")
        return True


def _ef_125(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if not defender.is_alive:
        _failed(battle)
        return True
    if defender.nv_status == gs.PARALYZED:
        move_data.power *= 2
    dmg = _calculate_damage(attacker, defender, battlefield, battle, move_data)
    if defender.is_alive and dmg and defender.nv_status == gs.PARALYZED:
        cure_nv_status(gs.PARALYZED, defender, battle)
    return True


def _ef_126(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    move_data = Move(PokeSim.get_move_data(["swift"])[0])


def _ef_127(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    attacker.charged = 2
    battle.add_text(attacker.nickname + " began charging power!")
    give_stat_change(attacker, battle, gs.SP_DEF, 1)


def _ef_128(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if (
        defender.is_alive
        and not defender.taunt
        and not defender.has_ability("oblivious")
    ):
        defender.taunt = randrange(3, 6)
        battle.add_text(defender.nickname + " fell for the taunt!")
    else:
        _failed(battle)


def _ef_129(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    _failed(battle)


def _ef_130(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if (
        defender.is_alive
        and not defender.substitute
        and (attacker.item or defender.item)
        and attacker.item != "griseous-orb"
        and defender.item != "griseous-orb"
        and not defender.has_ability("sticky-hold")
        and not defender.has_ability("multitype")
        and not attacker.has_ability("multitype")
    ):
        a_item = attacker.item
        attacker.give_item(defender.item)
        defender.give_item(a_item)
        battle.add_text(attacker.nickname + " switched items with its target!")
        if attacker.item:
            battle.add_text(
                attacker.nickname + " obtained one " + cap_name(attacker.item) + "."
            )
        if defender.item:
            battle.add_text(
                defender.nickname + " obtained one " + cap_name(defender.item) + "."
            )
    else:
        _failed(battle)


def _ef_131(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if (
        defender.is_alive
        and defender.ability
        and not defender.has_ability("wonder-guard")
        and not defender.has_ability("multitype")
    ):
        attacker.give_ability(defender.ability)
        battle.add_text(
            attacker.nickname
            + " copied "
            + defender.nickname
            + "'s "
            + defender.ability
            + "!"
        )
    else:
        _failed(battle)


def _ef_132(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    t = attacker.trainer
    if not t.wish:
        t.wish = 2
        t.wish_poke = attacker.nickname
    else:
        _failed(battle)


def _ef_133(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    possible_moves = [
        move
        for poke in attacker.trainer.poke_list
        for move in poke.moves
        if move.name not in gd.ASSIST_CHECK
    ]
    if len(possible_moves):
        _process_effect(
            attacker,
            defender,
            battlefield,
            battle,
            Move(possible_moves[randrange(len(possible_moves))].md),
            is_first,
        )
    else:
        _failed(battle)
    return True


def _ef_134(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if not attacker.v_status[gs.INGRAIN]:
        battle.add_text(attacker.nickname + " planted its roots!")
        attacker.v_status[gs.INGRAIN] = 1
        attacker.trapped = True
        attacker.grounded = True
    else:
        _failed(battle)


def _ef_135(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    dmg = _calculate_damage(attacker, defender, battlefield, battle, move_data)
    if dmg:
        give_stat_change(attacker, battle, gs.ATK, -1, bypass=True)
        give_stat_change(attacker, battle, gs.DEF, -1, bypass=True)
    return True


def _ef_136(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if is_first:
        attacker.magic_coat = True
        battle.add_text(attacker.nickname + " shrouded itself with Magic Coat!")
    else:
        _failed(battle)


def _ef_137(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if not attacker.item and not attacker.h_item and attacker.last_consumed_item:
        attacker.give_item(attacker.last_consumed_item)
        attacker.last_consumed_item = None
        battle.add_text(
            attacker.nickname + " found one " + cap_name(attacker.item) + "!"
        )
    else:
        _failed(battle)


def _ef_138(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if attacker.turn_damage:
        move_data.power *= 2


def _ef_139(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if defender.is_alive and not defender.invulnerable and not defender.protect:
        t = defender.trainer
        if t.light_screen or t.reflect:
            t.light_screen = 0
            t.reflect = 0
            battle.add_text("It shattered the barrier!")
        _calculate_damage(attacker, defender, battlefield, battle, move_data)
    else:
        _failed(battle)
    return True


def _ef_140(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if (
        defender.is_alive
        and not defender.v_status[gs.DROWSY]
        and not defender.substitute
        and not defender.nv_status == gs.FROZEN
        and not defender.nv_status == gs.ASLEEP
        and not defender.has_ability("insomnia")
        and not defender.has_ability("vital-spirit")
        and not defender.trainer.safeguard
        and not (
            defender.has_ability("leaf-guard")
            and battlefield.weather == gs.HARSH_SUNLIGHT
        )
        and not (defender.uproar and not defender.has_ability("soundproof"))
    ):
        defender.v_status[gs.DROWSY] = 2
        battle.add_text(attacker.nickname + " made " + defender.nickname + " drowsy!")
    else:
        _failed(battle)


def _ef_141(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    dmg = _calculate_damage(attacker, defender, battlefield, battle, move_data)
    if defender.is_alive and dmg and defender.item and defender.h_item:
        battle.add_text(
            attacker.nickname
            + " knocked off "
            + defender.nickname
            + "'s "
            + cap_name(defender.item)
            + "!"
        )
        defender.item = None
    return True


def _ef_142(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if (
        defender.is_alive
        and attacker.cur_hp < defender.cur_hp
        and _calculate_type_ef(defender, move_data)
    ):
        defender.take_damage(defender.cur_hp - attacker.cur_hp)
    else:
        _failed(battle)
    return True


def _ef_143(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    move_data.power = max(1, (150 * attacker.cur_hp) // attacker.max_hp)


def _ef_144(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if (
        defender.is_alive
        and not defender.has_ability("wonder-guard")
        and not defender.has_ability("multitype")
        and not attacker.has_ability("wonder-guard")
        and not attacker.has_ability("multitype")
    ):
        a_ability = attacker.ability
        attacker.give_ability(defender.ability)
        defender.give_ability(a_ability)
        battle.add_text(attacker.nickname + " swapped abilities with its target!")
    else:
        _failed(battle)


def _ef_145(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    a_moves = [move.name for move in attacker.moves]
    t = defender.trainer
    if not t.imprisoned_poke and any(
        [move.name in a_moves for poke in t.poke_list for move in poke.moves]
    ):
        battle.add_text(attacker.nickname + " sealed the opponent's move(s)!")
        t.imprisoned_poke = attacker
    else:
        _failed(battle)


def _ef_146(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if (
        attacker.nv_status == gs.BURNED
        or attacker.nv_status == gs.PARALYZED
        or attacker.nv_status == gs.POISONED
    ):
        attacker.nv_status = 0
        battle.add_text(attacker.nickname + "'s status return Trueed to normal!")
    else:
        _failed(battle)


def _ef_147(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    battle.add_text(
        attacker.nickname + " wants " + attacker.enemy.name + " to bear a grudge!"
    )


def _ef_148(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if is_first:
        attacker.snatch = True
        battle.add_text(attacker.nickname + " waits for a target to make a move!")
    else:
        _failed(battle)


def _ef_149(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    dmg = _calculate_damage(attacker, defender, battlefield, battle, move_data)
    if dmg and randrange(1, 101) < move_data.ef_chance:
        paralyze(defender, battle)
    return True


def _ef_150(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if not move_data.ef_stat and not _power_herb_check(attacker, battle):
        move_data.ef_stat = 1
        attacker.next_moves.put(move_data)
        attacker.in_water = True
        attacker.invulnerable = True
        attacker.inv_count = 1
        battle._pop_text()
        battle.add_text(attacker.nickname + " hid underwater!")
        return True


def _ef_151(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    attacker.type = ("normal", None)
    battle.add_text(
        attacker.nickname
        + " transformed into the "
        + attacker.types[0].upper()
        + " type!"
    )


def _ef_152(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    dmg = _calculate_damage(
        attacker, defender, battlefield, battle, move_data, crit_chance=1
    )
    if dmg and randrange(10) < 1:
        burn(defender, battle)
    return True


def _ef_153(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if not attacker.mud_sport and not (defender.is_alive and defender.mud_sport):
        attacker.mud_sport = True
        battle.add_text("Electricity's power was weakened")
    else:
        _failed(battle)


def _ef_154(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if battlefield.weather == gs.HARSH_SUNLIGHT:
        move_data.type = "fire"
    elif battlefield.weather == gs.RAIN:
        move_data.type = "water"
    elif battlefield.weather == gs.HAIL:
        move_data.type = "ice"
    elif battlefield.weather == gs.SANDSTORM:
        move_data.type == "rock"
    else:
        move_data.type = "normal"
    if battlefield.weather != gs.CLEAR:
        move_data.power *= 2


def _ef_156(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    sleep(defender, battle, forced=True)


def _ef_157(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if defender.is_alive and (
        defender.stat_stages[gs.ATK] > -6 or defender.stat_stages[gs.DEF] > -6
    ):
        give_stat_change(defender, battle, gs.ATK, -1)
        give_stat_change(defender, battle, gs.DEF, -1)
    else:
        _failed(battle)


def _ef_158(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if attacker.stat_stages[gs.DEF] < 6 or attacker.stat_stages[gs.SP_DEF] < 6:
        give_stat_change(attacker, battle, gs.DEF, 1)
        give_stat_change(attacker, battle, gs.SP_DEF, 1)
    else:
        _failed(battle)


def _ef_159(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if defender.is_alive and defender.in_air:
        cc_ib[1] = True


def _ef_160(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if attacker.stat_stages[gs.ATK] < 6 or attacker.stat_stages[gs.DEF] < 6:
        give_stat_change(attacker, battle, gs.ATK, 1)
        give_stat_change(attacker, battle, gs.DEF, 1)
    else:
        _failed(battle)


def _ef_161(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if not move_data.ef_stat and not _power_herb_check(attacker, battle):
        move_data.ef_stat = 1
        attacker.next_moves.put(move_data)
        attacker.in_air = True
        attacker.invulnerable = True
        attacker.inv_count = 1
        battle._pop_text()
        battle.add_text(attacker.nickname + " sprang up!")
        return True
    dmg = _calculate_damage(attacker, defender, battlefield, battle, move_data)
    if dmg and randrange(10) < 3:
        paralyze(defender, battle)
    return True


def _ef_162(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    dmg = _calculate_damage(
        attacker, defender, battlefield, battle, move_data, crit_chance=1
    )
    if dmg and randrange(10) < 1:
        poison(defender, battle)
    return True


def _ef_163(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    dmg = _calculate_damage(attacker, defender, battlefield, battle, move_data)
    if dmg and randrange(10) < 1:
        paralyze(defender, battle)
    if dmg:
        _recoil(attacker, battle, max(1, dmg // 3), move_data)
    return True


def _ef_164(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if not attacker.water_sport and not (defender.is_alive and defender.water_sport):
        attacker.water_sport = True
        battle.add_text("Fire's power was weakened")
    else:
        _failed(battle)


def _ef_165(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if attacker.stat_stages[gs.SP_ATK] < 6 or attacker.stat_stages[gs.SP_DEF] < 6:
        give_stat_change(attacker, battle, gs.SP_ATK, 1)
        give_stat_change(attacker, battle, gs.SP_DEF, 1)
    else:
        _failed(battle)


def _ef_166(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if attacker.stat_stages[gs.ATK] < 6 or attacker.stat_stages[gs.SPD] < 6:
        give_stat_change(attacker, battle, gs.ATK, 1)
        give_stat_change(attacker, battle, gs.SPD, 1)
    else:
        _failed(battle)


def _ef_167(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    t = defender.trainer
    if defender.is_alive and not t.dd_count:
        move_data.type = "typeless"
        t.dd_dmg = _calculate_damage(
            attacker,
            defender,
            battlefield,
            battle,
            move_data,
            crit_chance=0,
            skip_dmg=True,
        )
        t.dd_count = 3
        battle.add_text(attacker.nickname + " chose Doom Desire as its destiny!")
    else:
        _failed(battle)
    return True


def _ef_168(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    attacker.heal(max(1, attacker.max_hp // 2))
    if not is_first or not "flying" in attacker.types:
        return True
    attacker.r_types = attacker.types
    other_type = [type for type in attacker.types if type != "flying"]
    if len(other_type) > 0:
        attacker.types = (other_type[0], None)
    else:
        attacker.types = ("normal", None)


def _ef_169(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if not battlefield.gravity_count:
        battlefield.gravity_count = 5
        battlefield.acc_modifier = 5 / 3
        attacker.grounded = True
        defender.grounded = True
        battle.add_text("Gravity intensified!")
    else:
        _failed(battle)


def _ef_170(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if defender.is_alive and not defender.me_target:
        defender.me_target = True
        battle.add_text(attacker.nickname + " identified " + defender.nickname + "!")
    else:
        _failed(battle)


def _ef_171(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if defender.nv_status == gs.ASLEEP:
        move_data.power *= 2
    dmg = _calculate_damage(attacker, defender, battlefield, battle, move_data)
    if defender.is_alive and dmg:
        cure_nv_status(gs.ASLEEP, defender, battle)
    return True


def _ef_172(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    attacker.calculate_stats_effective()
    defender.calculate_stats_effective()
    move_data.power = min(
        150,
        attacker.stats_effective[gs.SPD] * 25 / max(1, defender.stats_effective[gs.SPD])
        + 1,
    )


def _ef_173(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    t = attacker.trainer
    if t.num_fainted >= len(t.poke_list) - 1 or battle._process_selection(t):
        _failed(battle)
    battle.add_text("The healing wish came true!")
    t.current_poke.heal(t.current_poke.max_hp)
    t.current_poke.nv_status = 0


def _ef_174(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if attacker.cur_hp < attacker.max_hp // 2:
        move_data.power *= 2


def _ef_175(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if (
        attacker.item
        and attacker.item in gd.BERRY_DATA
        and not battlefield.weather in [gs.HARSH_SUNLIGHT, gs.RAIN]
        and not attacker.has_ability("klutz")
        and not attacker.embargo_count
    ):
        move_data.type, move_data.power = gd.BERRY_DATA[attacker.item]
        attacker.give_item(None)
    else:
        _failed(battle)
        return True


def _ef_176(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if not is_first and defender.is_alive and defender.protect:
        battle.add_text(defender.nickname + " fell for the feint!")
        _calculate_damage(attacker, defender, battlefield, battle, move_data)
    else:
        _failed(battle)
    return True


def _ef_177(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    dmg = _calculate_damage(attacker, defender, battlefield, battle, move_data)
    if (
        defender.is_alive
        and dmg
        and defender.item
        and defender.item in gd.BERRY_DATA
        and not defender.has_ability("sticky-hold")
        and not defender.substitute
    ):
        battle.add_text(
            attacker.nickname
            + " stole and ate "
            + defender.nickname
            + "'s "
            + defender.item
            + "!"
        )
        if not attacker.has_ability("klutz") and not attacker.embargo_count:
            pi.use_item(
                attacker.trainer,
                battle,
                defender.item,
                attacker,
                randrange(len(attacker.moves)),
                text_skip=True,
                can_skip=True
            )
        defender.give_item(None)
    return True


def _ef_178(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if not attacker.trainer.tailwind_count:
        battle.add_text(
            "The tailwind blew from being " + attacker.trainer.name + "'s team!"
        )
        attacker.trainer.tailwind_count = 3
        for poke in attacker.trainer.poke_list:
            poke.stats_actual[gs.SPD] *= 2
    else:
        _failed(battle)


def _ef_179(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    ef_stats = attacker.stat_stages + [attacker.accuracy_stage, attacker.evasion_stage]
    ef_stats = [stat_i for stat_i in range(len(ef_stats)) if ef_stats[stat_i] < 6]
    if len(ef_stats):
        give_stat_change(attacker, battle, randrange(len(ef_stats)), 2)
    else:
        _failed(battle)


def _ef_180(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if not is_first and attacker.turn_damage and defender.is_alive:
        defender.take_damage(int(attacker.last_damage_taken * 1.5))
    else:
        _failed(battle)
    return True


def _ef_181(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    _calculate_damage(attacker, defender, battlefield, battle, move_data)
    t = attacker.trainer
    if t.num_fainted < len(t.poke_list) - 1:
        battle._process_selection(t)
    return True


def _ef_182(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    dmg = _calculate_damage(attacker, defender, battlefield, battle, move_data)
    if attacker.is_alive and dmg:
        give_stat_change(attacker, battle, gs.DEF, -1, bypass=True)
        give_stat_change(attacker, battle, gs.SP_DEF, -1, bypass=True)
    return True


def _ef_183(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if not is_first:
        move_data.power *= 2


def _ef_184(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if not is_first and defender.turn_damage:
        move_data.power *= 2


def _ef_185(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if defender.is_alive and not defender.embargo_count:
        defender.embargo_count = 5
        battle.add_text(defender.nickname + " can't use items anymore!")
    else:
        _failed(battle)


def _ef_186(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if attacker.item:
        battle.add_text(attacker.nickname + " flung its " + attacker.item + "!")
        move_data.power = 20
        _calculate_damage(attacker, defender, battlefield, battle, move_data)
        if attacker.is_alive:
            attacker.give_item(None)
    else:
        _failed(battle)


def _ef_187(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if attacker.nv_status:
        give_nv_status(attacker.nv_status, defender, battle)
        attacker.nv_status = 0
    else:
        _failed(battle)


def _ef_188(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if move_data.cur_pp >= 4:
        move_data.power = 40
    elif move_data.cur_pp == 3:
        move_data.power = 50
    elif move_data.cur_pp == 2:
        move_data.power = 60
    elif move_data.cur_pp == 1:
        move_data.power = 80
    else:
        move_data.power = 200


def _ef_189(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if defender.is_alive and not defender.hb_count:
        defender.hb_count = 5
        battle.add_text(defender.nickname + " was prevented from healing!")
    else:
        _failed(battle)


def _ef_190(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    move_data.power = int(1 + 120 * attacker.cur_hp / attacker.max_hp)


def _ef_191(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    attacker.stats_actual[gs.ATK], attacker.stats_actual[gs.DEF] = (
        attacker.stats_actual[gs.DEF],
        attacker.stats_actual[gs.ATK],
    )
    battle.add_text(attacker.nickname + " switched its Attack and Defense!")
    attacker.power_trick = True


def _ef_192(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if (
        defender.is_alive
        and not defender.has_ability("multitype")
        and not defender.ability_suppressed
    ):
        defender.ability_suppressed = True
        battle.add_text(defender.nickname + "'s ability was suppressed!")
    else:
        _failed(battle)


def _ef_193(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if not attacker.trainer.lucky_chant:
        attacker.trainer.lucky_chant = 5
        battle.add_text(
            "The Lucky Chant shielded"
            + attacker.trainer.name
            + "'s team from critical hits!"
        )
    else:
        _failed(battle)


def _ef_194(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if attacker.mf_move:
        if attacker.mf_move.power:
            attacker.mf_move.power = int(1.5 * attacker.mf_move.power)
        battle.add_text(
            attacker.nickname + " used " + cap_name(attacker.mf_move.name) + "!"
        )
        _process_effect(
            attacker, defender, battlefield, battle, attacker.mf_move, is_first
        )
        attacker.mf_move = None
    else:
        _failed(battle)
    return True


def _ef_195(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if battle.last_move and battle.last_move.name != move_data.name:
        _process_effect(
            attacker, defender, battlefield, battle, Move(battle.last_move.md), is_first
        )
        return True
    else:
        _failed(battle)


def _ef_196(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if defender.is_alive:
        attacker.stat_stages[gs.ATK], defender.stat_stages[gs.ATK] = (
            defender.stat_stages[gs.ATK],
            attacker.stat_stages[gs.ATK],
        )
        attacker.stat_stages[gs.SP_ATK], defender.stat_stages[gs.SP_ATK] = (
            defender.stat_stages[gs.SP_ATK],
            attacker.stat_stages[gs.SP_ATK],
        )
        battle.add_text(
            attacker.nickname
            + " switched all changes to its Attack and Sp. Atk with "
            + defender.nickname
            + "!"
        )
    else:
        _failed(battle)


def _ef_197(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if defender.is_alive:
        attacker.stat_stages[gs.DEF], defender.stat_stages[gs.DEF] = (
            defender.stat_stages[gs.DEF],
            attacker.stat_stages[gs.DEF],
        )
        attacker.stat_stages[gs.SP_DEF], defender.stat_stages[gs.SP_DEF] = (
            defender.stat_stages[gs.SP_DEF],
            attacker.stat_stages[gs.SP_DEF],
        )
        battle.add_text(
            attacker.nickname
            + " switched all changes to its Defense and Sp. Def with "
            + defender.nickname
            + "!"
        )
    else:
        _failed(battle)


def _ef_198(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    move_data.power = max(
        200, 60 + 20 * sum([stat for stat in attacker.stat_stages if stat > 0])
    )


def _ef_199(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if len(attacker.moves) < 2 or not all(
        [
            attacker.moves[i].cur_pp < attacker.old_pp[i]
            or attacker.moves[i] == "last-resort"
            for i in range(len(attacker.moves))
        ]
    ):
        _failed(battle)
        return True


def _ef_200(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if (
        defender.is_alive
        and not defender.has_ability("multitype")
        and not defender.has_ability("truant")
    ):
        battle.add_text(defender.nickname + " acquired insomnia!")
        defender.give_ability("insomnia")
    else:
        _failed(battle)


def _ef_201(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if not is_first or not attacker.sp_check:
        _failed(battle)
        return True


def _ef_202(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    defender.trainer.toxic_spikes += 1
    battle.add_text(
        "Poison spikes were scattered all around the feet of "
        + defender.trainer.name
        + "'s team!"
    )


def _ef_203(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if defender.is_alive:
        attacker.stat_stages, defender.stat_stages = (
            defender.stat_stages,
            attacker.stat_stages,
        )
        battle.add_text(
            attacker.nickname + " switched stat changes with " + defender.nickname + "!"
        )
    else:
        _failed(battle)


def _ef_204(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if not attacker.v_status[gs.AQUA_RING]:
        battle.add_text(attacker.nickname + " surrounded itself with a veil of water!")
        attacker.v_status[gs.AQUA_RING] = 1
    else:
        _failed(battle)


def _ef_205(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if not attacker.magnet_rise:
        attacker.magnet_rise = True
        battle.add_text(attacker.nickname + " levitated on electromagnetism!")
    else:
        _failed(battle)


def _ef_206(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    dmg = _calculate_damage(attacker, defender, battlefield, battle, move_data)
    if dmg:
        _recoil(attacker, battle, max(1, dmg // 3), move_data)
    if defender.is_alive and dmg and randrange(10) < 1:
        burn(defender, battle)
    return True


def _ef_207(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    dmg = _calculate_damage(attacker, defender, battlefield, battle, move_data)
    if dmg:
        _recoil(attacker, battle, max(1, dmg // 3), move_data)


def _ef_208(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    dmg = _calculate_damage(attacker, defender, battlefield, battle, move_data)
    if defender.is_alive and dmg:
        if randrange(1, 101) < move_data.ef_chance:
            paralyze(defender, battle)
        if randrange(1, 101) < move_data.ef_chance:
            _flinch(defender, battle, is_first)
    return True


def _ef_209(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    dmg = _calculate_damage(attacker, defender, battlefield, battle, move_data)
    if defender.is_alive and dmg:
        if randrange(1, 101) < move_data.ef_chance:
            freeze(defender, battle)
        if randrange(1, 101) < move_data.ef_chance:
            _flinch(defender, battle, is_first)
    return True


def _ef_210(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    dmg = _calculate_damage(attacker, defender, battlefield, battle, move_data)
    if defender.is_alive and dmg:
        if randrange(1, 101) < move_data.ef_chance:
            burn(defender, battle)
        if randrange(1, 101) < move_data.ef_chance:
            _flinch(defender, battle, is_first)
    return True


def _ef_211(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if defender.is_alive:
        battle.add_text(_stat_text(defender, gs.EVA, -1))
        if defender.evasion_stage > -6:
            defender.evasion_stage -= 1
    defender.trainer.spikes = 0
    defender.trainer.toxic_spikes = 0
    defender.stealth_rock = 0
    defender.trainer.safeguard = 0
    defender.trainer.light_screen = 0
    defender.trainer.reflect = 0
    defender.trainer.mist = 0


def _ef_212(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if not battlefield.trick_room_count:
        battlefield.trick_room_count = 5
        battle.add_text(attacker.nickname + " twisted the dimensions!")
    else:
        battlefield.trick_room_count = 0
        battle.add_text("The twisted dimensions return Trueed to normal!")


def _ef_213(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if (
        defender.is_alive
        and (attacker.gender == "male" and defender.gender == "female")
        or (attacker.gender == "female" and defender.gender == "male")
    ):
        give_stat_change(defender, battle, gs.SP_ATK, -2, forced=True)
    else:
        _failed(battle)


def _ef_214(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if not defender.trainer.stealth_rock:
        defender.trainer.steal_rock = 1
        battle.add_text(
            "Pointed stones float in the air around "
            + defender.trainer.name
            + "'s team!"
        )
    else:
        _failed(battle)


def _ef_215(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    dmg = _calculate_damage(attacker, defender, battlefield, battle, move_data)
    if defender.is_alive and dmg and randrange(100) < 1:
        confuse(defender, battle)
    return True


def _ef_216(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if attacker.item and attacker.item in gd.PLATE_DATA:
        move_data.type = gd.PLATE_DATA[attacker.item]


def _ef_217(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    dmg = _calculate_damage(attacker, defender, battlefield, battle, move_data)
    if dmg:
        _recoil(attacker, battle, max(1, dmg // 2), move_data)


def _ef_218(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    t = attacker.trainer
    if t.num_fainted >= len(t.poke_list) - 1:
        _failed(battle)
    attacker.faint()
    battle._process_selection(t)
    battle.add_text(t.current_poke.nickname + "became cloaked in mystical moonlight!")
    t.current_poke.heal(t.current_poke.max_hp)
    t.current_poke.nv_status = 0
    for move in t.current_poke.moves:
        move.cur_pp = move.max_pp


def _ef_219(
    attacker: pk.Pokemon,
    defender: pk.Pokemon,
    battlefield: bf.Battlefield,
    battle: bt.Battle,
    move_data: Move,
    is_first: bool,
    cc_ib: list,
) -> bool:
    if not move_data.ef_stat and not _power_herb_check(attacker, battle):
        move_data.ef_stat = 1
        attacker.next_moves.put(move_data)
        attacker.invulnerable = True
        attacker.inv_count = 1
        battle.add_text(attacker.nickname + " vanished instantly!")
    attacker.invulnerable = False


_MOVE_EFFECTS = [_ef_000, _ef_001, _ef_002, _ef_003, _ef_004, _ef_005, _ef_006, _ef_007, _ef_008, _ef_009, _ef_010, _ef_011, None, _ef_013, _ef_014, None, _ef_016, _ef_017, _ef_018, _ef_019, _ef_020, _ef_021, _ef_022, _ef_023, _ef_024, _ef_025, _ef_026, _ef_027, _ef_028, _ef_029, _ef_030, _ef_031, _ef_032, _ef_033, _ef_034, _ef_035, _ef_036, _ef_037, _ef_038, _ef_039, _ef_040, _ef_041, _ef_042, _ef_043, _ef_044, None, _ef_046, _ef_047, _ef_048, _ef_049, _ef_050, _ef_051, _ef_052, _ef_053, _ef_054, _ef_055, _ef_056, _ef_057, _ef_058, _ef_059, _ef_060, _ef_061, _ef_062, _ef_063, _ef_064, _ef_065, _ef_066, _ef_067, _ef_068, _ef_069, _ef_070, _ef_071, _ef_072, _ef_073, _ef_074, _ef_075, _ef_076, _ef_077, _ef_078, _ef_079, _ef_080, _ef_081, _ef_082, _ef_083, _ef_084, _ef_085, _ef_086, _ef_087, _ef_088, _ef_089, _ef_090, _ef_091, _ef_092, _ef_093, _ef_094, _ef_095, _ef_096, _ef_097, _ef_098, _ef_099, _ef_100, _ef_101, _ef_102, _ef_103, _ef_104, _ef_105, _ef_106, _ef_107, _ef_108, _ef_109, _ef_110, _ef_111, _ef_112, _ef_113, _ef_114, _ef_115, _ef_116, _ef_117, _ef_118, _ef_119, _ef_120, _ef_121, _ef_122, _ef_123, _ef_124, _ef_125, _ef_126, _ef_127, _ef_128, _ef_129, _ef_130, _ef_131, _ef_132, _ef_133, _ef_134, _ef_135, _ef_136, _ef_137, _ef_138, _ef_139, _ef_140, _ef_141, _ef_142, _ef_143, _ef_144, _ef_145, _ef_146, _ef_147, _ef_148, _ef_149, _ef_150, _ef_151, _ef_152, _ef_153, _ef_154, None, _ef_156, _ef_157, _ef_158, _ef_159, _ef_160, _ef_161, _ef_162, _ef_163, _ef_164, _ef_165, _ef_166, _ef_167, _ef_168, _ef_169, _ef_170, _ef_171, _ef_172, _ef_173, _ef_174, _ef_175, _ef_176, _ef_177, _ef_178, _ef_179, _ef_180, _ef_181, _ef_182, _ef_183, _ef_184, _ef_185, _ef_186, _ef_187, _ef_188, _ef_189, _ef_190, _ef_191, _ef_192, _ef_193, _ef_194, _ef_195, _ef_196, _ef_197, _ef_198, _ef_199, _ef_200, _ef_201, _ef_202, _ef_203, _ef_204, _ef_205, _ef_206, _ef_207, _ef_208, _ef_209, _ef_210, _ef_211, _ef_212, _ef_213, _ef_214, _ef_215, _ef_216, _ef_217, _ef_218, _ef_219]