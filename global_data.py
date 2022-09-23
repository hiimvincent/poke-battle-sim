# Specific Move Data
MOVE = 'move'
ITEM = 'item'
SWITCH = ['other', 'switch']
RECHARGING = ['other', 'recharging']
BIDING = ['other', 'biding']
RAGE = ['move', 'rage']
STRUGGLE = ['move', 'struggle']
PURSUIT = ['move', 'pursuit']
UPROAR = ['move', 'uproar']
FOCUS_PUNCH = ['move', 'focus-punch']
ME_FIRST = ['move', 'me-first']

# Check Data for Moves, Statuses, Items, and Abilities
PROTECT_TARGETS = [8, 9, 10, 11]

PURSUIT_CHECK = {'baton-pass', 'teleport', 'u-turn', 'volt-switch', 'parting-shot'}

HP_TYPES = ['fighting', 'flying', 'poison', 'ground', 'rock', 'bug', 'ghost', 'steel', 'fire', 'water', 'grass', 'electric', 'psychic', 'ice', 'dragon', 'dark']

GROUNDED_CHECK = {'bounce', 'fly', 'high-jump-kick', 'jump-kick', 'magnet-rise', 'splash'}

HEAL_BLOCK_CHECK = {'heal-order', 'milk-drink', 'moonlight', 'morning-sun', 'recover', 'rest', 'roost', 'slack-off', 'soft-boiled', 'synthesis', 'wish', 'lunar-dance', 'healing-wish'}

METRONOME_CHECK = {'assist', 'chatter', 'copycat', 'counter', 'covet', 'destiny-bond', 'detect', 'endure', 'feint', 'focus-punch', 'follow-me', 'helping-hand', 'me-first', 'mimic', 'mirror-coat', 'mirror-move', 'protect', 'sketch', 'sleep-talk', 'snatch', 'struggle', 'switcheroo', 'thief', 'trick'}

ENCORE_CHECK = {'transform', 'mimic', 'sketch', 'mirror-move', 'sleep-talk', 'encore', 'struggle'}

ASSIST_CHECK = {'chatter', 'copycat', 'counter', 'covet', 'destiny-bond', 'detect', 'endure', 'feint', 'focus-punch', 'follow-me', 'helping-hand', 'me-first', 'metronome', 'mimic', 'mirror-coat', 'mirror-move', 'protect' 'sketch', 'sleep-talk', 'snatch', 'struggle', 'switcheroo', 'thief', 'trick'}

MAGIC_COAT_CHECK = {'attract', 'block', 'captivate', 'charm', 'confuse-ray', 'cotton-spore', 'dark-void', 'fake-tears', 'feather-dance', 'flash', 'flatter', 'gastro-acid', 'glare', 'grass-whistle', 'growl', 'hypnosis', 'kinesis', 'leech-seed', 'leer', 'lovely-kiss', 'mean-look', 'metal-sound', 'poison-gas', 'poison-powder', 'sand-attack', 'scary-face', 'screech', 'sing', 'sleep-powder', 'smokescreen', 'spider-web', 'spore', 'string-shot', 'stun-spore', 'supersonic', 'swagger', 'sweet-kiss', 'sweet-scent', 'tail-whip', 'thunder-wave', 'tickle', 'toxic', 'will-o-wisp', 'worry-seed', 'yawn'}

SNATCH_CHECK = {'acid-armor', 'acupressure', 'agility', 'amnesia', 'aromatherapy', 'barrier', 'belly-drum', 'bulk-up', 'calm-mind', 'camouflage', 'charge', 'cosmic-power', 'defender-order', 'defender-curl', 'double-team', 'dragon-dance', 'focus-energy', 'growth', 'harden', 'heal-bell', 'heal-order', 'howl', 'ingrain', 'iron-defense', 'light-screen', 'meditate', 'milk-drink', 'minimize', 'mist', 'moonlight', 'morning-sun', 'nasty-plot', 'psych-up', 'recover', 'reflect', 'refresh', 'rest', 'rock-polish', 'roost', 'safeguard', 'sharpen', 'slack-off', 'soft-boiled', 'stockpile', 'substitute', 'swallow', 'swords-dance', 'synthesis', 'tail-glow', 'tailwind', 'withdraw'}

