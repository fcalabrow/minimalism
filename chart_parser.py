from derivations import *
from structures import *
import copy

lexicon = Lexicon()
counter = 0
ug = UniversalGrammar(set(), set(), set())
i_lang = ILanguage(lexicon, ug)
derivation = Derivation(i_lang, word_list=list(i_lang.lexicon.lex))

#Initialize the chart to the empty set of items and the agenda to the axioms
#of the deduction system.
agenda = set(derivation.stages[0].lexical_array.the_list)
chart = set()
last_index = len(agenda)
# Select an item from the agenda, called the trigger item, and remove it.
while len(agenda) > 0:
    trigger = agenda.pop()
# Add the trigger item to the chart, if necessary.
    if trigger not in chart:
        chart.add(trigger)
# If the trigger item was added to the chart, generate all items that are
# new immediate consequences of the trigger item together with all items
# in the chart, and add these generated items to the agenda.
        for item in chart - {trigger}:
            try:
                new_so = trigger.merge(item, last_index)
                agenda.add(new_so)
                last_index += 1
            except Exception as e:
                try:
                    new_so = item.merge(trigger, last_index)
                    agenda.add(new_so)
                    last_index += 1
                except Exception as e:
                    continue
#If a goal item is in the chart, the goal is proved (and the string recognized);
#otherwise it is not
goal_item = 'C'

def iterate(so, phase):
    for daughter in so.syntactic_object_set:
        if isinstance(daughter, LexicalItemToken):
            print(daughter)
            print(daughter.is_final(phase))
        elif isinstance(daughter, SyntacticObjectSet):
            iterate(daughter, phase)
        # print('Successfull parsing')
        # tr = tree(item)
        # tr.pretty_print()
        # break    
for item in chart:
    if isinstance(item, SyntacticObjectSet):
        if len(item.triggers) == 0 and item.category.label == goal_item:
            tr = tree(item)
            tr.pretty_print()
            string = copy.copy(item).transfer(phase=item)
            print(string)