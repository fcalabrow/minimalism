from typing import *
from derivations import *
from structures import *
from structures.features import Trigger_Feature
from parser.utils import normalize
import copy
import traceback

class Parser():
    def __init__(self, derivation: Derivation, goal_item_label:str = 'C', func_phon_label:str = 'none'):
        self.vocabulary = derivation.stages[0].lexical_array.the_list
        self.goal_item_label = goal_item_label
        self.func_phon_label = func_phon_label

    def parse(self, sentence: str, step_view = False):
        sentence = normalize(sentence)
        lexical_items = {item for item in self.vocabulary if list(item.lexical_item.phon)[0].label in sentence.lower().strip().split(' ')}
        functional_items = {item for item in self.vocabulary if list(item.lexical_item.phon)[0].label == self.func_phon_label and [syn.label for syn in list(item.lexical_item.syn) if isinstance(syn, Trigger_Feature)][0] in [syn.label for item in self.vocabulary for syn in item.lexical_item.syn if isinstance(syn,Cat_Feature)]}
        self.agenda = Agenda(lexical_items.union(functional_items))
        self.chart = Chart()
        last_index = len(self.agenda)
        step = 0

        while len(self.agenda) > 0:
            if step_view:
                print('Step {}'.format(step))
                print(self.agenda)
                print(self.chart)
            trigger = self.agenda.pop()
        # Add the trigger item to the chart, if necessary.
            if trigger not in self.chart:
                self.chart.add(trigger)
        # If the trigger item was added to the chart, generate all items that are
        # new immediate consequences of the trigger item together with all items
        # in the chart, and add these generated items to the agenda.
                for item in self.chart - {trigger}:
                    try:
                        new_so = trigger.merge(item, last_index)
                        self.agenda.add(new_so)
                        last_index += 1
                        ### Remove merged LI and add a copy with a new index to the chart 
                        try:
                            if isinstance(trigger,LexicalItemToken):
                                new_trigger = copy.copy(trigger)
                                new_trigger.idx = last_index
                                self.chart.add(new_trigger)
                                try:
                                    self.chart.remove(trigger)
                                except Exception:
                                    print(trigger)
                                    print(self.chart)
                                    print(traceback.format_exc())
                                last_index += 1
                                trigger = new_trigger
                        except Exception:
                            print(traceback.format_exc())
                        ###
                    except Exception:
                        try:
                            new_so = item.merge(trigger, last_index)
                            self.agenda.add(new_so)
                            last_index += 1
                            ###
                            try:
                                if isinstance(item,LexicalItemToken):
                                    new_item = copy.copy(item)
                                    new_item.idx = last_index
                                    self.chart.add(new_item)
                                    try:
                                        self.chart.remove(item)
                                    except Exception:
                                        print(item)
                                        print(self.chart)
                                        print(traceback.format_exc())
                                    last_index += 1
                                    item = new_item
                            except Exception:
                                print(traceback.format_exc())
                            ###
                        except Exception:
                            continue
            step += 1
        #If a goal item is in the chart, the goal is proved (and the string recognized);
        #otherwise it is not
        if step_view:
            print('')
            print('Aplying Transfer...')
            print('')
        successfull_parses = 0
        for item in self.chart:
            if isinstance(item, SyntacticObjectSet):
                if len(item.triggers) == 0 and item.category.label == self.goal_item_label:
                    transferred = copy.copy(item).transfer(self.func_phon_label)
                    if sentence == transferred:
                        successfull_parses += 1
                        print('PARSE {}:'.format(successfull_parses))
                        tr = tree(item)
                        tr.pretty_print()
        if successfull_parses == 0:
            print('Sentence is not derivable.')

class Agenda(set):
    def __init__(self, axioms:list):
        for axiom in axioms:
            self.add(axiom)
    
    def __str__(self):
        print('')
        print("{} item{} in the agenda:".format(len(self),'s' if len(self) > 1 and len(self) != 0 else ''))
        print('')
        for item in self:
            tr = tree(item)
            tr.pretty_print()
        return('')

class Chart(set):
    def __init__(self):
        pass
    
    def __str__(self):
        print('')
        print("{} item{} in the chart:".format(len(self),'s' if len(self) > 1 and len(self) != 0 else ''))
        print('')
        for item in self:
            tr = tree(item)
            tr.pretty_print()
        return('')
