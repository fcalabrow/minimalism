from derivations import *
from structures import *

# def main():
#     lexicon = Lexicon()
#     counter = 0
#     ug = UniversalGrammar(set(), set(), set()) # todo: add feature import to UG
#     i_lang = ILanguage(lexicon, ug)
#     derivation = Derivation(i_lang, word_list=list(i_lang.lexicon.lex))
#     derivation.derive()

def main():
    while True:
        sentence = input("Insert a sentence to parse or press (f) to finish: ")
        if sentence != 'f':
            try:
                parse(sentence)
            except AssertionError:
                print("Some words are not in the lexicon")
        else:
            break

main()