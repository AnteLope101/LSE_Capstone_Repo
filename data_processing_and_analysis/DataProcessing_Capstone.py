# -*- coding: utf-8 -*-
import re
import pandas as pd
import numpy as np
import spacy
from spacy.symbols import ORTH
from spacy.language import Language
from spacy.matcher import PhraseMatcher
from unidecode import unidecode
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
from google.api_core import exceptions
from google.api_core import retry
import json
from urllib.request import urlopen
from unidecode import unidecode
from itertools import chain
from custom_nlp import *


example_data = data1.append(data2, ignore_index=True)
example_data = example_data[['source', 'url', 'date_published', 'title', 'article_original', 'segment', 'person', 'gender', 'gender_accuracy', 'gender_samples']]
example_data.to_csv('processed_data/example_data.csv')



## Define function to remove articles that are likely to be irrelevant to science
def remove_irrelevant_articles(raw_data):
    '''Assumes all_data is a dataframe of all processed data.
    Returns the dataframe with non-science-relevant articles removed.'''
    
    to_remove = []
    for i, article in raw_data[['article']].itertuples():
        
        if pd.isna(article):
            to_remove.append(i)
            continue    
        
        ir_terms = re.findall(r'\b((episodes?)|(movies?)|(films?)|(tvs?)|(books?)|(novels?)|(olympics?)|(althele.+)|(football))\b', article, re.IGNORECASE)
        if len(ir_terms) > 5:
            to_remove.append(i)
        
    raw_data.drop(to_remove, axis=0, inplace=True)
    raw_data.reset_index(drop=True, inplace=True)
        
    return raw_data




## Define function to remove irrelevant names that has a low likelihood of corrsponding to person names
def relevant_name(person):
    '''Assumes person is a string representing a potential personn name.
    Tests if person refers to an actual person name and returns True if person passes all tests; False otherwise.'''
  
    names = person.split()
    if re.search(r'[^\s\.\-\'a-zA-Z]', person):
        return False
    
    elif len(names) == 1:
        return False
    
    elif person[0].islower():
        return False
        
    elif person.startswith('St '):
        return False
    
    elif re.search(r'\b((crater)|(glacier))\b', person, re.IGNORECASE):
        return False
    
    elif len(re.sub(r'[^a-zA-Z\s[.]]', '', names[0])) <= 1:
        return False
    
    return True




## Define function to split article into segments using spacy
def get_segments(doc):
    '''Assumes doc is a spacy doc of a news article.
    Returns a dictionay of relevant person names and their corresponding article segments.'''
    
    all_doc_per = {}
    for i, ent in enumerate(doc.ents):
        if ent.label_ == 'PERSON' and len(ent.text.split(' ')) > 1 and ent.text[0].isupper():
            
            person = re.sub(r'^((ph[.]?d[.]?)|(dr[.]?)|(prof[.]?))\s', '', ent.text, flags=re.I).strip()
            person = unidecode(person).replace("'s ", ' ').replace("s' ", 's ')
            
            if not relevant_name(person):
                continue
            
            if person not in all_doc_per: 
                all_doc_per[person] = None 
    
    sentences = list(doc.sents)         
    for person in all_doc_per.keys():
        for si, sent in enumerate(doc.sents):
            
            person0 = re.sub('[.]$', '', person)
            if re.search(r'\b{}\b'.format(person0), sent.text):
                
                if si+5 < len(sentences):
                    seg5 = sentences[si:si+5]
                    seg5 = ' '.join([s.text for s in seg5])
                    all_doc_per[person] = seg5
                    break
                
                else:
                    seg5 = sentences[si:]
                    seg5 = ' '.join([s.text for s in seg5])
                    all_doc_per[person] = seg5
                    break
    
    all_names = list(all_doc_per.keys())
    all_segs = list(all_doc_per.values())
    for se_i, se in enumerate(all_segs):
        if not se:
            del all_doc_per[all_names[se_i]]
    
    return all_doc_per
                


