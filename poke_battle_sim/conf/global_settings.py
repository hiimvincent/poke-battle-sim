# CSV Paths
DATA_DIR = 'data'
POKEMON_STATS_CSV = 'pokemon_stats.csv'
NATURES_CSV = 'natures.csv'
MOVES_CSV = 'move_list.csv'
TYPE_EF_CSV = 'type_effectiveness.csv'
ABILITIES_CSV = 'abilities.csv'
ITEMS_CSV = 'items_gen4.csv'

# Stat Ranges
LEVEL_MIN, LEVEL_MAX = 1, 100
STAT_ACTUAL_MIN, STAT_ACTUAL_MAX = 1, 500
IV_MIN, IV_MAX = 0, 31
EV_MIN, EV_MAX = 0, 255
EV_TOTAL_MAX = 510
NATURE_DEC, NATURE_INC = 0.9, 1.1

# Misc Settings
POKE_NUM_MIN, POKE_NUM_MAX = 1, 6
POSSIBLE_GENDERS = ['male', 'female', 'genderless']
COMPLETED_MOVES = 467

# Non-volatile Statuses
BURNED = 1
FROZEN = 2
PARALYZED = 3
POISONED = 4
ASLEEP = 5
BADLY_POISONED = 6

# Non-volatile Status Conversion
NV_STATUSES = {
    'burned': 1,
    'frozen': 2,
    'paralyzed': 3,
    'poisoned': 4,
    'asleep': 5,
    'badly poisoned': 6
}

# Volatile Statuses
V_STATUS_NUM = 9
CONFUSED = 0
FLINCHED = 1
LEECH_SEED = 2
BINDING_COUNT = 3
NIGHTMARE = 4
CURSE = 5
DROWSY = 6
INGRAIN = 7
AQUA_RING = 8

# Binding Types
BIND = 1
WRAP = 2
FIRE_SPIN = 3
CLAMP = 4
WHIRLPOOL = 5
SAND_TOMB = 6
MAGMA_STORM = 7

# Weather Types
CLEAR = 0
HARSH_SUNLIGHT = 1
RAIN = 2
SANDSTORM = 3
HAIL = 4
FOG = 5

# Stat Ordering Format
HP = 0
ATK = 1
DEF = 2
SP_ATK = 3
SP_DEF = 4
SPD = 5
STAT_NUM = 6
ACC = 6
EVA = 7

STAT_TO_NAME = ['Health', 'Attack', 'Defense', 'Sp. Atk', 'Sp. Def', 'Speed', 'accuracy', 'evasion']

# Move Categories
STATUS = 1
PHYSICAL = 2
SPECIAL = 3

# Base Pokemon Stats Formatting
NDEX = 0
NAME = 1
TYPE1 = 2
TYPE2 = 3
STAT_START = 4
# HP = 4, ATK = 5, DEF = 6, SP_ATK = 7, SP_DEF = 8, SPD = 9
HEIGHT = 10
WEIGHT = 11
BASE_EXP = 12
GEN = 13

# Move Data Formatting
MOVE_ID = 0
MOVE_NAME = 1
MOVE_TYPE = 3
MOVE_POWER = 4
MOVE_PP = 5
MOVE_ACC = 6
MOVE_PRIORITY = 7
MOVE_TARGET = 8
MOVE_CATEGORY = 9
MOVE_EFFECT_ID = 10
MOVE_EFFECT_CHANCE = 11
MOVE_EFFECT_AMT = 12
MOVE_EFFECT_STAT = 13

# CSV Numerical Columns
POKEMON_STATS_NUMS = [0, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
MOVES_NUM = [0, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]

# Player Turn Actions
ACTION_PRIORITY = {
    'other': 3,
    'item': 2,
    'move': 1
}

# Turn Data
ACTION_TYPE = 0
ACTION_VALUE = 1
ITEM_TARGET_POS = 2
MOVE_TARGET_POS = 3

# Pre-process Move Data
PPM_MOVE = 0
PPM_MOVE_DATA = 1
PPM_BYPASS = 2

# Item Thresholds
BERRY_THRESHOLD = 0.5
DAMAGE_THRESHOLD = 0.25