## Define function to create nlp model with custom tokenization rules
import spacy
from spacy.symbols import ORTH

def get_custom_nlp(disable=None):
    '''Returns a spacy nlp model with custom tokenization and sentencizer rules.'''

    ## Define custom sentencizer
    def my_sentencizer(doc):
        '''Assumes doc is a spacy doc object.
        Returns a doc object with custome sentencizer rules applied.'''
        for i, token in enumerate(doc[:-1]):
            if token.text == 'prof.' or token.text == 'Prof.':
                doc[i].is_sent_start = False
            if token.text == 'dr.' or token.text == 'Dr.':
                doc[i].is_sent_start = False
            if token.text == 'phd.':
                doc[i].is_sent_start = False
            if token.text == 'mphil.':
                doc[i].is_sent_start = False
                
            if token.text in ('/', ',', ':'):
                doc[i+1].is_sent_start = False
            if token.is_lower:
                doc[i].is_sent_start = False
            if i != 0 and doc[i-1].is_punct == False:
                doc[i].is_sent_start = False
            if token.is_punct and doc[i+1].is_lower:
                doc[i].is_sent_start = False
            if token.is_punct and token.text not in ('.', '"', "'", '!', '?'):
                doc[i+1].is_sent_start = False
            # if token.text == 'so':
            #     doc[i].is_sent_start = False
            # if token.text == 'say' or token.text == 'says' or token.text == 'said':
            #     doc[i].is_sent_start = False
            # if token.text == 'tell' or token.text == 'tells' or token.text == 'told':
            #     doc[i].is_sent_start = False
            # if token.text == 'add' or token.text == 'adds' or token.text == 'added':
            #     doc[i].is_sent_start = False
        
        return doc
    
    if not disable:
        nlp = spacy.load('en_core_web_sm')
    else:
        nlp = spacy.load('en_core_web_sm', disable=disable)

    nlp.tokenizer.add_special_case('prof.', [{'ORTH':'prof.'}])
    nlp.tokenizer.add_special_case('dr.', [{'ORTH':'dr.'}])
    nlp.tokenizer.add_special_case('phd.', [{'ORTH':'phd.'}])
    nlp.tokenizer.add_special_case('ph.d.', [{'ORTH':'ph.d.'}])
    nlp.tokenizer.add_special_case('Phd.', [{'ORTH':'phd.'}])
    nlp.tokenizer.add_special_case('PhD.', [{'ORTH':'phd.'}])
    nlp.tokenizer.add_special_case('PHD.', [{'ORTH':'phd.'}])
    nlp.tokenizer.add_special_case('Ph.d.', [{'ORTH':'ph.d.'}])
    nlp.tokenizer.add_special_case('Ph.D.', [{'ORTH':'ph.d.'}])
    nlp.tokenizer.add_special_case('PH.D.', [{'ORTH':'ph.d.'}])
    nlp.tokenizer.add_special_case('mphil.', [{'ORTH':'mphil.'}])
    nlp.tokenizer.add_special_case('MPhil.', [{'ORTH':'mphil.'}])
    nlp.tokenizer.add_special_case('MPHIL.', [{'ORTH':'mphil.'}])

    nlp.add_pipe(my_sentencizer, before='parser')
    
    # bytes_data = nlp.to_bytes()
    # lang = nlp.meta["lang"] 
    # pipeline = nlp.meta["pipeline"] 

    # nlp = spacy.blank(lang)
    # for pipe_name in pipeline:
    #     pipe = nlp.create_pipe(pipe_name)
    #     nlp.add_pipe(pipe)
    # nlp.from_bytes(bytes_data)
    
    return nlp