## Define function to trim segments up to the appearance of a second name
def trim_segments(all_doc_per):
    '''Assumes all_doc_per is a dictionary of person names and segments.
    Returns a new dictionary of person names and trimmed segments.'''
    
    matcher = PhraseMatcher(nlp.vocab)
    patterns = [nlp.make_doc(name) for name in all_doc_per.keys()]
    matcher.add('Name', None, *patterns)
    
    all_segments = nlp.pipe(list(all_doc_per.values()), n_threads=4)
    for doc_i, doc in enumerate(matcher.pipe(all_segments)):
        matches = matcher(doc)
        persons = [(doc[start:end], start) for matcher_id, start, end in matches]
        
        if len(persons) == 0:
            
            del all_doc_per[patterns[doc_i].text]
        
        elif len(persons) == 1:
            seg5 = doc.text
            all_doc_per[patterns[doc_i].text] = seg5
        
        else:
            sentences = list(doc.sents)
            persons_remove = [per for per in persons if per[1] > sentences[0].end]
            if not persons_remove:
                seg5 = doc.text
                all_doc_per[patterns[doc_i].text] = seg5
            else:
                i = 1
                sent = sentences[i]
                while persons_remove[0][1] > sent.end:
                    i += 1
                    sent = sentences[i]
                else:
                    seg5 = sentences[:i]
                    seg5 = ' '.join([s.text for s in seg5])
                    all_doc_per[patterns[doc_i].text] = seg5

    return all_doc_per




## Define function to create a data frame of with segments and person names extracted.
def create_seg_df(data):
    '''Assume data is a data frame from data collection.
    Returns a new data frame with articles being split into segments.'''
    
    nlp = get_custom_nlp(disable=['tagger'])

    new_segments = pd.DataFrame()

    for rowtuples in data.itertuples():  
        
        article = unidecode(rowtuples.article).replace("'s ", ' ').replace("s' ", 's ').replace("'m ", ' ').replace("'re ", ' ').replace("n't ", ' not ').replace('\n', ' ')
        article = re.sub(r'\s{2,}', ' ', article)
        article = re.sub(r"(\s+)|(\xa0)", " ", article)
        doc = nlp(article)
    
        name_segments = get_segments(doc)
        name_segments = trim_segments(name_segments)
        
        if not name_segments:
            continue
        
        new_rows = pd.DataFrame([rowtuples]).drop(['Index'], axis=1)
        new_rows = pd.concat([new_rows]*len(name_segments), ignore_index=True)
        
        new_rows.rename(columns={'article':'article_original'}, inplace=True)
        new_rows['segment'] = list(name_segments.values())
        new_rows['person'] = list(name_segments.keys())

        new_segments = new_segments.append(new_rows, ignore_index=True, sort=False)
    
    return new_segments



## Define generator function to split data frames.
def split_df(data, n):
    '''Assumes data is a large data frame.
    Splits data into n equal parts using numpy.'''

    for df in np.array_split(data, n):
        yield df



## Define function to validate person names extracted by Spacy using Google's Natural Language API.
def validate_namesdf(data):
    '''Assume data is a processed data frame with a person column.
    Return the data frame with an added validated person column.'''

    client = language.LanguageServiceClient.from_service_account_json('capstone-268223-d1374d0bdb4a.json')
    
    new_segments = pd.DataFrame()
    all_segments = split_df(data, 100)
    
    for segments in all_segments:
        
        segments.reset_index(drop=True, inplace=True)
        all_per_str = ', '.join(list(segments['person']))
        document = types.Document(content=all_per_str,
                                  type=enums.Document.Type.PLAIN_TEXT,
                                  language='en')
        
        predicate_504 = retry.if_exception_type(exceptions.DeadlineExceeded)
        retry_504 = retry.Retry(predicate_504)
        
        google_ents = retry_504(client.analyze_entities,)(document, encoding_type='UTF32')
        google_entities = sorted(google_ents.entities, key = lambda ent: ent.mentions[0].text.begin_offset)
        
        all_per_dict = {}
        for ent in google_entities:
            if enums.Entity.Type(ent.type).name=='PERSON':
                for ment in ent.mentions:
                    pname = ment.text.content
                    if len(pname.split()) > 1:
                        if pname not in all_per_dict:
                            all_per_dict[pname] = 'IS_NAME'
                        break

        is_name = []
        for i, person in segments[['person']].itertuples():
            if person not in all_per_dict:
                is_name.append(None)
            else:
                is_name.append(all_per_dict[person])

        segments['is_name'] = is_name
        segments.dropna(subset=['is_name'], inplace=True)
    
        new_segments = new_segments.append(segments, ignore_index=True)

    return new_segments





