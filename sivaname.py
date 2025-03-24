from indic_transliteration import sanscript, detect
from indic_transliteration.sanscript import transliterate

file_name = 'sivanames.txt'

def check_siva_name(name, number):
    if detect.detect(name) == sanscript.DEVANAGARI:
        name = transliterate(name, sanscript.DEVANAGARI, sanscript.IAST)
    elif detect.detect(name) == sanscript.ITRANS:
        name = transliterate(name, sanscript.ITRANS, sanscript.IAST)
    elif detect.detect(name) == sanscript.HK:
        name = transliterate(name, sanscript.HK, sanscript.IAST)
    
    with open(file_name) as fp:
        lines = fp.readlines()
        sivaname = lines[number - 1]
        for n in name.split(' '):
            if sivaname == n or (len(n) >= 4 and n[:4] == sivaname[:4]):
                return True

    return False