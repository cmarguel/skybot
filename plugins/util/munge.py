# -*- coding: utf-8 -*-

def munge(inp, munge_count=0):
    reps = 0


    for n in xrange(len(inp)):
        rep = character_replacements.get(inp[n])
        if rep:
            inp = inp[:n] + unicode(rep) + inp[n + 1:]
            reps += 1
            if reps == munge_count:
                break
    return inp

character_replacements = {
    'a': u'ä',
    #    'b': 'Б',
    'c': u'ċ',
    'd': u'đ',
    'e': u'ë',
    'f': u'ƒ',
    'g': u'ġ',
    'h': u'ħ',
    'i': u'í',
    'j': u'ĵ',
    'k': u'ķ',
    'l': u'ĺ',
    #    'm': 'ṁ',
    'n': u'ñ',
    'o': u'ö',
    'p': u'ρ',
    #    'q': 'ʠ',
    'r': u'ŗ',
    's': u'š',
    't': u'ţ',
    'u': u'ü',
    #    'v': '',
    'w': u'ω',
    'x': u'χ',
    'y': u'ÿ',
    'z': u'ź',
    'A': u'Å',
    'B': u'Β',
    'C': u'Ç',
    'D': u'Ď',
    'E': u'Ē',
    #    'F': 'Ḟ',
    'G': u'Ġ',
    'H': u'Ħ',
    'I': u'Í',
    'J': u'Ĵ',
    'K': u'Ķ',
    'L': u'Ĺ',
    'M': u'Μ',
    'N': u'Ν',
    'O': u'Ö',
    'P': u'Р',
    #    'Q': 'Ｑ',
    'R': u'Ŗ',
    'S': u'Š',
    'T': u'Ţ',
    'U': u'Ů',
    #    'V': 'Ṿ',
    'W': u'Ŵ',
    'X': u'Χ',
    'Y': u'Ỳ',
    'Z': u'Ż'}