## Define function to  remove article segments with little contents
def clean_segments(data):
    '''Assumes data is a dataframe of processed data.
    Returns a cleaned dataframe without pseudo-articles containing mainly numbers.'''

    to_remove = []
    for i, segment in data[['segment']].itertuples():

        ## Remove articles with at least three consecutive capitalized words
        if re.search(r'[A-Z]{3,}\s[A-Z]{3,}\s[A-Z]{3,}', segment):
            to_remove.append(i)
            continue
        
        ## Remove articles that start with at least 2 '_' or 3 '-'
        if re.search(r'^([_]{2,})|^([-]{3,})', segment):
            to_remove.append(i)
            continue
        
        ## Remove articles that have 15 or fewer alphabetic words
        segment = re.sub(r'[^A-Za-z\s]', '', segment)
        if len(segment.split()) <= 15:  
            to_remove.append(i)
            continue

    data.drop(to_remove, axis=0, inplace=True)
    data.reset_index(drop=True, inplace=True)
    
    return data




## Define function to find frequently occurred person names
def find_common_names(data, n):
    '''Assumes data is a processed data frame.
    Returns names that occurred more than n times in the corpus and their counts.'''
    
    name_counts = data.groupby('person')['segment'].count().sort_values(ascending=False)
    top_names_counts = name_counts[name_counts > 10]
    
    return top_names_counts



## Define functionn to remove common names and non-focal names from articles
# common_names = pd.read_csv('processed_data/common_names.csv' , header=None)
# common_names = common_names.apply(lambda x: ','.join(x.dropna().values.tolist()), axis=1).str.cat(sep = ',')
# common_names = set(common_names.replace(', ', ',').split(','))

def remove_names(data, common_names, n=5):
    '''Assumes data is a processed data frame, common_names is a set of frequently occurring names and n is the number of co-occurring names in the same segment to be removed.
    Returns a data frame with common names and non-focal names removed and replaced with handles.'''

    common_inds = [i for i, person in data[['person']].itertuples() if person in common_names]
    
    ir_names0 = data.loc[data['no_of_persons'] > 5, 'person']
    ir_names0 = set(ir_names0)
    ir_inds = list(data.loc[data['no_of_persons'] > 5, 'person'].index)
    
    for url, rows in data.groupby('url', sort = False):
        article = rows['article_original'].iloc[0]
        for ip, person in rows[['person']].itertuples():
            pattern = person.replace(' ', '|')
            if person in common_names:
                article = re.sub(r'\b{}s?\b'.format(pattern), '[COMMON_NAME]', article)
                if ip not in common_inds:
                    common_inds.append(ip)
            elif person in ir_names0:
                article = re.sub(r'\b{}s?\b'.format(pattern), '[NON_FOCAL_NAME]', article)
                if ip not in ir_inds:
                    ir_inds.append(ip)

        data.loc[rows.index, 'article_original'] = article

    all_inds = np.union1d(ir_inds, common_inds)
    data.drop(all_inds, inplace=True)
    
    return data




