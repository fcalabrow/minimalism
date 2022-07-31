import re
from structures import *
from derivations import derivation

class Derivation(derivation.Derivation):
    
    successfull_derivation = None
    sentence_to_parse = ''
    transferred_sentence = []

    def transfer(self,so):
        list_from_set = list(so.syntactic_object_set)
        x,y = list_from_set[0],list_from_set[1]
        W = list(self.stages[-1].workspace.w)[0]
        
        empty_li = LexicalItem({Cat_Feature('E')},{Sem_Feature('')},{Phon_Feature("")})
        self.i_lang.lexicon.lex.add(empty_li)
        empty_so = LexicalItemToken(empty_li,0)
        if x.is_final(y,W) == False:
            x = empty_so
        if y.is_final(x,W) == False:
            y = empty_so

        if isinstance(x,LexicalItemToken) and isinstance(y,LexicalItemToken):
            if len(x.triggers) != 0: # if head
                self.transferred_sentence.append(list(x.lexical_item.phon)[0].label)
                self.transferred_sentence.append(list(y.lexical_item.phon)[0].label)
            else: # if complement
                self.transferred_sentence.append(list(y.lexical_item.phon)[0].label)
                self.transferred_sentence.append(list(x.lexical_item.phon)[0].label)
        elif isinstance(x,SyntacticObjectSet) and isinstance(y,SyntacticObjectSet):
            if len(x.triggers) != 0: # if head
                self.transfer(y)
                self.transfer(x)
            else: # if specifier
                self.transfer(x)
                self.transfer(y)
        else:
            if isinstance(x,LexicalItemToken) and isinstance(y,SyntacticObjectSet):
                self.transferred_sentence.append(list(x.lexical_item.phon)[0].label)
                self.transfer(y)
            elif isinstance(y,LexicalItemToken) and isinstance(x,SyntacticObjectSet):
                self.transferred_sentence.append(list(y.lexical_item.phon)[0].label)
                self.transfer(x)

    def autotf(self, index, debug = False):
        if debug == True:
                self.print_derivation()
        x = self.stages[-1].workspace.find_workspace(index) # get x
        triggers = [trigger for trigger in x.triggers]
        trigger_labels = [trigger.label for trigger in triggers]
        
        # Rule 1 - Successful derivation
        if len(x.triggers) == 0 and len(self.stages[-1].workspace.w) == 1 and len(self.stages[-1].lexical_array.the_list) == 0:
            if debug == True:
                print('Aplying transfer')
            self.transferred_sentence = []
            self.transfer(x)
            self.transferred_sentence = [word for word in self.transferred_sentence if word != '' and not word.startswith('[')]
            self.transferred_sentence = ' '.join(self.transferred_sentence)
            if debug == True:
                print('Transferred sentence:',self.transferred_sentence)
            if self.transferred_sentence == self.sentence_to_parse:
                if debug == True:
                    self.print_derivation()
                    print("Successfull parsing!")
                    print('')
                self.successfull_derivation = self
                return True
            else:
                return None

        # Rule 2
        if len(triggers) > 1 and len(self.stages[-1].workspace.w) == 1 and len(self.stages[-1].lexical_array.the_list) == 0 and isinstance(x,SyntacticObjectSet):
            return None

        # Rule 3 - Internal merge
        if len(triggers) == 1 and triggers[0].label[-1] == '/' and len(self.stages[-1].workspace.w) == 1 and isinstance(x, SyntacticObjectSet):
            #x.lexical_item.copy_features()
            triggers[0].label = triggers[0].label[0:-1]
            if debug == True:
                print('Aplying rule 3: internal merge (X,Y)')
                print('')
            for y in x.syntactic_object_set:
                if y.category.label == triggers[0].label:
                    self.automerge(index,y.idx, debug=debug)
                    return True
                elif isinstance(y, SyntacticObjectSet):
                    for z in y.syntactic_object_set:
                        if z.category.label == triggers[0].label:
                            y = z
                            self.automerge(index,y.idx,debug=debug)
                            return True
            return None

        # Rule 4 - Select
        if len(self.stages[-1].workspace.w) == 1 and len(self.stages[-1].lexical_array.the_list) > 0:
            if debug == True:
                print('Aplying rule 4: select(Y)')
                print('')
            for li in self.stages[-1].lexical_array.the_list:
                if (list(li.lexical_item.phon)[0]).label.startswith('[') and len(x.triggers) == 0:
                    triggers_fc = [re.sub("/","",trigger.label) for trigger in li.triggers if trigger.label.startswith('/')]
                    if x.category.label in triggers_fc:
                        for trigger in li.triggers:
                            if trigger.label.startswith("/"):
                                trigger.label = re.sub("/","",trigger.label)
                        self.autoselect(li.idx,debug)
                        return True

            list_of_idxs = [y.idx for y in self.stages[-1].lexical_array.the_list]
            self.autoselect(min(list_of_idxs),debug)
            return True

        # Rule 5 - External merge (Y,X)
        if len(triggers) == 0 and len(self.stages[-1].workspace.w) == 2:
            if debug == True:
                print('Aplying rule 5: external merge (Y,X)')
                print('')
            for y in self.stages[-1].workspace.w:
                triggers_y = [trigger.label for trigger in y.triggers]
                if len(triggers_y) > 0 and x.category.label in triggers_y:
                    self.automerge(y.idx,index,debug=debug)
                    return True
                # Rule 7 
            if len(self.stages[-1].lexical_array.the_list) > 0:
                    if debug == True:
                        print('Aplying rule 7: select(Z)')
                        print('')
                    index_z = min([y.idx for y in self.stages[-1].lexical_array.the_list])
                    self.autoselect(index_z,debug)
                    return True
            return None

        # Rule 6 - External merge (X,Y)
        if len(triggers) > 0 and len(self.stages[-1].workspace.w) == 2:
            if debug == True:
                print('Aplying rule 6: external merge (X,Y)')
                print('')
            for y in self.stages[-1].workspace.w:
                if y.category.label in trigger_labels:
                    self.automerge(index,y.idx,debug=debug)
                    return True
            return None

        # Rule 8 - External merge
        if len(x.triggers) > 0 and len(self.stages[-1].workspace.w) == 3:
            if debug == True:
                print('Aplying rule 8: external merge(Z,Y)')
                print('')
            z = self.stages[-1].workspace.find_workspace(index-1)
            if z in self.stages[-1].workspace.w:
                self.automerge(index,index-1,debug=debug)
                return True
            else:
                z_idx = max([so.idx for so in self.stages[-1].workspace.w if so!=x])
                self.automerge(index,z_idx,debug=debug)
                return True
    
    def autoselect(self, index, debug):
        last_stage = self.stages[-1]
        lexical_item_token = last_stage.lexical_array.find_lexical_array(index)
        new_stage = last_stage.select_stage(lexical_item_token)
        self.stages.append(new_stage)
        if self.autotf(index,debug=debug) == None:
             if debug == True:
                print('Derivation failed')
                print('')
             return
    
    def automerge(self, idx1, idx2, debug):
        last_stage = self.stages[-1]
        try:
            new_stage = last_stage.merge_stage(idx1, idx2)
        except InteractionError:
            if debug == True:
                print('Derivation failed')
            return
        self.stages.append(new_stage)
        #print('Stage: ',len(self.stages))
        index = max([x.idx for x in last_stage.workspace.w])
        if self.autotf(index,debug=debug) == None:
             if debug == True:
                print('Derivation failed')
                print('')
             return

    def autoderive(self, sentence, debug):
        self.sentence_to_parse = sentence
        self.autoselect(0, debug)

