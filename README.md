# Bachelor
Praktischer Anteil meiner Bachelorarbeit
Um das Framework nutzen zu können, muss das Data2Text Modell https://github.com/gongliym/data2text-transformer/ heruntergeladen werden.
Das Starten von Framework.py ermöglicht die Datenvorverarbeitung in einem Schritt, da es intern die benötigten Scripte mit den gegebenen Parametern ausführt.
Damit können Daten die der newformat.json Struktur folgen verwendet werden.

[
  {
    "non_entity_records": {
      "weather": "sunny",
      "date": "02.19.2021"
    },
    "entity_records": {
      "entity_0": {
        "identifier": "0",
        "group": "0",
        "features": "one",
        "name": "Klaus"
      },
      "entity_1": {
        "identifier": "1",
        "group": ["0", "1"],
        "features": ["more", "than", "one", "feature"],
        "name": "Dave"
      }
    },
    "group_records": {
      "group_0": {
        "identifier": "0",
        "name": "Gruppe 1",
        "features": "Gewinner"
      },
      "group_2": {
        "identifier": "1",
        "name": "Leipzig",
        "features": ["Stadt", "Kreis"]
      }
    },
    "summary": ["Tokenized", "summary", "about", "the", "entities", "and", "groups"]
  },
  {
    ...
  }
]
