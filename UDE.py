import sys
import codecs
import argparse
import json
import re
import nltk
from datetime import datetime
from collections import Counter, defaultdict
from text2num import text2num, NumberException
from tokenizer import word_tokenize, sent_tokenize

SUMMARY_KEY = "summary"

NON_ENTITY_RECORDS_KEY = "non_entity_records"

UNIQUE_IDENTIFIER = "identifier"
ENTITIES_KEY = "entities"
ENTITY_TEXT_ATTRIBUTE = "Name"

GROUPING_KEY = "belongs_to"

GROUPS_KEY = "groups"
GROUP_TEXT_ATTRIBUTE = "Name"

FEATURE_KEY = "features"

NOT_AVAILABLE = "N/A"


#these keys had to be manually changed
number_words = set(["one", "two", "three", "four", "five", "six", "seven", "eight", "nine",
                    "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen",
                    "seventeen", "eighteen", "nineteen", "twenty", "thirty", "forty", "fifty",
                    "sixty", "seventy", "eighty", "ninety", "hundred", "thousand"])


'''
JSON General Data Format:
[
    
    {       ###entry_0###
    "non_entity_records" = [
        "attribute_1": "value_1",
        "attribute_2": "value_2",
        "day": "sunday",
        ...
    ],
    "summary": [
        "This", "is", "a", "tokenized", "summary", "...",
    ], 
    "entities": [
        "entity_0": {
            "identifier": "unique ID",
            "belongs_to": "group_1_ID"
            "features": ["list", "of", "features",...],
            "Attribute_1": "value",
            "Attribute_2": "value",
            ...
        },
        "entity_1": {
            "identifier": "unique ID",
            "belongs_to": ["group_1_ID", "group_2_ID"],
            "features": ["list", "of", "features",...],
            ...
        }
    ], 
    "groups" : [
        "group_1": {
            "Identifier": "unique ID",
            "ATTRIBUTE_1_KEY" (TEAM NAME): "New Orleans Saints", 
            "ATTRIBUTE_2_KEY" (CITY): "New Orleans", 
            "ATTRIBUTE_3_KEY" (POINTS): "27", 
            ...,
            "features": ["V", "W"]
        }, 
        "group_2": {
            "Identifier": "unique ID",
            "ATTRIBUTE_1_KEY" (TEAM NAME): "Indianapolis Colts", 
            "ATTRIBUTE_2_KEY" (CITY): "Indianapolis",
            "ATTRIBUTE_3_KEY" (POINTS): "21", 
            ...,
            "features": ["H", "L"]
        },
        ...,
    ]
    },

    {       ### more entries###
            ....
    }
]'''
## 
## EINGABEN: "entity|attribute|value|feature"
## AUSGABEN: .gtable,.summary, .orig_summary, .links, .gtable_label, .summary_label
##         

def create_record_data(json_data):
    '''
    Creates a record of the form entity_id|attribute|value|features
    for each entity, group and non-entity information piece in each game 
    and returns this as a list of lists of strings
    '''
    ret = []
    for entry in json_data:
        records = []
        #record_string = '{}|{}|{}|{}'
        for _dict in entry:
            if _dict == SUMMARY_KEY:
                continue
            elif _dict == NON_ENTITY_RECORDS_KEY:
                #create records for non entities
                for attribute in entry[_dict]:
                    record_string = '{}|{}|{}|{}'.format('N/A', attribute, entry[_dict][attribute], 'N/A')
                    #print(record_string)
                    records.append(record_string)
            elif _dict == ENTITIES_KEY or _dict == GROUPS_KEY:
                for entity in entry[_dict]:
                    #extract feature list
                    features_list = entry[_dict][entity][FEATURE_KEY]
                    features_string = '/'.join(feat for feat in features_list)
                    #get unique entity id
                    idx = entry[_dict][entity][UNIQUE_IDENTIFIER]
                    #get attributes and values
                    for attribute in entry[_dict][entity]:
                        #skip features, because we catch them earlier
                        if attribute == FEATURE_KEY:
                            continue
                        #if attribute is a list, we make a new record for each list element
                        if isinstance(entry[_dict][entity][attribute], list):
                            for attr in entry[_dict][entity][attribute]:
                                record_string = '{}|{}|{}|{}'.format(idx, attribute, attr, features_string)
                        else:
                            record_string = '{}|{}|{}|{}'.format(idx, attribute, entry[_dict][entity][attribute], features_string)
                            records.append(record_string)
                        #print(record_string)      
        ret.append(records)
    return ret      

