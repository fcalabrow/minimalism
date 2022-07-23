from structures import *
from derivations import derivation

class Derivation(derivation.Derivation):
    
    sentence_to_parse = ''
    transferred_sentence = []

    def transfer(self,so):
        list_from_set = list(so.syntactic_object_set)
        x,y = list_from_set[0],list_from_set[1]
        if type(x) == LexicalItemToken and type(y) == LexicalItemToken:
            if len(x.triggers) != 0: # if head
                self.transferred_sentence.append(list(x.lexical_item.phon)[0].label)
                self.transferred_sentence.append(list(y.lexical_item.phon)[0].label)
            else: # if complement
                self.transferred_sentence.append(list(y.lexical_item.phon)[0].label)
                self.transferred_sentence.append(list(x.lexical_item.phon)[0].label)
        elif type(x) == SyntacticObjectSet and type(y) == SyntacticObjectSet:
            if len(x.triggers) != 0: # if head
                self.transfer(y)
                self.transfer(x)
            else: # if specifier
                self.transfer(x)
                self.transfer(y)
        else: # internal merge
            if type(x) == LexicalItemToken:
                self.transferred_sentence.append(list(x.lexical_item.phon)[0].label)
                for z in list(y.syntactic_object_set):
                    if z.lexical_item != x.lexical_item:
                        self.transferred_sentence.append(list(z.lexical_item.phon)[0].label)
    
    def autotf(self, index):
        self.print_derivation()
        x = self.stages[-1].workspace.find_workspace(index) # get x

        # Rule 1 - Successful derivation
        if len(x.triggers) == 0 and len(self.stages[-1].workspace.w) == 1 and len(self.stages[-1].lexical_array.the_list) == 0:
            print('Aplying transfer')
            self.transfer(x)
            self.transferred_sentence = ' '.join(self.transferred_sentence)
            if self.transferred_sentence == self.sentence_to_parse:
                print("Successfull parsing!")
                print('')
                return True
            else:
                #print('Transferred sentence: ',self.transferred_sentence)
                return None

        # Rule 2
        if len(x.triggers) > 1 and len(self.stages[-1].workspace.w) == 1 and len(self.stages[-1].lexical_array.the_list) == 0 and type(x) != SyntacticObjectSet:
            return None

        # Rule 3 - Internal merge
        if len(x.triggers) == 1 and len(self.stages[-1].workspace.w) == 1 and len(self.stages[-1].lexical_array.the_list) == 0 and type(x) == SyntacticObjectSet:
            features = [trigger for trigger in x.triggers]
            if features[0].label[-1] == '/':
                features[0].label = features[0].label[0:-1]
                print('Aplying rule 3: internal merge (X,Y)')
                print('')
                for y in x.syntactic_object_set:
                    if y.category.label == features[0].label:
                        self.automerge(index,y.idx)
                        return True
                    elif type(y) == SyntacticObjectSet:
                        for z in y:
                            features = [trigger for trigger in x.triggers]
                            if z.category.label == features[0].label:
                                y = z
                                self.automerge(index,y.idx)
                                return True
            return None

        # Rule 4 - Select
        if len(self.stages[-1].workspace.w) == 1 and len(self.stages[-1].lexical_array.the_list) > 0:
            print('Aplying rule 4: select(Y)')
            print('')
            list = [y.idx for y in self.stages[-1].lexical_array.the_list]
            self.autoselect(min(list))
            return True

        # Rule 5 - External merge (Y,X)
        if len(x.triggers) == 0 and len(self.stages[-1].workspace.w) == 2:
            print('Aplying rule 5: external merge (Y,X)')
            print('')
            for y in self.stages[-1].workspace.w:
                features = [trigger for trigger in y.triggers]
                if len(features) > 0 and x.category.label == features[0].label:
                    self.automerge(y.idx,index)
                    return True
                # Rule 7 
            if len(self.stages[-1].lexical_array.the_list) > 0:
                    print('Aplying rule 7: select(Z)')
                    print('')
                    index_z = min([y.idx for y in self.stages[-1].lexical_array.the_list])
                    self.autoselect(index_z)
                    return True
            return None

        # Rule 6 - External merge (X,Y)
        if len(x.triggers) > 0 and len(self.stages[-1].workspace.w) == 2:
            print('Aplying rule 6: external merge (X,Y)')
            print('')
            features = [trigger for trigger in x.triggers]
            for y in self.stages[-1].workspace.w:
                if y.category.label == features[0].label:
                    self.automerge(index,y.idx)
                    return True
            return None

        # Rule 8 - External merge
        if len(x.triggers) > 0 and len(self.stages[-1].workspace.w) == 3:
            print('Aplying rule 8: external merge(Z,Y)')
            print('')
            self.automerge(index,index-1)
            return True

    def autoselect(self, index):
        last_stage = self.stages[-1]
        lexical_item_token = last_stage.lexical_array.find_lexical_array(index)
        new_stage = last_stage.select_stage(lexical_item_token)
        self.stages.append(new_stage)
        if self.autotf(index) == None:
             print('Derivation failed')
             print('')
             return
    
    def automerge(self, idx1, idx2):
        last_stage = self.stages[-1]
        try:
            new_stage = last_stage.merge_stage(idx1, idx2)
        except InteractionError:
            print('Derivation failed')
            return
        self.stages.append(new_stage)
        #print('Stage: ',len(self.stages))
        index = max([x.idx for x in last_stage.workspace.w])
        if self.autotf(index) == None:
             print('Derivation failed')
             print('')
             return

    def autoderive(self,sentence):
        self.sentence_to_parse = sentence
        self.autoselect(0)

def word_to_lex(lexicon,word):
    """ Matches a word with its lexical items
    Return None if word is not in lexicon """
    lexical_item = None
    for x in lexicon.lex:
            if (list(x.phon))[0].label == word:
                lexical_item = x
    return lexical_item

def phrase_to_list(lexicon, phrase):
    """ Param: phrase (str)
    Return: list of lexical_item """
    phrase = phrase.split()
    list = [word_to_lex(lexicon, w) for w in phrase]
    list.reverse()
    return list

def parse(sentence,filename="lexicon.xml"):
    lexicon = Lexicon(filename)
    ug = UniversalGrammar(set(), set(), set())
    i_lang = ILanguage(lexicon, ug)
    list = phrase_to_list(lexicon, sentence)
    deriv = Derivation(i_lang, word_list=list)
    deriv.autoderive(sentence)
    del deriv