def word_to_lex(lexicon_list,word):
    """ Matches a word with its lexical items
    Return None if word is not in lexicon """
    lexical_item = None
    for x in lexicon_list:
            if (list(x.phon))[0].label == word:
                lexical_item = x
    return lexical_item

def phrase_to_list(lexicon_list, phrase):
    """ Param: phrase (str)
    Return: list of lexical_item """
    phrase = phrase.split()
    new_list = [word_to_lex(lexicon_list, word) for word in phrase]
    new_list.reverse()
    return new_list

def add_functional_categories(word_list,functional_list):
    words_with_fc = []
    for word in word_list:
        if word == None:
            raise AssertionError
        category = [c.label for c in word.syn if isinstance(c,Cat_Feature)]
        for fcw in functional_list:
            triggers = [re.sub("/","",t.label) for t in fcw.syn if isinstance(t,Trigger_Feature) and t.label.startswith('/')]
            if category[0] in triggers:
                if fcw not in word_list and word not in words_with_fc:
                    word_list.append(fcw)
                    words_with_fc.append(word)
    return word_list

def get_possible_lexicons(lexicon):
    import itertools
    duplicates = []
    for item1 in lexicon.lex:
        phon1 = [ph.label for ph in item1.phon if isinstance(ph,Phon_Feature)][0]
        category1 = [c.label for c in item1.syn if isinstance(c,Cat_Feature)][0]
        for duplicate in duplicates:
            for item3 in duplicate:
                phon3 = [ph.label for ph in item3.phon if isinstance(ph,Phon_Feature)][0]
                category3 = [c.label for c in item3.syn if isinstance(c,Cat_Feature)][0]
                if phon1 == phon3 and phon1 == category3 and item1 not in duplicate:
                    duplicate.append(item1)
                    pass 
        for item2 in lexicon.lex:
            phon2 = [ph.label for ph in item2.phon if isinstance(ph,Phon_Feature)][0]
            category2 = [c.label for c in item2.syn if isinstance(c,Cat_Feature)][0]
            if phon1 == phon2 and category1 == category2 and item1 != item2:
                if not any(item1 in list for list in duplicates):
                    duplicates.append([item1,item2])
    all_fc_possibilities = list(itertools.product(*duplicates))
    lexicon_list = [item for item in lexicon.lex if not any(item in list for list in duplicates)]
    all_possibilities = []
    for possibility in all_fc_possibilities:
        new_list = [item for item in possibility] + [item for item in lexicon_list]
        all_possibilities.append(new_list)
    return all_possibilities

def parse(sentence,filename="lexicon.xml",debug=True):
    sentence = ' '.join(((re.sub("[\.\,\!\?\:\;\-\=¿¡\|\(\)#\[\]\"]", "", sentence).lower()).split()))
    lexicon = Lexicon(filename)
    possible_lexicons = get_possible_lexicons(lexicon)
    ug = UniversalGrammar(set(), set(), set())
    i_lang = ILanguage(lexicon, ug)
    successfull_derivations = []
    for i in range(len(possible_lexicons)):
        word_list = phrase_to_list(possible_lexicons[i], sentence)
        functional_list = [item for item in possible_lexicons[i] if (list(item.phon))[0].label.startswith('[')]
        word_list = add_functional_categories(word_list,functional_list)
        deriv = Derivation(i_lang, word_list=word_list)
        deriv.autoderive(sentence, debug)
        if deriv.successfull_derivation != None:
            successfull_derivations.append(deriv.successfull_derivation)
    
    if len(successfull_derivations) > 0:
        print('')
        print(len(successfull_derivations),"derivation(s)")
        print('')
        for derivation in successfull_derivations:
            derivation.print_derivation()
            print('')
    else:
        print('')
        print('Sentence is not derivable.')
        print('')