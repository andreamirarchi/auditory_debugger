# auditory_debugger/sound_bank.py

ERROR_SOUNDS = {

    ZeroDivisionError: [
        (220,500),
        (180,600),
        (140,900)
    ],

    TypeError: [
        (400,400),
        (650,400),
        (300,400)
    ],

    ValueError: [
        (550,600),
        (550,600)
    ],

    IndexError: [
        (700,300),
        (750,300)
    ],

    KeyError: [
        (650,400),
        (500,900)
    ],

    AttributeError: [
        (300,500),
        (800,500),
        (250,800)
    ],

    RecursionError: [
        (200,500),
        (250,500),
        (300,700)
    ]

}

EVENT_SOUNDS = {

    "UI_FREEZE": [
        (150,800),
        (120,800)
    ],

    "MAIN_THREAD_BLOCK": [
        (180,1000)
    ],

    "EVENT_LOOP_STORM": [
        (400,300),
        (600,300),
        (700,400)
    ],

    "WIDGET_LOST": [
        (500,600),
        (300,500)
    ],

    "RENDER_FAILURE": [
        (700,400),
        (800,500)
    ],

    "SLOW_UI": [
        (250,1200)
    ],

    "slow": [
        (250,1200),
        (200,800)
    ],

    "burst": [
        (900,120),
        (900,120),
        (700,300)
    ],

    "exit": [
        (600,180),
        (400,120)
    ]

}


DYNAMIC_SOUNDS = {

    "enter": lambda value: [
        (400 + value*40,220),
        (600 + value*40,220)
    ]

}