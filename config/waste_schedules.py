# Waste collection schedule for Calvenzano 2026
WASTE_SCHEDULE = {
    "CARTA E CARTONE": {  # Paper and cardboard - every other Saturday
        1: [3, 17, 31],
        2: [14, 28],
        3: [14, 28],
        4: [11, 27],  # Note: April 27 is Monday
        5: [9, 23],
        6: [6, 20],
        7: [4, 18],
        8: [1, 17, 29],  # Note: August 17 is Monday
        9: [12, 26],
        10: [10, 24],
        11: [7, 21],
        12: [5, 19],
    },
    "INDIFFERENZIATO": {  # Non-recyclable waste - every Wednesday
        1: [7, 14, 21, 28],
        2: [4, 11, 18, 25],
        3: [4, 11, 18, 25],
        4: [1, 8, 15, 22, 29],
        5: [6, 13, 20, 27],
        6: [3, 10, 17, 24],
        7: [1, 8, 15, 22, 29],
        8: [5, 12, 19, 26],
        9: [2, 9, 16, 23, 30],
        10: [7, 14, 21, 28],
        11: [4, 11, 18, 25],
        12: [2, 9, 16, 23, 30],
    },
    "ORGANICO": {  # Organic waste - every Saturday, twice a week in summer
        1: [3, 10, 17, 24, 31],
        2: [7, 14, 21, 28],
        3: [7, 14, 21, 28],
        4: [4, 11, 18, 25],
        5: [2, 9, 16, 23, 30],
        6: [3, 6, 10, 13, 17, 20, 24, 27],  # Wednesday and Saturday in summer
        7: [1, 4, 8, 11, 15, 18, 22, 25, 29],  # Wednesday and Saturday in summer
        8: [1, 5, 8, 12, 17, 19, 22, 26, 29],  # Note: August 17 is Monday
        9: [2, 5, 9, 12, 16, 19, 23, 26, 30],  # Wednesday and Saturday in summer
        10: [3, 10, 17, 24, 31],
        11: [7, 14, 21, 28],
        12: [5, 12, 19, 26],
    },
    "PLASTICA": {  # Plastic - every Saturday
        1: [3, 10, 17, 24, 31],
        2: [7, 14, 21, 28],
        3: [7, 14, 21, 28],
        4: [4, 11, 18, 24],  # Note: April 24 is Friday
        5: [2, 9, 16, 23, 30],
        6: [6, 13, 20, 27],
        7: [4, 11, 18, 25],
        8: [1, 8, 14, 22, 29],  # Note: August 14 is Friday
        9: [5, 12, 19, 26],
        10: [3, 10, 17, 24, 31],
        11: [7, 14, 21, 28],
        12: [5, 12, 19, 29],  # Note: December 29 is Tuesday
    },
    "VETRO E BARATTOLAME": {  # Glass and cans - every Friday
        1: [2, 9, 16, 23, 30],
        2: [6, 13, 20, 27],
        3: [6, 13, 20, 27],
        4: [3, 10, 17, 24, 30],  # Note: April 30 is Thursday
        5: [8, 15, 22, 29],
        6: [5, 12, 19, 26],
        7: [3, 10, 17, 24, 31],
        8: [7, 14, 21, 28],
        9: [4, 11, 18, 25],
        10: [2, 9, 16, 23, 30],
        11: [6, 13, 20, 27],
        12: [4, 11, 18, 23, 31],  # Note: Dec 23 is Wed, Dec 31 is Thu
    },
}

# Waste disposal instructions
WASTE_INSTRUCTIONS = {
    "CARTA E CARTONE": "📦 Conferire in scatole o sacchi di CARTA. Non utilizzare sacchi in plastica.",
    "INDIFFERENZIATO": "🗑️ Conferire negli appositi sacchi trasparenti.",
    "ORGANICO": "🥕 Conferire racchiuso negli appositi sacchetti di MATER-BI (amido di mais), nei bidoni forniti.",
    "PLASTICA": "♻️ Conferire negli appositi contenitori forniti dall'Amministrazione Comunale.",
    "VETRO E BARATTOLAME": "🍾 Conferire negli appositi bidoni forniti dall'Amministrazione comunale.",
}

# Emoji for waste types
WASTE_EMOJI = {
    "CARTA E CARTONE": "📦",
    "INDIFFERENZIATO": "🗑️",
    "ORGANICO": "🥕",
    "PLASTICA": "♻️",
    "VETRO E BARATTOLAME": "🍾",
}

# Italian month names
MONTH_NAMES = {
    1: "Gennaio",
    2: "Febbraio",
    3: "Marzo",
    4: "Aprile",
    5: "Maggio",
    6: "Giugno",
    7: "Luglio",
    8: "Agosto",
    9: "Settembre",
    10: "Ottobre",
    11: "Novembre",
    12: "Dicembre",
}

# Italian day names
DAY_NAMES = {
    0: "Lunedì",
    1: "Martedì",
    2: "Mercoledì",
    3: "Giovedì",
    4: "Venerdì",
    5: "Sabato",
    6: "Domenica",
}
