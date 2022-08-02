from derivations import *
from structures import *
import os

filename = "lexicon.xml"

def print_grammars():
    global filename
    full_path = os.path.abspath("data")
    print(full_path)
    filenames = [f for f in os.listdir(full_path) if os.path.isfile(os.path.join(full_path, f))]
    for f in filenames:
        if f == filename:
            filenames.pop(filenames.index(f))
            filenames.insert(0, f)
    indexes = {i:f for i,f in enumerate(filenames)}
    print(f'{len(indexes)} grammar(s) found: ')
    for key,value in indexes.items():
        if key == 0:
            print(f"{key}: '{value}' (current)")
        else:
            print(f"{key}: '{value}'")
    return indexes

def manual_derivation(filename=filename):
    lexicon = Lexicon(filename)
    counter = 0
    ug = UniversalGrammar(set(), set(), set()) # todo: add feature import to UG
    i_lang = ILanguage(lexicon, ug)
    derivation = Derivation(i_lang, word_list=list(i_lang.lexicon.lex))
    derivation.derive()

def main():
    global filename
    debug = False
    enable = 'Enable'
    while True:
        new_line = "\n"
        user_input = input(f'Select an option and press enter:{new_line*2}1 - Parser{new_line}2 - Manual derivation{new_line}3 - Change default grammar{new_line}4 - {enable} stage-by-stage view{new_line}5 - Quit{new_line*2}')
        if user_input == '1':
            sentence = input(f'{new_line}Insert a sentence to parse:{new_line*2}')
            try:
                parse(sentence,filename,debug)
            except AssertionError:
                print(f"{new_line}[ERROR] Some words are not in the lexicon{new_line}")
        elif user_input == '2':
            manual_derivation(filename)
        elif user_input == '3':
            while True:
                indexes = print_grammars()
                file_index = input(f'Select the index of the new grammar:{new_line}')
                try:
                    filename = indexes[int(file_index)]
                    break
                except:
                    print(f'{new_line}[ERROR] Insert a valid option{new_line}')
        elif user_input == '4':
            debug = not debug
            if debug == False:
                enable = "Enable"
            else:
                enable = 'Disable'
        elif user_input == '5':
            break
        else:
            print('Select a valid option (1-4)')

main()