def extract_summary_list(json_data):
    '''
    Extract the summary tokens as a list 
    '''
    summaries = []
    for entry in json_data:
        s = entry[SUMMARY_KEY]
        summaries.append(s)
    return summaries

def extract_entity_ids(json_data, anonymised_ids=False):
    '''
    Create a list of dicts for each name and part of a name with the corresponding ids of each entity
    The name is defined by the entity_text_attribute. Please dont concatenate the names of the entities in
    the input json file
    Returns a list of dicts with key, value pairs for each entity, where value may be a string, or a set
    of strings corresponding to the ids of the entity
    TODO: 
    +++ groups!
    +   add option to anonymise ids here 
    +   add possibility to ignore parts of the name (["II", "III", "Jr", "Jr.", ...])
    '''
    entity_list = [] #list of dicts of the form [entry1{'David': {'0', '1'} -> set, 'Nate': '2'}, entry2{...},...]
    #entity names are tokenized, each token = dict key, values = each entity id (anonymised?) when the correspondings
    #entity name equals the key
    for entry in json_data:
        #extract entity names
        entity_dict = {}
        for entity in entry[ENTITIES_KEY]:
            idx = "e{}".format(entry[ENTITIES_KEY][entity][UNIQUE_IDENTIFIER])
            #try to get the naming attribute. as its not necessary, we have to failcheck
            try:
                name = entry[ENTITIES_KEY][entity][ENTITY_TEXT_ATTRIBUTE]
            except KeyError:
                name = "N/A"
            entity_dict[name] = idx
        #do the same for groups
        for group in entry[GROUPS_KEY]:
            idx = "g{}".format(entry[GROUPS_KEY][group][UNIQUE_IDENTIFIER])
            try:
                name = entry[GROUPS_KEY][group][GROUP_TEXT_ATTRIBUTE]
            except KeyError:
                name = "N/A"
            entity_dict[name] = idx

        #here we split the full name and add each part to the dictionary.
        #because these subnames may occur more than once, we have to create a set of ids
        #if it does instead of using a single value. 
        for e in list(entity_dict.keys()):
            parts = e.strip().split()
            if len(parts) > 1:
                for part in parts:
                    if len(part) > 1:
                        if part not in entity_dict:
                            entity_dict[part] = entity_dict[e]
                        elif isinstance(entity_dict[part], set):
                            entity_dict[part].add[entity_dict[e]]
                        elif entity_dict[part] != entity_dict[e]:
                            id_set = set()
                            id_set.add(entity_dict[e])
                            id_set.add(entity_dict[part])
                            entity_dict[part] = id_set
        res = {}
        for each in entity_dict:
            key = '_'.join(each.split())
            res[key] = entity_dict[each]
        entity_list.append(res)
    return entity_list

def get_entity_index(entry): #done?
    '''
    Returns a list of lists, one list per group, which contain the IDs of the entities
    that belong to this group

    TODO: 
    ++ Figure out a way to make an entity be part of two different groups
    '''
    ret = []

    for group in entry[GROUPS_KEY].keys():
        g_list = []
        g_key = entry[GROUPS_KEY][group][UNIQUE_IDENTIFIER]
        for ent in entry[ENTITIES_KEY].keys():
            if(g_key in entry[ENTITIES_KEY][ent][GROUPING_KEY]):
                g_list.append(entry[ENTITIES_KEY][ent][UNIQUE_IDENTIFIER])
        ret.append(g_list)
    return ret

