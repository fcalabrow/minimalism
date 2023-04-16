from derivations import *
from structures import *
from parser.chart_parser import Parser
from parser.utils import *
import os

def manual_derivation(filename='lexicon.xml'):
    lexicon = Lexicon(filename)
    ug = UniversalGrammar(set(), set(), set()) # todo: add feature import to UG
    i_lang = ILanguage(lexicon, ug)
    derivation = Derivation(i_lang, word_list=list(i_lang.lexicon.lex))
    derivation.derive()

def main():
    filename = 'lexicon.xml'
    step_view = False
    enable = 'Enable'
    while True:
        new_line = "\n"
        user_input = input(f'Select an option and press enter:{new_line*2}1 - Parser{new_line}2 - Manual derivation{new_line}3 - Change grammar{new_line}4 - {enable} step-by-step view when parsing{new_line}5 - Quit{new_line*2}')
        if user_input == '1':
            sentence = input(f'{new_line}Insert a sentence to parse:{new_line*2}')
            try:
                lexicon = Lexicon(filename=filename)
                ug = UniversalGrammar(set(), set(), set())
                i_lang = ILanguage(lexicon, ug)
                derivation = Derivation(i_lang, word_list=list(i_lang.lexicon.lex))
                parser = Parser(derivation)
                parser.parse(sentence, step_view)
            except AssertionError:
                print(f"{new_line}[ERROR] Some words are not in the lexicon{new_line}")
        elif user_input == '2':
            manual_derivation(filename)
        elif user_input == '3':
            while True:
                indexes = print_grammars(filename)
                file_index = input(f'Select the index of the new grammar:{new_line}')
                try:
                    filename = indexes[int(file_index)]
                    break
                except:
                    print(f'{new_line}[ERROR] Insert a valid option{new_line}')
        elif user_input == '4':
            step_view = not step_view
            if step_view == False:
                enable = "Enable"
            else:
                enable = 'Disable'
        elif user_input == '5':
            break
        else:
            print('Select a valid option (1-4)')

if __name__ == '__main__':
    main()