"""Word search generator with themed word lists."""
from __future__ import annotations

import random
from dataclasses import dataclass

# All 8 directions as (row step, col step).
DIRS_ALL = [(0, 1), (1, 0), (1, 1), (-1, 1), (0, -1), (-1, 0), (-1, -1), (1, -1)]
# Forward-only directions for easier puzzles.
DIRS_EASY = [(0, 1), (1, 0), (1, 1)]

# Letters weighted roughly like English so the filler looks natural.
FILL = "EEEEEEAAAAARRRRIIIIOOOOTTTTNNNNSSSSLLLCCCUUUDDDPPMMHHGGBBFFYYWKVXZJQ"


@dataclass
class Placement:
    word: str       # display form, e.g. "BALD EAGLE"
    row: int
    col: int
    dr: int
    dc: int
    length: int

    def cells(self) -> list[tuple[int, int]]:
        return [(self.row + k * self.dr, self.col + k * self.dc) for k in range(self.length)]


@dataclass
class WordSearch:
    title: str
    grid: list[list[str]]
    placements: list[Placement]

    @property
    def words(self) -> list[str]:
        return sorted(p.word for p in self.placements)


def _key(word: str) -> str:
    return "".join(ch for ch in word.upper() if ch.isalpha())


def make_puzzle(
    rng: random.Random,
    title: str,
    words: list[str],
    size: int = 15,
    count: int = 15,
    dirs: list[tuple[int, int]] | None = None,
) -> WordSearch:
    dirs = dirs or DIRS_ALL
    pool = [w.upper() for w in words if 3 <= len(_key(w)) <= size]
    for _attempt in range(50):
        chosen = rng.sample(pool, min(count, len(pool)))
        chosen.sort(key=lambda w: -len(_key(w)))
        grid = [["" for _ in range(size)] for _ in range(size)]
        placements: list[Placement] = []
        for w in chosen:
            p = _place(rng, grid, w, dirs)
            if p is None:
                break
            placements.append(p)
        else:
            for r in range(size):
                for c in range(size):
                    if not grid[r][c]:
                        grid[r][c] = rng.choice(FILL)
            if all(_occurrences(grid, _key(p.word)) == 1 for p in placements):
                return WordSearch(title, grid, placements)
    raise RuntimeError(f"could not build word search for {title!r}")