def get_all_attributes(entry):
    ''' 
    Returns two lists which contain all unique attributes of entities and groups respectively
    '''
    all_entity_attributes = set()
    all_group_attributes = set()
    counter = 0
    for group in entry[GROUPS_KEY]:
        for key in entry[GROUPS_KEY][group].keys():
            all_group_attributes.add(key)
    for entity in entry[ENTITIES_KEY]:
        for key in entry[ENTITIES_KEY][entity].keys():
            all_entity_attributes.add(key)

    return list(all_entity_attributes), list(all_group_attributes)

def get_group_list(entry):
    groups = set()
    for group in entry[GROUPS_KEY]:
        groups.add(entry[GROUPS_KEY][groups][UNIQUE_IDENTIFIER])
    return list(groups)


def convert_links(json_data, links):
    '''
    compute the entry table and the indices of the found entity references in this entry table.
    The entry table consists of each attribute for each entity, sorted by the groups the entities
    belong to. after all entity attributes are indexed, the grouped attributes are indexed, again
    sorted by groups. The output consists of a list of lists, one for each entry in the input data.
    Each of these sublists have a string containing start posisitions and end positions (see links) of
    attributes found in the text and the position of the referenced attribute in the full (entry) table
    '''
    alignments = []
    
    for entry, links in zip(json_data, links):
        all_entity_attributes, all_group_attributes = get_all_attributes(entry)
        grouped_entity_lists = get_entity_index(entry)
        group_list = get_group_list(entry)
        entry_align = []
        for each_link in links:
            s_idx, e_idx, identifier, attribute = each_link
            #calculate offsets
            #entry offsets:
            #starts with entities
            #offset increases for each attribute (all unique attributes for an entry are considered)
            #the entities are "sorted" by group --> entities of the first group appear first
            #last entry has offset of #entities * #entity attributes * #groups
            #after each entity has its offset, go on with groups
            #starts after #entities * #entity attributes * #groups + 1
            #each groups attributes are considered
            #--> #groups * (_total entity offset_ * #group attributes) + 1
            #key_offset determines the attribute position in the table
            if identifier.startswith("e") # = entity
               key_offset = all_entity_attributes.index(attribute)
               if identifier[1:] in grouped_entity_list[0]:
                  entry_offset = entity_list.index(identifier) * len(all_entity_attributes)
               else:
                  entry_offset = (len(entity_list) + entity_list.index(identifier)) * len(all_entity_attributes)
            
            if identifier.startswith("g"): # = group
               key_offset = all_group_attributes.index(attribute)
               if identifier == group_list[0]:
                  entry_offset = len(group_list) * len(entity_list) * len(all_entity_attributes) + 1
               else:
                   entry_offset = len(group_list) * (len(entity_list) * len(all_entity_attributes) + len(all_group_attributes)) + 1

            index_in_table = entry_offset + key_offset

            links_str = "{}:{}-{}".format(s_idx, e_idx, index_in_table)
            entry_align.append(links_str)

        alignments.append(entry_align)
    return alignments        

def extract_summary_entities(words, entity_dict):
    '''
    Takes a list of words and extracts the entities from the text by comparing them to the entity_dict
    Returns a list of tuples, each tuple encompassing the word-position of the entity in the text, the entities name
    and its type (startPos, EndPos, name, type)
    '''
    entities = []
    idx = 0
    while idx < len(words):
        if words[idx] in entity_dict:
            entity_name = words[idx]
            entity_types = entity_dict[entity_name]
            if isinstance(entity_types, set):
                for each_type in entity_types:
                    entities.append((idx, idx+1, entity_name, each_type))
            else:
                entities.append((idx, idx+1, entity_name, entity_types))
        idx += 1
    return entities

