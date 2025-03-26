# Waste collection schedule for Calvenzano 2025
WASTE_SCHEDULE = {
    "CARTA E CARTONE": {  # Paper and cardboard - every other Saturday
        1: [4, 18],
        2: [1, 15],
        3: [1, 15, 29],
        4: [12, 26],
        5: [10, 24],
        6: [7, 21],
        7: [5, 19],
        8: [2, 16, 30],
        9: [13, 27],
        10: [11, 25],
        11: [8, 22],
        12: [6, 20]
    },
    "INDIFFERENZIATO": {  # Non-recyclable waste - every Wednesday
        1: [2, 8, 15, 22, 29],  # Note: January 2 is Thursday
        2: [5, 12, 19, 26],
        3: [5, 12, 19, 26],
        4: [2, 9, 16, 23, 30],
        5: [7, 14, 21, 28],
        6: [4, 11, 18, 25],
        7: [2, 9, 16, 23, 30],
        8: [6, 13, 20, 27],
        9: [3, 10, 17, 24],
        10: [1, 8, 15, 22, 29],
        11: [5, 12, 19, 26],
        12: [3, 10, 17, 24, 31]
    },
    "ORGANICO": {  # Organic waste - every Saturday, twice a week in summer
        1: [4, 11, 18, 25],
        2: [1, 8, 15, 22],
        3: [1, 8, 15, 22, 29],
        4: [5, 12, 19, 26],
        5: [3, 10, 17, 24, 31],
        6: [4, 7, 11, 14, 18, 21, 25, 28],  # Wednesday and Saturday in summer
        7: [2, 5, 9, 12, 16, 19, 23, 26, 30],  # Wednesday and Saturday in summer
        8: [2, 6, 9, 13, 16, 20, 23, 27, 30],  # Wednesday and Saturday in summer
        9: [3, 6, 10, 13, 17, 20, 24, 27],  # Wednesday and Saturday in summer
        10: [4, 11, 18, 25],
        11: [3, 8, 15, 22, 29],  # Note: November 3 is Monday
        12: [6, 13, 20, 27]
    },
    "PLASTICA": {  # Plastic - every Saturday
        1: [4, 11, 18, 25],
        2: [1, 8, 15, 22],
        3: [1, 8, 15, 22, 29],
        4: [5, 12, 19, 26],
        5: [3, 10, 17, 24, 31],
        6: [7, 14, 21, 28],
        7: [5, 12, 19, 26],
        8: [2, 9, 16, 23, 30],
        9: [6, 13, 20, 27],
        10: [4, 11, 18, 25],
        11: [4, 8, 15, 22, 29],  # Note: November 4 is Tuesday
        12: [6, 13, 20, 27]
    },
    "VETRO E BARATTOLAME": {  # Glass and cans - every Friday
        1: [3, 10, 17, 24, 31],
        2: [7, 14, 21, 28],
        3: [7, 14, 21, 28],
        4: [4, 11, 18, 25],
        5: [2, 9, 16, 23, 30],
        6: [6, 13, 20, 27],
        7: [4, 11, 18, 25],
        8: [1, 8, 16, 22, 29],  # Note: August 16 is Saturday
        9: [5, 12, 19, 26],
        10: [3, 10, 17, 24, 31],
        11: [7, 14, 21, 28],
        12: [5, 12, 19, 26]
    },
    "TESSILI E INDUMENTI": {  # Textiles and clothing - last Thursday of each month
        1: [30],
        2: [27],
        3: [27],
        4: [24],
        5: [29],
        6: [26],
        7: [31],
        8: [28],
        9: [25],
        10: [30],
        11: [27],
        12: [25]  # Actually the last Thursday is January 1, 2026
    }
}

# Waste disposal instructions
WASTE_INSTRUCTIONS = {
    "CARTA E CARTONE": "📦 Conferire in scatole o sacchi di CARTA. Non utilizzare sacchi in plastica.",
    "INDIFFERENZIATO": "🗑️ Conferire negli appositi sacchi trasparenti.",
    "ORGANICO": "🥕 Conferire racchiuso negli appositi sacchetti di MATER-BI (amido di mais), nei bidoni forniti.",
    "PLASTICA": "♻️ Conferire negli appositi contenitori forniti dall'Amministrazione Comunale.",
    "VETRO E BARATTOLAME": "🍾 Conferire negli appositi bidoni forniti dall'Amministrazione comunale.",
    "TESSILI E INDUMENTI": "👕 Segnalare via e n. civico chiamando o mandando un WhatsApp al 324 150 8217. In alternativa, utilizzare il cassone presso il centro di raccolta."
}

# Emoji for waste types
WASTE_EMOJI = {
    "CARTA E CARTONE": "📦",
    "INDIFFERENZIATO": "🗑️",
    "ORGANICO": "🥕",
    "PLASTICA": "♻️",
    "VETRO E BARATTOLAME": "🍾",
    "TESSILI E INDUMENTI": "👕"
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
    12: "Dicembre"
}

# Italian day names
DAY_NAMES = {
    0: "Lunedì",
    1: "Martedì",
    2: "Mercoledì",
    3: "Giovedì",
    4: "Venerdì",
    5: "Sabato",
    6: "Domenica"
}