def _place(rng, grid, word, dirs) -> Placement | None:
    key = _key(word)
    n = len(grid)
    options = []
    for dr, dc in dirs:
        for r in range(n):
            for c in range(n):
                er, ec = r + dr * (len(key) - 1), c + dc * (len(key) - 1)
                if not (0 <= er < n and 0 <= ec < n):
                    continue
                overlap = 0
                fits = True
                for k, ch in enumerate(key):
                    cell = grid[r + dr * k][c + dc * k]
                    if cell == ch:
                        overlap += 1
                    elif cell:
                        fits = False
                        break
                if fits and overlap < len(key):
                    options.append((overlap, rng.random(), r, c, dr, dc))
    if not options:
        return None
    # Prefer some crossings (looks professional) but keep it random.
    options.sort(reverse=True)
    pick = rng.choice(options[: max(1, len(options) // 4)])
    _, _, r, c, dr, dc = pick
    for k, ch in enumerate(key):
        grid[r + dr * k][c + dc * k] = ch
    return Placement(word, r, c, dr, dc, len(key))


def _occurrences(grid: list[list[str]], key: str) -> int:
    """How many times a word appears in any of the 8 directions (palindromes count once)."""
    n = len(grid)
    hits = set()
    for dr, dc in DIRS_ALL:
        for r in range(n):
            for c in range(n):
                cells = []
                for k in range(len(key)):
                    rr, cc = r + dr * k, c + dc * k
                    if not (0 <= rr < n and 0 <= cc < n) or grid[rr][cc] != key[k]:
                        break
                    cells.append((rr, cc))
                else:
                    hits.add(frozenset(cells))
    return len(hits)


THEMES: dict[str, list[str]] = {
    "In the Garden": ["TULIP", "ROSE", "DAISY", "TROWEL", "COMPOST", "SEEDLING", "WATERING CAN", "HOSE", "MULCH", "PANSY", "MARIGOLD", "LAVENDER", "SHED", "TRELLIS", "BULBS", "PRUNE", "WEEDS", "SUNFLOWER", "HERBS", "GREENHOUSE", "IVY", "PEONY"],
    "Backyard Birds": ["ROBIN", "BLUEJAY", "CARDINAL", "SPARROW", "FINCH", "WREN", "CHICKADEE", "NUTHATCH", "WARBLER", "ORIOLE", "DOVE", "STARLING", "BLUEBIRD", "TITMOUSE", "JUNCO", "GRACKLE", "HUMMINGBIRD", "FEEDER", "NEST", "FEATHER", "WOODPECKER", "BIRDBATH"],
    "Baking Day": ["FLOUR", "SUGAR", "BUTTER", "YEAST", "DOUGH", "OVEN", "WHISK", "ROLLING PIN", "MUFFIN", "COOKIE", "PIE CRUST", "VANILLA", "CINNAMON", "KNEAD", "FROSTING", "SPATULA", "BISCUIT", "SCONE", "SPRINKLES", "TIMER", "APRON", "BAKING SODA"],
    "At the Beach": ["SAND", "WAVES", "SEASHELL", "TIDE", "TOWEL", "UMBRELLA", "SUNSCREEN", "LIGHTHOUSE", "PIER", "SEAGULL", "CRAB", "DUNES", "SURF", "BOARDWALK", "PELICAN", "SANDCASTLE", "COOLER", "FLIP FLOPS", "SNORKEL", "OCEAN", "BREEZE", "SUNSET"],
    "National Parks": ["YOSEMITE", "ZION", "YELLOWSTONE", "GLACIER", "ACADIA", "DENALI", "ARCHES", "OLYMPIC", "SEQUOIA", "EVERGLADES", "SHENANDOAH", "BADLANDS", "BIG BEND", "REDWOOD", "SAGUARO", "BRYCE CANYON", "GRAND TETON", "JOSHUA TREE", "CANYONLANDS", "HALEAKALA", "VOYAGEURS", "CONGAREE"],
    "Kitchen Things": ["KETTLE", "TOASTER", "SKILLET", "LADLE", "COLANDER", "TEAPOT", "BLENDER", "GRATER", "TONGS", "PLATTER", "SAUCEPAN", "MIXER", "PANTRY", "CUTTING BOARD", "MEASURING CUP", "STOCKPOT", "OVEN MITT", "PEELER", "CORKSCREW", "NAPKIN", "SAUCER", "CASSEROLE"],
    "Musical Instruments": ["PIANO", "VIOLIN", "CELLO", "GUITAR", "BANJO", "FLUTE", "CLARINET", "TRUMPET", "TROMBONE", "SAXOPHONE", "HARP", "DRUMS", "TUBA", "OBOE", "BASSOON", "UKULELE", "HARMONICA", "ACCORDION", "XYLOPHONE", "MANDOLIN", "ORGAN", "PICCOLO"],
    "Weather Watch": ["SUNNY", "CLOUDY", "RAINBOW", "THUNDER", "LIGHTNING", "DRIZZLE", "HAIL", "SLEET", "BLIZZARD", "FOG", "HUMIDITY", "BREEZE", "TORNADO", "HURRICANE", "FORECAST", "BAROMETER", "FROST", "DEW POINT", "MONSOON", "SHOWERS", "HEAT WAVE", "OVERCAST"],
    "Ocean Life": ["DOLPHIN", "WHALE", "OCTOPUS", "STARFISH", "SEAHORSE", "JELLYFISH", "SHARK", "TURTLE", "LOBSTER", "CORAL", "SQUID", "MANATEE", "STINGRAY", "CLAM", "OYSTER", "WALRUS", "SEAL", "ORCA", "KELP", "BARNACLE", "SWORDFISH", "PUFFERFISH"],
    "Classic Board Games": ["CHESS", "CHECKERS", "BACKGAMMON", "DOMINOES", "SCRABBLE", "MONOPOLY", "CLUE", "BINGO", "MAHJONG", "PARCHEESI", "CRIBBAGE", "YAHTZEE", "DICE", "PAWN", "BISHOP", "KNIGHT", "ROOK", "SPINNER", "GAME BOARD", "TOKEN", "CHINESE CHECKERS", "SORRY"],
    "Fruit Basket": ["APPLE", "BANANA", "CHERRY", "GRAPE", "LEMON", "MANGO", "PEACH", "PEAR", "PLUM", "APRICOT", "KIWI", "PAPAYA", "PINEAPPLE", "WATERMELON", "BLUEBERRY", "RASPBERRY", "TANGERINE", "NECTARINE", "FIG", "POMEGRANATE", "CRANBERRY", "GUAVA"],
    "Vegetable Patch": ["CARROT", "POTATO", "TOMATO", "ONION", "GARLIC", "CELERY", "SPINACH", "LETTUCE", "CABBAGE", "BROCCOLI", "ZUCCHINI", "PUMPKIN", "RADISH", "TURNIP", "BEETS", "PEAS", "ASPARAGUS", "CUCUMBER", "EGGPLANT", "KALE", "LEEK", "SQUASH"],
    "Around the House": ["ATTIC", "BASEMENT", "PORCH", "CHIMNEY", "HALLWAY", "STAIRCASE", "DOORBELL", "MAILBOX", "CURTAINS", "BOOKSHELF", "FIREPLACE", "LAMP", "RUG", "SOFA", "PILLOW", "WINDOW", "GARAGE", "LAUNDRY", "CLOSET", "FENCE", "DRIVEWAY", "PANTRY"],
    "Knitting and Sewing": ["YARN", "NEEDLE", "THREAD", "BUTTON", "THIMBLE", "PATTERN", "STITCH", "BOBBIN", "SPOOL", "FABRIC", "QUILT", "SCISSORS", "PINCUSHION", "CROCHET", "HEM", "SEAM", "ZIPPER", "WOOL", "SKEIN", "PURL", "TAPE MEASURE", "EMBROIDERY"],
    "Breakfast Table": ["PANCAKES", "WAFFLES", "BACON", "OATMEAL", "TOAST", "OMELET", "CEREAL", "MUFFIN", "YOGURT", "GRANOLA", "SYRUP", "COFFEE", "ORANGE JUICE", "BAGEL", "HASH BROWNS", "SAUSAGE", "GRITS", "CROISSANT", "JAM", "HONEY", "TEA", "FRENCH TOAST"],
    "Farm Animals": ["COW", "HORSE", "PIG", "SHEEP", "GOAT", "CHICKEN", "ROOSTER", "DUCK", "GOOSE", "TURKEY", "DONKEY", "LLAMA", "ALPACA", "PONY", "CALF", "LAMB", "PIGLET", "BARN", "TRACTOR", "HAYLOFT", "PASTURE", "STABLE"],
    "Space and Stars": ["PLANET", "COMET", "GALAXY", "NEBULA", "ASTEROID", "ORBIT", "ROCKET", "SATELLITE", "TELESCOPE", "MERCURY", "VENUS", "MARS", "JUPITER", "SATURN", "URANUS", "NEPTUNE", "ECLIPSE", "METEOR", "COSMOS", "ASTRONAUT", "MILKY WAY", "CONSTELLATION"],
    "Trees of the Forest": ["OAK", "MAPLE", "BIRCH", "PINE", "SPRUCE", "CEDAR", "WILLOW", "ELM", "ASPEN", "HICKORY", "WALNUT", "CHESTNUT", "SYCAMORE", "MAGNOLIA", "DOGWOOD", "REDWOOD", "SEQUOIA", "CYPRESS", "JUNIPER", "HEMLOCK", "POPLAR", "BEECH"],
    "Fishing Trip": ["ROD", "REEL", "BAIT", "LURE", "TACKLE BOX", "BOBBER", "SINKER", "NET", "CANOE", "LAKE", "TROUT", "BASS", "CATFISH", "SALMON", "WALLEYE", "PERCH", "WADERS", "CAST", "HOOK", "DOCK", "CREEK", "MINNOW"],
    "Holiday Season": ["WREATH", "GARLAND", "STOCKING", "TINSEL", "CANDLE", "SNOWMAN", "COCOA", "SLEIGH", "REINDEER", "CAROLS", "GINGERBREAD", "MISTLETOE", "ORNAMENT", "RIBBON", "PRESENTS", "EGGNOG", "FIREPLACE", "SNOWFLAKE", "CANDY CANE", "LIGHTS", "FAMILY", "FEAST"],
    "Autumn Days": ["LEAVES", "PUMPKIN", "HARVEST", "ACORN", "SCARECROW", "HAYRIDE", "CIDER", "SWEATER", "RAKE", "ORCHARD", "CORNSTALK", "SQUIRREL", "CHESTNUT", "BONFIRE", "GOURD", "MAPLE", "PIE", "CRISP", "SCARF", "HARVEST MOON", "APPLE PICKING", "FOLIAGE"],
    "Springtime": ["BLOSSOM", "BUD", "DAFFODIL", "LILAC", "TULIP", "RAIN", "PUDDLE", "UMBRELLA", "ROBIN", "BUNNY", "LAMB", "SPROUT", "MEADOW", "PICNIC", "KITE", "BUTTERFLY", "BUMBLEBEE", "EASTER", "GREEN", "SUNSHINE", "SEEDS", "BREEZE"],
    "Summer Fun": ["SWIMMING", "BARBECUE", "LEMONADE", "CAMPING", "FIREFLIES", "ICE CREAM", "HAMMOCK", "VACATION", "SPRINKLER", "WATERMELON", "FIREWORKS", "POPSICLE", "SUNGLASSES", "ROAD TRIP", "PICNIC", "PADDLE", "CANOE", "BONFIRE", "SANDALS", "SUNHAT", "PARADE", "FAIR"],
    "Winter Wonderland": ["SNOW", "ICICLE", "MITTENS", "SLED", "SKATES", "IGLOO", "FROST", "BLANKET", "FLANNEL", "SNOWBALL", "CHILL", "SHOVEL", "TOBOGGAN", "SKIING", "PARKA", "EARMUFFS", "HOT COCOA", "FIRESIDE", "POLAR", "SNOWDRIFT", "WOOL SOCKS", "HIBERNATE"],
    "Dog Breeds": ["BEAGLE", "POODLE", "BOXER", "COLLIE", "DALMATIAN", "TERRIER", "SPANIEL", "RETRIEVER", "LABRADOR", "BULLDOG", "CHIHUAHUA", "DACHSHUND", "GREYHOUND", "HUSKY", "PUG", "CORGI", "SHEEPDOG", "MASTIFF", "SCHNAUZER", "POINTER", "WHIPPET", "BASSET"],
    "Cat Corner": ["WHISKERS", "PURR", "KITTEN", "TABBY", "CALICO", "SIAMESE", "PERSIAN", "MAINE COON", "SCRATCH", "LITTER", "CATNIP", "YARN BALL", "MEOW", "PAWS", "TAIL", "NAP", "SUNBEAM", "COLLAR", "TREATS", "POUNCE", "TOMCAT", "SPHYNX"],
    "Travel and Trips": ["PASSPORT", "SUITCASE", "AIRPORT", "TICKET", "LUGGAGE", "MAP", "COMPASS", "CRUISE", "TRAIN", "HOTEL", "POSTCARD", "SOUVENIR", "ITINERARY", "JOURNEY", "BACKPACK", "TOURIST", "CAMERA", "GUIDEBOOK", "DEPARTURE", "ARRIVAL", "BOARDING", "EXPLORE"],
    "Good Feelings": ["JOY", "PEACE", "HOPE", "KINDNESS", "GRATITUDE", "LAUGHTER", "CALM", "COMFORT", "WONDER", "DELIGHT", "CHEERFUL", "GENTLE", "PATIENCE", "FRIENDSHIP", "CHARITY", "WARMTH", "SMILE", "BLESSING", "HARMONY", "CONTENT", "SERENITY", "TRUST"],
    "Colors": ["CRIMSON", "SCARLET", "MAROON", "CORAL", "AMBER", "GOLDEN", "LEMON", "OLIVE", "EMERALD", "JADE", "TEAL", "TURQUOISE", "AZURE", "NAVY", "INDIGO", "VIOLET", "LAVENDER", "MAGENTA", "IVORY", "BEIGE", "CHARCOAL", "SILVER"],
    "Sports": ["BASEBALL", "FOOTBALL", "SOCCER", "TENNIS", "GOLF", "HOCKEY", "BOWLING", "BASKETBALL", "VOLLEYBALL", "SWIMMING", "CYCLING", "ARCHERY", "ROWING", "BOXING", "WRESTLING", "SKIING", "CURLING", "CROQUET", "BADMINTON", "PICKLEBALL", "SOFTBALL", "LACROSSE"],
    "Tea Party": ["TEAPOT", "TEACUP", "SAUCER", "EARL GREY", "CHAMOMILE", "DARJEELING", "OOLONG", "SCONES", "CLOTTED CREAM", "CUCUMBER", "SANDWICH", "LACE", "DOILY", "SUGAR CUBE", "MILK", "LEMON", "STEEP", "INFUSER", "BISCUITS", "CRUMPET", "JASMINE", "MINT"],
    "Classic Cars": ["MUSTANG", "CORVETTE", "THUNDERBIRD", "CADILLAC", "BEETLE", "CONVERTIBLE", "COUPE", "SEDAN", "CHROME", "TAILFIN", "HUBCAP", "BUMPER", "ENGINE", "PISTON", "CARBURETOR", "HEADLIGHT", "STEERING", "DRIVE IN", "ROADSTER", "WAGON", "TRUNK", "GARAGE"],
    "Butterflies and Bugs": ["MONARCH", "SWALLOWTAIL", "LADYBUG", "DRAGONFLY", "BUMBLEBEE", "CRICKET", "FIREFLY", "GRASSHOPPER", "BEETLE", "CATERPILLAR", "COCOON", "MOTH", "ANT", "CICADA", "KATYDID", "WINGS", "ANTENNAE", "NECTAR", "POLLEN", "CHRYSALIS", "HONEYBEE", "MANTIS"],
    "At the Library": ["BOOK", "AUTHOR", "LIBRARIAN", "SHELF", "NOVEL", "POETRY", "MYSTERY", "BIOGRAPHY", "ATLAS", "DICTIONARY", "CATALOG", "BOOKMARK", "CHAPTER", "INDEX", "QUIET", "READING", "FICTION", "HISTORY", "JOURNAL", "PAGES", "LIBRARY CARD", "STORYTIME"],
    "Rivers of the World": ["NILE", "AMAZON", "YANGTZE", "MISSISSIPPI", "DANUBE", "RHINE", "THAMES", "SEINE", "GANGES", "VOLGA", "MEKONG", "CONGO", "TIGRIS", "EUPHRATES", "COLORADO", "HUDSON", "OHIO", "YUKON", "ZAMBEZI", "INDUS", "ORINOCO", "TAGUS"],
    "Sweet Treats": ["CHOCOLATE", "FUDGE", "CARAMEL", "TOFFEE", "BROWNIE", "CUPCAKE", "DONUT", "ECLAIR", "MACARON", "TRUFFLE", "LOLLIPOP", "MARSHMALLOW", "COBBLER", "PUDDING", "CHEESECAKE", "SUNDAE", "SHORTBREAD", "TAFFY", "LICORICE", "MERINGUE", "PRALINE", "GUMDROP"],
    "Camping Out": ["TENT", "SLEEPING BAG", "LANTERN", "CAMPFIRE", "SMORES", "FLASHLIGHT", "HIKING", "TRAIL", "COMPASS", "CANTEEN", "BACKPACK", "KINDLING", "MARSHMALLOW", "STARS", "OWL", "PINE CONE", "COOLER", "CABIN", "RANGER", "TARP", "MOSQUITO", "WILDERNESS"],
    "Famous Composers": ["MOZART", "BEETHOVEN", "BACH", "CHOPIN", "HANDEL", "HAYDN", "VIVALDI", "BRAHMS", "SCHUBERT", "WAGNER", "VERDI", "PUCCINI", "TCHAIKOVSKY", "DEBUSSY", "RAVEL", "LISZT", "MAHLER", "DVORAK", "GERSHWIN", "COPLAND", "ELGAR", "GRIEG"],
    "Flowers in Bloom": ["ORCHID", "LILY", "IRIS", "POPPY", "VIOLET", "ZINNIA", "DAHLIA", "ASTER", "CARNATION", "GARDENIA", "HYDRANGEA", "AZALEA", "BEGONIA", "PETUNIA", "GERANIUM", "JASMINE", "LOTUS", "CAMELLIA", "SNAPDRAGON", "FOXGLOVE", "HIBISCUS", "BLUEBELL"],
    "Mountains and Valleys": ["SUMMIT", "PEAK", "RIDGE", "CANYON", "VALLEY", "GORGE", "CLIFF", "MESA", "PLATEAU", "GLACIER", "BOULDER", "FOOTHILLS", "TIMBERLINE", "AVALANCHE", "ALPINE", "CREVASSE", "VOLCANO", "SLOPE", "TRAILHEAD", "MEADOW", "WATERFALL", "BASIN"],
}
