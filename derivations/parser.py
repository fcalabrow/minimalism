from structures import *
from derivations import derivation

class Derivation(derivation.Derivation):
    
    def autotf(self, index):
        self.print_derivation()
        x = self.stages[-1].workspace.find_workspace(index) # get x

        # Rule 1 - Successful derivation
        if len(x.triggers) == 0 and len(self.stages[-1].workspace.w) == 1 and len(self.stages[-1].lexical_array.the_list) == 0:
            print("Successfull parsing!")
            print('')
            return True

        # Rule 2
        if len(x.triggers) > 1 and len(self.stages[-1].workspace.w) == 1 and len(self.stages[-1].lexical_array.the_list) == 0 and type(x) != SyntacticObjectSet:
            return None

        # Rule 3 - Internal merge
        if len(x.triggers) > 0 and len(self.stages[-1].workspace.w) == 1 and len(self.stages[-1].lexical_array.the_list) == 0 and type(x) == SyntacticObjectSet:
            print('Aplying rule 3: internal merge (X,Y)')
            features = [trigger for trigger in x.triggers]
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
            list = [y.idx for y in self.stages[-1].lexical_array.the_list]
            self.autoselect(min(list))
            return True

        # Rule 5 - External merge (Y,X)
        if len(x.triggers) == 0 and len(self.stages[-1].workspace.w) == 2:
            print('Aplying rule 5: external merge (Y,X)')
            for y in self.stages[-1].workspace.w:
                features = [trigger for trigger in y.triggers]
                if len(features) > 0 and x.category.label == features[0].label:
                    self.automerge(y.idx,index)
                    return True
                # Rule 7 
            if len(self.stages[-1].lexical_array.the_list) > 0:
                    print('Aplying rule 7: select(Z)')
                    index_z = min([y.idx for y in self.stages[-1].lexical_array.the_list])
                    self.autoselect(index_z)
                    return True
            return None

        # Rule 6 - External merge (X,Y)
        if len(x.triggers) > 0 and len(self.stages[-1].workspace.w) == 2:
            features = [trigger for trigger in x.triggers]
            for y in self.stages[-1].workspace.w:
                if y.category.label == features[0].label:
                    self.automerge(index,y.idx)
                    return True
            return None

        # Rule 8 - External merge
        if len(x.triggers) > 0 and len(self.stages[-1].workspace.w) == 3:
            print('Aplying rule 8')
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

    def autoderive(self):
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

def parse(phrase):
    lexicon = Lexicon()
    ug = UniversalGrammar(set(), set(), set())
    i_lang = ILanguage(lexicon, ug)
    list = phrase_to_list(lexicon, phrase)
    deriv = Derivation(i_lang, word_list=list)
    deriv.autoderive()
    del deriv