def extract_summary_numbers(sent_words, ignore_numbers=''):
    '''
    Extract textual numbers in the text but ignoring certain keywords (like "three pointers", "Elfmeter")
    Returns a list of tuples, which are composed of the start and end position of text numbers, the string
    that is the number and the value of the number. 

    TODO:
    ++ What happens to non-int numbers? 
    '''
    ignores =[]
    numbers = []
    idx = 0
    #try to parse string numbers as int ("2" -> 2)
    while idx < len(sent_words):
        is_number = False
        try:
            number_value = int(sent_words[idx])
            numbers.append((idx, idx+1, sent_words[idx], number_value))
            idx += 1
            continue
        except:
            pass
        # try to parse written numbers to ints ("Two" -> 2)
        for end_idx in range(min(idx+5, len(sent_words)), idx, -1):
            number_string = ' '.join(sent_words[idx:end_idx])
            try:
                number_value = text2num(number_string)
                numbers.append((idx, end_idx, number_string, number_value))
                is_number = True
                idx = end_idx
                break
            except NumberException:
                if number_string in ignores:
                    break
        if not is_number:
            idx += 1
    return numbers

def get_links(entry, summary_entities, summary_numbers):
    '''
    Correlates the entities and groups with the detected summary entities
    Returns a list of (startPos, EndPos, "group_x+"entity_type, group_attribute) for groups
    and (startPos, EndPos, entity_id, entity_attribute) for entities (single attributes?)
    
    Beispiel: Klaus Kleber erspielte 3 Punkte für die New Orleans Saints
    --> (0,2,'e0','Name'), (3,4,'e0','Punkte'), (7,9,'g1','Name')
    Done?
    '''
    links = set()

    for number_item in summary_numbers:
        num_start_idx, num_end_idx, number_string, number_value = number_item

        for entity_item in summary_entities:
            (ent_start_idx, ent_end_idx, entity_name, entity_type) = entity_item

            #find numerical values and their position of every entity or group occuring in the text  
            #also find other references to e&g in the text and save the position and type of reference

            #if item is an entity
            if entity_type.startswith('e'):
                for entity in entry[ENTITIES_KEY]:
                    e = entry[ENTITIES_KEY][entity]
                    #search for the fitting entity in data
                    if e[UNIQUE_IDENTIFIER] == entity_type[1:]:
                        for attribute in e:
                            #check which attributes have values equals to the ones in the text
                            if e[attribute] == number_string \
                                or e[attribute] == str(number_value):
                                links.add((num_start_idx, num_end_idx, entity_type, attribute))
                            #also check other references found in the text
                            if entity_name in e[attribute]:
                                links.add((ent_start_idx, ent_end_idx, entity_type, attribute))
            #do the same with groups
            if entity_type.startswith('g'):
                for group in entry[GROUPS_KEY]:
                    g = entry[GROUPS_KEY][group]
                    if g[UNIQUE_IDENTIFIER] == entity_type[1:]:
                        for attribute in g:
                            if g[attribute] == number_string \
                                or g[attribute] == str(number_value):
                                links.add((num_start_idx, num_end_idx, entity_type, attribute))
                            if entity_name in g[attribute]:
                                links.add((ent_start_idx, ent_end_idx, entity_type, attribute))
    return list(links)


def extract_links(json_data, summary_list, entity_id_list, verbose=False):
    '''
    Extract a list of links which correlate the given records (entities, groups, etc) with 
    their positions in the text
    Returns a list of tuples capturing references of entities and groups with the corresponding
    positions of these references in the text. ()
    '''
    link_list = []
    for entry, summary, entities in zip(json_data, summary_list, entity_id_list):
        summary_text = ' '.join(summary)
        summary_sents = sent_tokenize(summary_text)

        links = set()
        sent_start_token_index = 0

        for sent in summary_sents:
            sent_words = sent.strip().split()
            summary_entities = extract_summary_entities(sent_words, entities)
            summary_numbers = extract_summary_numbers(sent_words)

            sent_links = get_links(entry, summary_entities, summary_numbers) #done ? 

            for each in sent_links:
                s_idx, e_idx, entry_key, type_key = each
                s_idx = sent_start_token_index + s_idx
                e_idx = sent_start_token_index + e_idx
                links.add((s_idx, e_idx, entry_key, type_key))
            sent_start_token_index += len(sent_words)
        link_list.append(links)

    return link_list