## Define function to remove non-science-related names eg. government officials, lawyers
def remove_nonsci_names(data):

    nlp = get_custom_nlp(disable=['tagger', 'ner'])

    nonsci_inds = []
    for i, segment, person in data[['segment', 'person']].itertuples():
        doc = nlp(segment)
        sentences = list(doc.sents)
        pattern = person.replace(' ', '|')
        
        for sent in sentences:
            if re.search(r'\b{}s?\b'.format(pattern), sent.text):
                sent = ' '.join([token.text for token in sent if token.is_punct == False or token.is_digit == False])
                if re.search(r'\b((ministers?)|(mps?)|(governors?)|(secretar.+)|(attorneys?)|(mayors?)|(parliaments?)|(tory)|(labour)|(federal)|(republicans?)|(democrats?)|(lawyers?)|(judges?)|(coach(es)?)|(extremists?)|(optimists?)|(journalists?)|(photographers?))\b', sent, re.IGNORECASE):
                    nonsci_inds.append(i)
                    break
        
        ir_terms = re.findall(r'\b((episodes?)|(movies?)|(films?)|(tvs?)|(books?)|(novels?)|(sci-fis?)|(olympics?)|(althele.+)|(football)|(gaming))\b', segment, re.IGNORECASE)
        re_terms = re.search(r'\b(scien.+|research.*?|stud[y|(ies)]|universit.+?|academi.+?|[a-zA-Z]+[gcm]ists?|engineers?|experts?|specialists?|prof[.]?(essors?)?|dr[.]?|lecturers?|postdocs?|ph[.]?d[.]?|mphil[.]?|authors?)\b', segment, re.IGNORECASE)
        if ir_terms and not re_terms:
            nonsci_inds.append(i)
            continue

    non_urls = data.loc[nonsci_inds, 'url']
    non_names = data.loc[nonsci_inds, 'person']
    for url, person in zip(non_urls, non_names):
        pattern = person.replace(' ', '|')
        article = data.loc[data['url'] == url, 'article_original'].iloc[0]
        article = re.sub(r'\b{}\b'.format(pattern), '[NON_SCI_NAME]', article)
        data.loc[data['url'] == url, 'article_original'] = article
    
    data.drop(nonsci_inds, inplace=True)
    data.reset_index(drop=True, inplace=True)
    
    return data



## Define function to add no_of_persons columnn
def get_num_persons(data):
    '''Assumes data is a processed data frame.
    Returns a data frame with an additional no_of_persons column indicating the number of persons that appear in the same segment (sentence).'''
        
    data.drop_duplicates(subset=['url', 'person'], inplace=True)
    data['no_of_persons'] = 1
    for segment, rows in data.groupby('segment', sort = False): 
        data.loc[rows.index, 'no_of_persons'] = len(rows)
    
    
    return data


## Define function to add total_no_of_persons column
def get_total_num_persons(data):
    '''Assumes data is a processed data frame.
    Returns a data frame with an additional total_no_of_persons column indicating the number of co-occurring persons in the same article.'''
    
    data['total_no_of_persons'] = 1
    data.sort_values(by=['source', 'url'], inplace=True)
    
    for url, rows in data.groupby('url', sort = False):
        num_persons = len(rows)
        data.loc[rows.index, 'total_no_of_persons'] = num_persons
    
    return data


data.to_csv('processed_data/processed_news_data123NNNNN.csv', index=False)




## Define function to add scientist column
from spacy.language import Language

def get_scientists(data):
    '''Assume data is a processed data frame.
    Returns a data frame with an additional scientist column indicating the scientist identity (as defined in the study) of a person name.'''
    
    nlp = get_custom_nlp(disable=['tagger', 'ner'])

    row_scientists = []
    
    for i, segment, person in data[['segment', 'person']].itertuples():
        
        segment = re.sub(r'\s{2,}', ' ', segment)
        doc = nlp(segment)
        sentences = list(doc.sents)

        pattern = person.replace(' ','|')
        for isent, sent in enumerate(sentences):
            if re.search(r'\b{}\b'.format(pattern), sent.text):
                sent = ' '.join([token.text for token in sent if token.is_punct == False or token.is_digit == False])
                
                sci = re.search(r'\b(scientists?|researchers?|[a-zA-Z]+[gcm]ists?|engineers?|prof[.]?(essors?)?|dr[.]?|lecturers?|postdocs?|ph[.]?d[.]?|mphil[.]?|authors?)\b', sent, re.IGNORECASE)
                non_sci = re.search(r'\b((optimists?)|(extremists?)|(strategists?)|(journalists?))\b', sent, re.IGNORECASE)

                sci_relev = re.search(r'\b(sciences?|research.*?|stud[y|(ies)]|experiments?|universit.+?|academi.+?|experts?|specialists?|collaborators?)\b', sent, re.IGNORECASE)
                sci_irrelev = re.search(r'\b((presidents?)|(ministers?)|(mps?)|(governors?)|(secretar.+)|(attorneys?)|(mayors?)|(parliaments?)|(tory)|(labour)|(federal)|(republicans?)|(democrats?)|(lawyers?)|(elections?)|(votes)|(bills?)|(compan[y|ies])|(firms?)|(enterprises?))\b', sent, re.IGNORECASE)        
                
                if sci and not non_sci:
                    row_scientists.append(1)
                    break
                elif sci_relev and not sci_irrelev:
                    row_scientists.append(1)
                    break

            if isent == len(sentences)-1:
                row_scientists.append(0)

    data['scientist'] = row_scientists

    return data