GROUNDED_CHECK = {'bounce', 'fly', 'high-jump-kick', 'jump-kick', 'magnet-rise', 'splash'}

SOUNDPROOF_CHECK = {'bug-buzz', 'chatter', 'grass-whistle', 'growl', 'heal-bell', 'hyper-voice', 'metal-sound', 'perish-song', 'roar', 'screech', 'sing', 'snore', 'supersonic', 'uproar'}

FREEZE_CHECK = {'flame-wheel', 'sacred-fire', 'flare-blitz'}

PUNCH_CHECK = {'bullet-punch', 'comet-punch', 'dizzy-punch', 'drain-punch', 'dynamic-punch', 'fire-punch', 'focus-punch', 'hammer-arm', 'ice-punch', 'match-punch', 'mega-punch', 'meteor-mash', 'shadow-punch', 'sky-uppercut', 'thunder-punch'}

RECOIL_CHECK = ['brave-bird', 'double-edge', 'flare-blitz', 'head-smash', 'high-jump-kick', 'jump-kick', 'submission', 'take-down', 'volt-tackle', 'wood-hammer']

BERRY_DATA = {'cheri-berry': ('fire', 60), 'chesto-berry': ('water', 60), 'pecha-berry': ('electric', 60), 'rawst-berry': ('grass', 60), 'aspear-berry': ('ice', 60), 'leppa-berry': ('fighting', 60), 'oran-berry': ('poison', 60), 'persim-berry': ('ground', 60), 'lum-berry': ('flying', 60), 'sitrus-berry': ('psychic', 60), 'figy-berry': ('bug', 60), 'wiki-berry': ('rock', 60), 'mago-berry': ('ghost', 60), 'aguav-berry': ('dragon', 60), 'iapapa-berry': ('dark', 60), 'razz-berry': ('steel', 60), 'bluk-berry': ('fire', 70), 'nanb-berry': ('water', 70), 'wepear-berry': ('electric', 70), 'pinap-berry': ('grass', 70), 'pomeg-berry': ('ice', 70), 'kelpsy-berry': ('fighting', 70), 'qualot-berry': ('poison', 70), 'hondew-berry': ('ground', 70), 'grepa-berry': ('flying', 70), 'tamato-berry': ('psychic', 70), 'cornn-berry': ('bug', 70), 'magost-berry': ('rock', 70), 'rabuta-berry': ('ghost', 70), 'nomel-berry': ('dragon', 70), 'spelon-berry': ('dark', 70), 'pamtre-berry': ('steel', 70), 'watmel-berry': ('fire', 80), 'durin-berry': ('water', 80), 'belue-berry': ('electric', 80), 'occa-berry': ('fire', 60), 'passho-berry': ('water', 60), 'wacan-berry': ('electric', 60), 'rindo-berry': ('grass', 60), 'yache-berry': ('ice', 60), 'chople-berry': ('fighting', 60), 'kebia-berry': ('poison', 60), 'shuca-berry': ('ground', 60), 'coba-berry': ('flying', 60), 'papaya-berry': ('psychic', 60), 'tanga-berry': ('bug', 60), 'charti-berry': ('rock', 60), 'kasib-berry': ('ghost', 60), 'haban-berry': ('dragon', 60), 'colbur-berry': ('dark', 60), 'babiri-berry': ('steel', 60), 'chilan-berry': ('normal', 60), 'liechi-berry': ('grass', 80), 'ganlon-berry': ('ice', 80), 'salac-berry': ('fighting', 80), 'petaya-berry': ('poison', 80), 'apricot-berry': ('ground', 80), 'lansat-berry': ('flying', 80), 'starf-berry': ('psychic', 80), 'enigma-berry': ('bug', 80), 'micle-berry': ('rock', 80), 'custap-berry': ('ghost', 80), 'jacoba-berry': ('dragon', 80), 'rowap-berry': ('dark', 80)}