def extract_labels(table_list, final_links, summary_list, verbose=False):
    table_labels_list = []
    summary_labels_list = []

    return table_labels_list, summary_labels_list

def main(args):
    
    json_data = json.load(open("scripts/newformat.json", "r"))
    table_list = create_record_data(json_data) #done!

    summary_list = extract_summary_list(json_data) #done?

    entity_id_list = extract_entity_ids(json_data) #game_entity_list

    links = extract_links(json_data, summary_list, entity_id_list) #extract links, can be mostly copied

    final_links= convert_links(json_data, links)

    table_labels_list, summary_labels_list = extract_labels(table_list, final_links, summary_list)
    print(entity_id_list)


def main1(args):
    '''
    Start data preprocessing for general data.
    This will return 
    - a .gtable file which contains the record data ( entity|attribute|value|features )
    - a .summary file which equals the summary with concatenated entity names (e.g. firstname_lastname)
    - a .orig_summary file which equals the summary without concatened entity names (e.g. firstname lastname)
    - a .links file which

    TODO:
    +++ Copy missing functions
    +++ Test if preprocessing results in equal files
    ++  allow to define constants 
    ++  add comments which explain each step
    +   allow for multiple summaries per data field
    +   resolve other TODOs

    '''
    json_data = json.load(open(args.data, 'r'))

    summary_key = 'summary'

    # convert json to table
    #jedes Spiel hat einen Eintrag in der table_list (57)
    table_list = extract_tables(json_data)

    # get summary
    if not args.test_mode:
        entity_dict = extract_entities(json_data)
        summary_list = extract_summary(json_data, summary_key, entity_dict)
        assert len(table_list) == len(summary_list)

        game_entity_list = extract_game_entities(json_data)
        assert len(table_list) == len(game_entity_list)
        links = extract_links(json_data, summary_list, game_entity_list, args.verbose)
        assert len(table_list) == len(links)
        final_links = convert_links(json_data, links)

        table_labels_list, summary_labels_list = extract_labels(table_list, final_links, summary_list, args.verbose)

        with open(args.output + ".gtable", "w") as outf:
            for game in table_list:
                assert all([len(item.split('|')) == 4 for item in game])
                outf.write("{}\n".format(' '.join(game)))
        outf.close()

        with open(args.output + ".summary", "w") as outf:
            for summary in summary_list:
                outf.write("{}\n".format(' '.join(summary)))
        outf.close()

        with open(args.output + ".orig_summary", "w") as outf:
            for game in json_data:
                outf.write("{}\n".format(' '.join(game[summary_key])))
        outf.close()

        with open(args.output + ".links", "w") as outf:
            for links in final_links:
                out_line = ' '.join(sorted(links, key = lambda x:int(x[:x.index(':')])))
                outf.write("{}\n".format(out_line))
        outf.close()

        with open(args.output + ".gtable_label", 'w') as outf:
            for table_labels in table_labels_list:
                outf.write("{}\n".format(' '.join(table_labels)))
        outf.close()

        with open(args.output + ".summary_label", 'w') as outf:
            for summary_labels in summary_labels_list:
                outf.write("{}\n".format(' '.join(summary_labels)))
        outf.close()

if __name__ == '__main__':
    readme = """
    """
    parser = argparse.ArgumentParser(description=readme)
    parser.add_argument("-d", "--data",   required=True, help = "json data")
    parser.add_argument("-o", "--output", required=True, help = "output prefix")
    parser.add_argument('-v', "--verbose", action='store_true', help = "verbose")
    parser.add_argument("-test_mode", default=False, help="testing mode, duh")
    parser.add_argument("-language", default="English", help="Language of your summaries")
    args = parser.parse_args()

    main(args)