## Define function to identify the gender of person names using GenderAPI
def add_gender(data):
    '''Assumes data is a processed data frame.
    Returns a  data frame with 3 additional columns indicating gender, accuracy and sample size of the gender identification respectively.'''
        
    api_key = 'sHmrouupMKmJsVchlJ'

    gender = []
    gender_accuracy = []
    gender_samples = []

    for i, person, num_persons in data[['person', 'no_of_persons']].itertuples():

        if num_persons == 1:
            first_name = person.split(' ')[0].lower()
            first_name = unidecode(first_name)
            url = "https://gender-api.com/get?key=" + api_key + "&name=" + first_name
                    
            response = urlopen(url)
            decoded = response.read().decode('utf-8')
            gen_data = json.loads(decoded)

            gender.append(gen_data['gender'])
            gender_accuracy.append(gen_data['accuracy'])
            gender_samples.append(gen_data['samples'])

    data['gender'] = gender
    data['gender_accuracy'] = gender_accuracy
    data['gender_samples'] = gender_samples
    
    return data



# Swap positions of the first names and last names of Eastern names for gender identification only
def swap_first_last_name(data):
    '''Assumes data is a processed data frame.
    Returns a list of tuples of Eastern names with their first name last name positions swapped, and their indices in the data frame'''
    
    new_persons = []
    for i, person in data.loc[to_drop, ['person']].itertuples():
        if re.search(r'((^Li )|(Xiao )|(Xi )|(Hua )|(An )|(Shi )|(Yuen ))', person):
            name = person.split()
            if len(name) == 2:
                new_name = ' '.join([name[1], name[0]])
                new_persons.append((i, new_name))
    
    return new_persons



## Define function to remove names with unkonwn gender or gender accuracy < 60  (since there is no reason to think that female/male names are more likely to be identified as unknown names; also remove non-names)
def remove_genders(data):
    '''Assumes data is a processed data frame.
    Returns a data frame with names whose genders were not identified or with low accuracy removed.'''

    to_keep_rows = []
    to_drop = []
    for i, person, gender, gender_acc in data[['person', 'gender', 'gender_accuracy']].itertuples():

        if gender == 'unknown' or int(gender_acc) < 60:
            to_drop.append(i)
        
    data.drop(to_drop, inplace=True)
    data.reset_index(drop=True, inplace=True)
    
    return data




