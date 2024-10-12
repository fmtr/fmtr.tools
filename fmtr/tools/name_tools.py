import random
from functools import lru_cache
from typing import Tuple


@lru_cache
def get_left():
    return [
        "admiring",
        "adoring",
        "affectionate",
        "agitated",
        "amazing",
        "angry",
        "awesome",
        "beautiful",
        "blissful",
        "bold",
        "boring",
        "brave",
        "busy",
        "charming",
        "clever",
        "compassionate",
        "competent",
        "condescending",
        "confident",
        "cool",
        "cranky",
        "crazy",
        "dazzling",
        "determined",
        "distracted",
        "dreamy",
        "eager",
        "ecstatic",
        "elastic",
        "elated",
        "elegant",
        "eloquent",
        "epic",
        "exciting",
        "fervent",
        "festive",
        "flamboyant",
        "focused",
        "friendly",
        "frosty",
        "funny",
        "gallant",
        "gifted",
        "goofy",
        "gracious",
        "great",
        "happy",
        "hardcore",
        "heuristic",
        "hopeful",
        "hungry",
        "infallible",
        "inspiring",
        "intelligent",
        "interesting",
        "jolly",
        "jovial",
        "keen",
        "kind",
        "laughing",
        "loving",
        "lucid",
        "magical",
        "modest",
        "musing",
        "mystifying",
        "naughty",
        "nervous",
        "nice",
        "nifty",
        "nostalgic",
        "objective",
        "optimistic",
        "peaceful",
        "pedantic",
        "pensive",
        "practical",
        "priceless",
        "quirky",
        "quizzical",
        "recursing",
        "relaxed",
        "reverent",
        "romantic",
        "sad",
        "serene",
        "sharp",
        "silly",
        "sleepy",
        "stoic",
        "strange",
        "stupefied",
        "suspicious",
        "sweet",
        "tender",
        "thirsty",
        "trusting",
        "unruffled",
        "upbeat",
        "vibrant",
        "vigilant",
        "vigorous",
        "wizardly",
        "wonderful",
        "xenodochial",
        "youthful",
        "zealous",
        "zen",
        "altruistic",
        "bewildered",
        "candid",
        "captivating",
        "chivalrous",
        "comical",
        "dashing",
        "dynamic",
        "eclectic",
        "effervescent",
        "exuberant",
        "fascinating",
        "frisky",
        "gleeful",
        "gregarious",
        "hilarious",
        "incisive",
        "innovative",
        "jubilant",
        "kaleidoscopic",
        "lively",
        "magnetic",
        "mesmerizing",
        "mirthful",
        "noble",
        "observant",
        "passionate",
        "playful",
        "profound",
        "radiant",
        "resilient",
        "sensational",
        "spirited",
        "tantalizing",
        "thoughtful",
        "unassuming",
        "vivacious",
        "whimsical",
        "winsome",
        "zesty"
    ]


@lru_cache
def get_right():
    return [
        'agah',
        'angelides',
        'appleyard',
        'arguelles',
        'barbee',
        'berra',
        'biebel',
        'bird',
        'boulala',
        'bowman',
        'boyle',
        'brenes',
        'cales',
        'campbell',
        'cardiel',
        'carroll',
        'castillo',
        'chalmers',
        'channita',
        'childress',
        'conklin',
        'creager',
        'dill',
        'duffy',
        'duren',
        'dyani',
        'dyrdek',
        'ellington',
        'fabry',
        'ferguson',
        'foster',
        'fowler',
        'frazier',
        'gall',
        'gayle',
        'glifberg',
        'gonzales',
        'greathouse',
        'hawk',
        'hendrix',
        'hensley',
        'hosoi',
        'howell',
        'hufnagel',
        'iannucci',
        'itkonen',
        'janoski',
        'johnson',
        'johnston',
        'jones',
        'kalis',
        'kennedy',
        'kirk',
        'koston',
        'lee',
        'lieu',
        'maldonado',
        'mandoli',
        'mangum',
        'manzoori',
        'mariano',
        'markovich',
        'mayhew',
        'mcbride',
        'mccrank',
        'mcdonald',
        'mckay',
        'milton',
        'montoya',
        'mountain',
        'mulder',
        'mullen',
        'mumford',
        'muska',
        'pappalardo',
        'pappas',
        'pastras',
        'penny',
        'pepper',
        'ponte',
        'randle',
        'richter',
        'rodriguez',
        'rothmeyer',
        'rowley',
        'roy',
        'saari',
        'salabanzi',
        'sanchez',
        'santarossa',
        'santos',
        'schaaf',
        'senn',
        'shao',
        'sheffey',
        'shipman',
        'song',
        'speyer',
        'staba',
        'stone',
        'stranger',
        'suriel',
        'teixeira',
        'templeton',
        'thomas',
        'tsocheff',
        'turner',
        'umali',
        'wainwright',
        'way',
        'welsh',
        'whaley',
        'wilson',
        'woodstock',
        'wray',
        'york',
        'zipp',
        'zitzer'
    ]


def get(sep: str | None = '-') -> str | Tuple[str, str]:
    """

    Get a random memorable name

    """
    left_right = random.choice(get_left()), random.choice(get_right())
    if not sep:
        return left_right
    text = sep.join(left_right)
    return text
