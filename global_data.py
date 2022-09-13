# Specific Move Data
MOVE = 'move'
RECHARGING = ('other', 'recharging')
BIDING = ('other', 'biding')
RAGE = ('move', 'rage')
STRUGGLE = ('move', 'struggle')
PURSUIT = ('move', 'pursuit')
SWITCH = ('other', 'switch')
UPROAR = ('move', 'uproar')
FOCUS_PUNCH = ('move', 'focus-punch')
ME_FIRST = ('move', 'me-first')

# Check Data for Moves and Statuses
PROTECT_TARGETS = [8, 9, 10, 11]

PURSUIT_CHECK = {'baton-pass', 'teleport', 'u-turn', 'volt-switch', 'parting-shot'}

HP_TYPES = {'fighting', 'flying', 'poison', 'ground', 'rock', 'bug', 'ghost', 'steel', 'fire', 'water', 'grass',
            'electric', 'psychic', 'ice', 'dragon', 'dark'}

GROUNDED_CHECK = {'bounce', 'fly', 'high-jump-kick', 'jump-kick', 'magnet-rise', 'splash'}

HEAL_BLOCK_CHECK = {'heal-order', 'milk-drink', 'moonlight', 'morning-sun', 'recover', 'rest', 'roost', 'slack-off',
                    'soft-boiled', 'synthesis', 'wish', 'lunar-dance', 'healing-wish'}

METRONOME_CHECK = {'assist', 'chatter', 'copycat', 'counter', 'covet', 'destiny-bond', 'detect', 'endure', 'feint',
                   'focus-punch', 'follow-me', 'helping-hand', 'me-first', 'mimic', 'mirror-coat', 'mirror-move',
                   'protect', 'sketch', 'sleep-talk', 'snatch', 'struggle', 'switcheroo', 'thief', 'trick'}

ENCORE_CHECK = {'transform', 'mimic', 'sketch', 'mirror-move', 'sleep-talk', 'encore', 'struggle'}

ASSIST_CHECK = {'chatter', 'copycat', 'counter', 'covet', 'destiny-bond', 'detect', 'endure', 'feint', 'focus-punch',
                'follow-me', 'helping-hand', 'me-first', 'metronome', 'mimic', 'mirror-coat', 'mirror-move', 'protect'
                'sketch', 'sleep-talk', 'snatch', 'struggle', 'switcheroo', 'thief', 'trick'}

MAGIC_COAT_CHECK = {'attract', 'block', 'captivate', 'charm', 'confuse-ray', 'cotton-spore', 'dark-void', 'fake-tears',
                    'feather-dance', 'flash', 'flatter', 'gastro-acid', 'glare', 'grass-whistle', 'growl', 'hypnosis',
                    'kinesis', 'leech-seed', 'leer', 'lovely-kiss', 'mean-look', 'metal-sound', 'poison-gas', 'poison-powder',
                    'sand-attack', 'scary-face', 'screech', 'sing', 'sleep-powder', 'smokescreen', 'spider-web', 'spore',
                    'string-shot', 'stun-spore', 'supersonic', 'swagger', 'sweet-kiss', 'sweet-scent', 'tail-whip',
                    'thunder-wave', 'tickle', 'toxic', 'will-o-wisp', 'worry-seed', 'yawn'}

SNATCH_CHECK = {'acid-armor', 'acupressure', 'agility', 'amnesia', 'aromatherapy', 'barrier', 'belly-drum', 'bulk-up',
                'calm-mind', 'camouflage', 'charge', 'cosmic-power', 'defender-order', 'defender-curl', 'double-team',
                'dragon-dance', 'focus-energy', 'growth', 'harden', 'heal-bell', 'heal-order', 'howl', 'ingrain',
                'iron-defense', 'light-screen', 'meditate', 'milk-drink', 'minimize', 'mist', 'moonlight', 'morning-sun',
                'nasty-plot', 'psych-up', 'recover', 'reflect', 'refresh', 'rest', 'rock-polish', 'roost', 'safeguard',
                'sharpen', 'slack-off', 'soft-boiled', 'stockpile', 'substitute', 'swallow', 'swords-dance', 'synthesis',
                'tail-glow', 'tailwind', 'withdraw'}

GROUNDED_CHECK = {'bounce', 'fly', 'high-jump-kick', 'jump-kick', 'magnet-rise', 'splash'}

FREEZE_CHECK = {'flame-wheel', 'sacred-fire', 'flare-blitz'}

