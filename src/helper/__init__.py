from .logger import logger

def convertCentsToString(cents: int) -> str:
    vorzeichen = "- " if cents < 0 else ""
    cents = abs(cents)
    vorKomma = "0" if cents < 99 else str(cents // 100)
    nachKomma = str(cents % 100).zfill(2)
    return vorzeichen + vorKomma + "," + nachKomma + " €"
