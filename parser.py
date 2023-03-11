from derivations import *
from structures import *

lexicon = Lexicon()
counter = 0
ug = UniversalGrammar(set(), set(), set()) # todo: add feature import to UG
i_lang = ILanguage(lexicon, ug)
derivation = Derivation(i_lang, word_list=list(i_lang.lexicon.lex))

# derivation tiene stages con un workspace con un syntactic object w

#Initialize the chart to the empty set of items and the agenda to the axioms
#of the deduction system.
agenda = set(derivation.stages[0].lexical_array.the_list)
chart = set()
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
                new_so = trigger.merge(item, len(chart))
                agenda.add(new_so)
            except Exception as e:
                try:
                    new_so = item.merge(trigger, len(chart))
                    agenda.add(new_so)
                except Exception as e:
                    continue
#If a goal item is in the chart, the goal is proved (and the string recognized);
#otherwise it is not
goal_item = 'C'

for item in chart:
    if item.category.label == goal_item:
        print('Successfull parsing')
        tr = tree(item)
        tr.pretty_print()
        break    