PLATE_DATA = {'draco-plate': 'dragon', 'dread-plate': 'dark', 'earth-plate': 'ground', 'fist-plate': 'fighting', 'flame-plate': 'fire', 'icicle-plate': 'ice', 'insect-plate': 'bug', 'iron-plate': 'steel', 'meadow-plate': 'grass', 'mind-plate': 'psychic', 'sky-plate': 'flying', 'spooky-plate': 'ghost', 'stone-plate': 'rock', 'toxic-plate': 'poison', 'zap-plate': 'electric'}

ABILITY_CHECK = {'stench', 'drizzle', 'speed-boost', 'battle-armor', 'sturdy', 'damp', 'limber', 'sand-veil', 'static', 'vold-absorb', 'water-absorb', 'oblivious', 'cloud-nine', 'compound-eyes', 'insomnia', 'color-change', 'immunity', 'flash-fire', 'shield-dust', 'own-tempo'}

CONTACT_CHECK = {'pound', 'karate-chop', 'double-slap', 'comet-punch', 'mega-punch', 'fire-punch', 'ice-punch', 'thunder-punch', 'scratch', 'vise-grip', 'guillotine', 'cut', 'wing-attack', 'fly', 'bind', 'slam', 'vine-whip', 'stomp', 'double-kick', 'mega-kick', 'jump-kick', 'rolling-kick', 'headbutt', 'horn-attack', 'fury-attack', 'horn-drill', 'tackle', 'body-slam', 'wrap', 'take-down', 'thrash', 'double-edge', 'bite', 'peck', 'drill-peck', 'submission', 'low-kick', 'counter', 'seismic-toss', 'strength', 'petal-dance', 'dig', 'quick-attack', 'rage', 'bide', 'lick', 'waterfall', 'clamp', 'skull-bash', 'constrict', 'high-jump-kick', 'leech-life', 'dizzy-punch', 'crabhammer', 'fury-swipes', 'hyper-fang', 'super-fang', 'slash', 'struggle', 'triple-kick', 'thief', 'flame-wheel', 'flail', 'reversal', 'mach-punch', 'feint-attack', 'outrage', 'rollout', 'false-swipe', 'spark', 'fury-cutter', 'steel-wing', 'return', 'frustration', 'dynamic-punch', 'megahorn', 'pursuit', 'rapid-spin', 'iron-tail', 'metal-claw', 'vital-throw', 'cross-chop', 'crunch', 'extreme-speed', 'rock-smash', 'fake-out', 'facade', 'focus-punch', 'smelling-salts', 'superpower', 'revenge', 'brick-break', 'knock-off', 'endeavor', 'dive', 'arm-thrust', 'blaze-kick', 'ice-ball', 'needle-arm', 'poison-fang', 'crush-claw', 'meteor-mash', 'astonish', 'shadow-punch', 'sky-uppercut', 'aerial-ace', 'dragon-claw', 'bounce', 'poison-tail', 'covet', 'volt-tackle', 'leaf-blade', 'wake-up-slap', 'hammer-arm', 'gyro-ball', 'pluck', 'u-turn', 'close-combat', 'payback', 'assurance', 'trump-card', 'wring-out', 'punishment', 'last-resort', 'sucker-punch', 'flare-blitz', 'force-palm', 'poison-jab', 'night-slash', 'aqua-tail', 'x-scissor', 'dragon-rush', 'drain-punch', 'brave-bird', 'giga-impact', 'bullet-punch', 'avalanche', 'shadow-claw', 'thunder-fang', 'ice-fang', 'fire-fang', 'shadow-sneak', 'zen-headbutt', 'rock-climb', 'power-whip', 'cross-poison', 'iron-head', 'grass-knot', 'bug-bite', 'wood-hammer', 'aqua-jet', 'head-smash', 'double-hit', 'crush-grip', 'shadow-force'}