BERRY_DATA = {'cheri-berry': ('fire', 60), 'chesto-berry': ('water', 60), 'pecha-berry': ('electric', 60), 'rawst-berry': ('grass', 60),
              'aspear-berry': ('ice', 60), 'leppa-berry': ('fighting', 60), 'oran-berry': ('poison', 60), 'persim-berry': ('ground', 60),
              'lum-berry': ('flying', 60), 'sitrus-berry': ('psychic', 60), 'figy-berry': ('bug', 60), 'wiki-berry': ('rock', 60),
              'mago-berry': ('ghost', 60), 'aguav-berry': ('dragon', 60), 'iapapa-berry': ('dark', 60), 'razz-berry': ('steel', 60),
              'bluk-berry': ('fire', 70), 'nanb-berry': ('water', 70), 'wepear-berry': ('electric', 70), 'pinap-berry': ('grass', 70),
              'pomeg-berry': ('ice', 70), 'kelpsy-berry': ('fighting', 70), 'qualot-berry': ('poison', 70), 'hondew-berry': ('ground', 70),
              'grepa-berry': ('flying', 70), 'tamato-berry': ('psychic', 70), 'cornn-berry': ('bug', 70), 'magost-berry': ('rock', 70),
              'rabuta-berry': ('ghost', 70), 'nomel-berry': ('dragon', 70), 'spelon-berry': ('dark', 70), 'pamtre-berry': ('steel', 70),
              'watmel-berry': ('fire', 80), 'durin-berry': ('water', 80), 'belue-berry': ('electric', 80), 'occa-berry': ('fire', 60),
              'passho-berry': ('water', 60), 'wacan-berry': ('electric', 60), 'rindo-berry': ('grass', 60), 'yache-berry': ('ice', 60),
              'chople-berry': ('fighting', 60), 'kebia-berry': ('poison', 60), 'shuca-berry': ('ground', 60), 'coba-berry': ('flying', 60),
              'papaya-berry': ('psychic', 60), 'tanga-berry': ('bug', 60), 'charti-berry': ('rock', 60), 'kasib-berry': ('ghost', 60),
              'haban-berry': ('dragon', 60), 'colbur-berry': ('dark', 60), 'babiri-berry': ('steel', 60), 'chilan-berry': ('normal', 60),
              'liechi-berry': ('grass', 80), 'ganlon-berry': ('ice', 80), 'salac-berry': ('fighting', 80), 'petaya-berry': ('poison', 80),
              'apricot-berry': ('ground', 80), 'lansat-berry': ('flying', 80), 'starf-berry': ('psychic', 80), 'enigma-berry': ('bug', 80),
              'micle-berry': ('rock', 80), 'custap-berry': ('ghost', 80), 'jacoba-berry': ('dragon', 80), 'rowap-berry': ('dark', 80)}

PLATE_DATA = {'draco-plate': 'dragon', 'dread-plate': 'dark', 'earth-plate': 'ground', 'fist-plate': 'fighting',
              'flame-plate': 'fire', 'icicle-plate': 'ice', 'insect-plate': 'bug', 'iron-plate': 'steel',
              'meadow-plate': 'grass', 'mind-plate': 'psychic', 'sky-plate': 'flying', 'spooky-plate': 'ghost',
              'stone-plate': 'rock', 'toxic-plate': 'poison', 'zap-plate': 'electric'}

ABILITY_CHECK = {'stench', 'drizzle', 'speed-boost', 'battle-armor', 'sturdy', 'damp', 'limber', 'sand-veil', 'static',
                 'vold-absorb', 'water-absorb', 'oblivious', 'cloud-nine', 'compound-eyes', 'insomnia', 'color-change',
                 'immunity', 'flash-fire', 'shield-dust', 'own-tempo'}

CONTACT_CHECK = {'pound', 'karate-chop', 'double-slap', 'comet-punch', 'mega-punch', 'fire-punch', 'ice-punch', 'thunder-punch', 'scratch', 'vise-grip', 'guillotine', 'cut', 'wing-attack', 'fly', 'bind', 'slam', 'vine-whip', 'stomp', 'double-kick', 'mega-kick', 'jump-kick', 'rolling-kick', 'headbutt', 'horn-attack', 'fury-attack', 'horn-drill', 'tackle', 'body-slam', 'wrap', 'take-down', 'thrash', 'double-edge', 'bite', 'peck', 'drill-peck', 'submission', 'low-kick', 'counter', 'seismic-toss', 'strength', 'petal-dance', 'dig', 'quick-attack', 'rage', 'bide', 'lick', 'waterfall', 'clamp', 'skull-bash', 'constrict', 'high-jump-kick', 'leech-life', 'dizzy-punch', 'crabhammer', 'fury-swipes', 'hyper-fang', 'super-fang', 'slash', 'struggle', 'triple-kick', 'thief', 'flame-wheel', 'flail', 'reversal', 'mach-punch', 'feint-attack', 'outrage', 'rollout', 'false-swipe', 'spark', 'fury-cutter', 'steel-wing', 'return', 'frustration', 'dynamic-punch', 'megahorn', 'pursuit', 'rapid-spin', 'iron-tail', 'metal-claw', 'vital-throw', 'cross-chop', 'crunch', 'extreme-speed', 'rock-smash', 'fake-out', 'facade', 'focus-punch', 'smelling-salts', 'superpower', 'revenge', 'brick-break', 'knock-off', 'endeavor', 'dive', 'arm-thrust', 'blaze-kick', 'ice-ball', 'needle-arm', 'poison-fang', 'crush-claw', 'meteor-mash', 'astonish', 'shadow-punch', 'sky-uppercut', 'aerial-ace', 'dragon-claw', 'bounce', 'poison-tail', 'covet', 'volt-tackle', 'leaf-blade', 'wake-up-slap', 'hammer-arm', 'gyro-ball', 'pluck', 'u-turn', 'close-combat', 'payback', 'assurance', 'trump-card', 'wring-out', 'punishment', 'last-resort', 'sucker-punch', 'flare-blitz', 'force-palm', 'poison-jab', 'night-slash', 'aqua-tail', 'x-scissor', 'dragon-rush', 'drain-punch', 'brave-bird', 'giga-impact', 'bullet-punch', 'avalanche', 'shadow-claw', 'thunder-fang', 'ice-fang', 'fire-fang', 'shadow-sneak', 'zen-headbutt', 'rock-climb', 'power-whip', 'cross-poison', 'iron-head', 'grass-knot', 'bug-bite', 'wood-hammer', 'aqua-jet', 'head-smash', 'double-hit', 'crush-grip', 'shadow-force'}