## Define function to extract quotes and create segments that do not include quotes
def get_quotes(data):
    '''Assumes data is a processed data frame.
    Returns a data frame with 2 additional columns indicating the direct and indirect speech attributed to a person name and their counts.'''

    data.drop_duplicates(subset=['url', 'person'], inplace=True)

    nlp = get_custom_nlp(disable=['tagger', 'ner'])
    
    
    for url, news in data.groupby('url', sort=False):
        
        person_dict = {per:[] for per in news.person}
        
        doc = nlp(news.article_original.iloc[0]) 
        all_sents = list(doc.sents)
        
        for i, sent in enumerate(doc.sents):
            
            if not re.search(r'\b((said)|(says?)|(tells?)|(told)|(adds?(ed)?)|(explains?(ed)?))\b|(points?(ed)? out)', sent.text, re.IGNORECASE):
                continue 
            
            for person, num_persons, gender in zip(news.person, news.no_of_persons, news.gender):
                
                pattern = person.replace(' ', '|')
            
                if re.search(r'\b{}s?\b'.format(pattern), sent.text):
                    person_dict[person].append(sent.text)
                    break
                elif gender == 'female' and re.search(r'she (\b((said)|(says?)|(tells?)|(told)|(adds?(ed)?)|(explains?(ed)?))\b|(points?(ed)? out))', sent.text, re.IGNORECASE):
                    i_sub = 1
                    while i_sub <= i:
                        if re.search(r'({})'.format(pattern), all_sents[i-i_sub].text):  #Assumes that co-reference locates in previous sentence the furthest
                            person_dict[person].append(sent.text)
                            break
                        else:
                            i_sub += 1
                    break 
                elif gender == 'male' and re.search(r'he (\b((said)|(says?)|(tells?)|(told)|(adds?(ed)?)|(explains?(ed)?))\b|(points?(ed)? out))', sent.text, re.IGNORECASE):
                    i_sub = 1
                    while i_sub <= i:
                        if re.search(r'({})'.format(pattern), all_sents[i-i_sub].text):  #Assumes that co-reference locates in previous sentence the furthest
                            person_dict[person].append(sent.text)
                            break
                        else:
                            i_sub += 1
                    break 
                                
                        
        all_quotes = pd.Series(person_dict)
        data.loc[data['url'] == url, 'quote'] = all_quotes.apply(lambda x: '/ '.join(x)).values
        data.loc[data['url'] == url, 'no_of_quotes'] = all_quotes.apply(len).values.astype('int32')
    
    data.reset_index(drop=True, inplace=True)
    
    return data



## Define function to get a sample of articles 
def sample_articles(data):
    '''Assumes data is a processed data frame.
    Returns a data frame representing 1% sample of the original articles from each source.'''

    data_nodup = data.drop_duplicates(subset=['url'])  

    articles_sample = pd.DataFrame()
    for source in data_nodup['source'].unique():
        data_sample = data_nodup[data_nodup['source'] == source].sample(frac=0.01)
        articles_sample = articles_sample.append(data_sample)

    return articles_sample




## Define function to stack dataframe
def stack_data(all_data):
    '''Assumes all_data is a processed dataframe.
    Returns a data frame with repeated article segments removed and person names appearing in the same segment/sentence concatenated.'''
    
    all_data.drop_duplicates(subset=['segment', 'person'], inplace=True)
    
    all_persons = []
    no_of_persons = []
    all_scientists = []
    all_genders = []
    all_gender_accs = []
    all_gender_sams = []
    all_quotes = []
    all_act_scientists = []
    
    for segment, rows in all_data.groupby('article_original', sort = False):
        
        no_of_persons.append(len(rows))
        
        rows['scientist'] = rows['scientist'].astype(str)
        rows['gender_accuracy'] = rows['gender_accuracy'].astype(str)
        rows['gender_samples'] = rows['gender_samples'].astype(str)
        rows['no_of_quotes'] = rows['no_of_quotes'].astype(str)
        
        if len(rows) > 1:
            
            all_persons.append(rows['person'].str.cat(sep='; '))
            all_genders.append(rows['gender'].str.cat(sep='; '))
            
            all_scientists.append(rows['scientist'].str.cat(sep='; '))
            all_gender_accs.append(rows['gender_accuracy'].str.cat(sep='; '))
            all_gender_sams.append(rows['gender_samples'].str.cat(sep='; '))
            all_quotes.append(rows['no_of_quotes'].str.cat(sep='; '))
        
        else:
            
            all_persons.append(rows['person'].iloc[0])
            all_genders.append(rows['gender'].iloc[0])
            
            all_scientists.append(rows['scientist'].iloc[0])
            all_gender_accs.append(rows['gender_accuracy'].iloc[0])
            all_gender_sams.append(rows['gender_samples'].iloc[0])
            all_quotes.append(rows['no_of_quotes'].iloc[0])
            
                                      
    new_data = all_data.drop_duplicates(subset=['article_original'])
    
    new_data['person'] = all_persons
    new_data['no_of_persons'] = no_of_persons
    new_data['scientist'] = all_scientists 
    new_data['gender'] = all_genders
    new_data['gender_accuracy'] = all_gender_accs
    new_data['gender_samples'] = all_gender_sams
    new_data['no_of_quotes'] = all_quotes

    new_data.reset_index(drop=True, inplace=True)
    
    return new_data