USABLE_ITEM_CHECK = {'potion', 'antidote', 'burn-heal', 'ice-heal', 'awakening', 'parlyz-heal', 'full-restore', 'max-potion', 'hyper-potion', 'super-potion', 'full-heal', 'revive', 'max-revive', 'fresh-water', 'soda-pop', 'lemonade', 'moomoo-milk', 'energypowder', 'energy-root', 'heal-powder', 'revival-herb', 'ether', 'max-ether', 'elixir', 'max-elixir', 'old-gateau', 'guard-spec.', 'dire-hit', 'x-attack', 'x-defense', 'x-speed', 'x-accuracy', 'x-special', 'x-sp.-def', 'blue-flute', 'yellow-flute', 'red-flute', 'cheri-berry', 'chesto-berry', 'pecha-berry', 'rawst-berry', 'aspear-berry', 'leppa-berry', 'oran-berry', 'persim-berry', 'lum-berry', 'sitrus-berry'}

DMG_ITEM_CHECK = {'griseous-orb', 'adamant-orb', 'lustrous-orb','silver-powder', 'insect-plate', 'soul-dew', 'metal-coat', 'iron-plate', 'soft-sand', 'earth-plate', 'hard-stone', 'stone-plate', 'rock-incense', 'miracle-seed', 'meadow-plate', 'rose-incense', 'blackglasses', 'dread-plate', 'black-belt', 'fist-plate', 'magnet', 'zap-plate', 'mystic-water', 'sea-incense', 'wave-incense', 'splash-plate', 'sharp-beak', 'sky-plate', 'poison-barb', 'toxic-plate', 'nevermeltice', 'icicle-plate', 'spell-tag', 'spooky-plate', 'twistedspoon', 'mind-plate', 'odd-incense', 'charcoal', 'flame-plate', 'dragon-fang', 'draco-plate', 'silk-scarf', 'muscle-band', 'wise-glasses', 'metronome'}

DMG_MULT_ITEM_CHECK = {'expert-belt', 'life-orb'}

PRE_HIT_BERRIES = {'occa-berry': 'fire', 'passho-berry': 'water', 'wacan-berry': 'electric', 'rindo-berry': 'grass', 'yache-berry': 'ice', 'chople-berry': 'fighting', 'kebia-berry': 'poison', 'shuca-berry': 'ground', 'coba-berry': 'flying', 'papaya-berry': 'psychic', 'tanga-berry': 'bug', 'charti-berry': 'rock', 'kasib-berry': 'ghost', 'haban-berry': 'dragon', 'colbur-berry': 'dark', 'babiri-berry': 'steel', 'chilan-berry': 'normal'}

ON_DAMAGE_ITEM_CHECK = {'liechi-berry', 'ganlon-berry', 'salac-berry', 'petaya-berry', 'apricot-berry', 'lansat-berry', 'starf-berry', 'micle-berry', 'custap-berry', 'enigma-berry'}

PRE_MOVE_ITEM_CHECK = {'quick-claw'}

STAT_CALC_ITEM_CHECK = {'metal-powder', 'quick-powder', 'thick-club', 'choice-band', 'choice-specs', 'choice-scarf', 'deepseatooth', 'deepseascale', 'light-ball', 'iron-ball'}

STATUS_ITEM_CHECK = {'cheri-berry', 'chesto-berry', 'pecha-berry', 'rawst-berry', 'aspear-berry', 'persim-berry', 'lum-berry', 'mental-herb', 'destiny-knot'}

ON_HIT_ITEM_CHECK = {'jaboca-berry', 'rowap-berry', 'sticky-barb'}

HOMC_ITEM_CHECK = {'brightpowder', 'lax-incense', 'wide-lens', 'zoom-lens'}

END_TURN_ITEM_CHECK = {'oran-berry', 'sitrus-berry', 'figy-berry', 'wiki-berry', 'mago-berry', 'aguav-berry', 'iapapa-berry', 'leftovers', 'black-sludge', 'toxic-orb', 'flame-orb', 'sticky-barb'}

POST_DAMAGE_ITEM_CHECK = {'shell-bell', 'life-orb'}

EXTRA_FLINCH_CHECK = {'aerial-ace', 'aeroblast', 'air-cutter', 'air-slash', 'aqua-jet', 'aqua-tail', 'arm-thrust', 'assurance', 'attack-order', 'aura-sphere', 'avalanche', 'barrage', 'beat-up', 'bide', 'bind', 'blast-burn', 'bone-rush', 'bonemerang', 'bounce', 'brave-bird', 'brick-break', 'brine', 'bug-bite', 'bullet-punch', 'bullet-seed', 'charge-beam', 'clamp', 'close-combat', 'comet-punch', 'crabhammer', 'cross-chop', 'cross-poison', 'crush-grip', 'cut', 'dark-pulse', 'dig', 'discharge', 'dive', 'double-hit', 'double-kick', 'double-slap', 'double-edge', 'draco-meteor', 'dragon-breath', 'dragon-claw', 'dragon-pulse', 'dragon-rush', 'drain-punch', 'drill-peck', 'earth-power', 'earthquake', 'egg-bomb', 'endeavor', 'eruption', 'explosion', 'extreme-speed', 'false-swipe', 'feint-attack', 'fire-fang', 'fire-spin', 'flail', 'flash-cannon', 'fly', 'force-palm', 'frenzy-plant', 'frustration', 'fury-attack', 'fury-cutter', 'fury-swipes', 'giga-impact', 'grass-knot', 'gunk-shot', 'gyro-ball', 'hammer-arm', 'head-smash', 'hidden-power', 'high-jump-kick', 'horn-attack', 'hydro-cannon', 'hydro-pump', 'hyper-beam', 'ice-ball', 'ice-fang', 'ice-shard', 'icicle-spear', 'iron-head', 'judgment', 'jump-kick', 'karate-chop', 'last-resort', 'lava-plume', 'leaf-blade', 'leaf-storm', 'low-kick', 'mach-punch', 'magical-leaf', 'magma-storm', 'magnet-bomb', 'magnitude', 'mega-kick', 'mega-punch', 'megahorn', 'meteor-mash', 'mirror-coat', 'mirror-shot', 'mud-bomb', 'mud-shot', 'muddy-water', 'night-shade', 'night-slash', 'ominous-wind', 'outrage', 'overheat', 'pay-day', 'payback', 'peck', 'petal-dance', 'pin-missile', 'pluck', 'poison-jab', 'poison-tail', 'power-gem', 'power-whip', 'psycho-boost', 'psycho-cut', 'psywave', 'punishment', 'quick-attack', 'rage', 'rapid-spin', 'razor-leaf', 'razor-wind', 'return', 'revenge', 'reversal', 'roar-of-time', 'rock-blast', 'rock-climb', 'rock-throw', 'rock-wrecker', 'rolling-kick', 'rollout', 'sand-tomb', 'scratch', 'seed-bomb', 'seed-flare', 'seismic-toss', 'self-destruct', 'shadow-claw', 'shadow-force', 'shadow-punch', 'shadow-sneak', 'shock-wave', 'signal-beam', 'silver-wind', 'skull-bash', 'sky-attack', 'sky-uppercut', 'slam', 'slash', 'snore', 'solar-beam', 'sonic-boom', 'spacial-rend', 'spike-cannon', 'spit-up', 'steel-wing', 'stone-edge', 'strength', 'struggle', 'submission', 'sucker-punch', 'surf', 'swift', 'tackle', 'take-down', 'thrash', 'thunder-fang', 'triple-kick', 'trump-card', 'twister', 'u-turn', 'uproar', 'vacuum-wave', 'vice-grip', 'vine-whip', 'vital-throw', 'volt-tackle', 'wake-up-slap', 'water-gun', 'water-pulse', 'waterfall', 'weather-ball', 'whirlpool', 'wing-attack', 'wood-hammer', 'wrap', 'x-scissor'}

HEALING_ITEM_CHECK = {'potion': 20, 'hyper-potion': 200, 'super-potion': 50, 'fresh-water': 50, 'soda-pop': 60, 'lemonade': 80, 'moomoo-milk': 100, 'energypowder': 50, 'energy-root': 200, 'berry-juice': 20, 'oran-berry': 10, 'sitrus-berry': 30}

TWO_TURN_CHECK = {'razor-wind', 'fly', 'dig', 'skull-bash', 'sky-attack', 'dive', 'bounce', 'shadow-force', 'bide', 'solar-beam', 'ice-ball', 'thrash', 'petal-dance', 'outrage'}