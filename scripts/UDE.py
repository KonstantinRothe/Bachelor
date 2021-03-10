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

def get_entities_from_group(entry, group):
    ret = []
    for _id in group:
        for entity in entry[args.entities_key]:
            if entry[args.entities_key][entity][args.identifier_key] == _id:
                ret.append(entry[args.entities_key][entity])
    assert len(group) == len(ret)
    return ret

def get_group_data(entry, group_ids):
    ret = []
    for group in entry[args.group_key]:
        if entry[args.group_key][group][args.identifier_key] in group_ids:
            ret.append(entry[args.group_key][group])
    assert len(group_ids) == len(ret)
    return ret

def create_record_data(json_data):
    ret = []
    for entry in json_data:
        records = []
        entity_attributes, group_attributes = get_all_attributes(entry)
        grouped_entities = get_entity_index(entry)
        biggest_group_size = bgs(grouped_entities)
        #create entity record data
        for g in grouped_entities.keys():
            e_list = get_entities_from_group(entry, grouped_entities[g])
            assert len(e_list) <= biggest_group_size
            
            for i in range(biggest_group_size):

                for attribute in entity_attributes:
                    if attribute == args.feature_key:
                        continue
                    try:
                        entity = e_list[i]
                        try:
                            _id = entity[args.identifier_key]
                            val = entity[attribute]
                            features_string = '/'.join(feat for feat in entity[args.feature_key])

                            if isinstance(val, list):
                                val = '/'.join(v for v in val)
                            else:
                                val = entity[attribute].replace(" ", "_")
                            record_string = '{}|{}|{}|{}'.format(_id, attribute, val, features_string)
                        except KeyError:
                            record_string = '{}|{}|{}|{}'.format(_id, attribute, args.not_available, features_string)
                    except IndexError:
                        _id = args.not_available
                        val = args.not_available
                        features_string = args.not_available
                        record_string = '{}|{}|{}|{}'.format(_id, attribute, val, features_string)
                    records.append(record_string)
                        
        #create group record data. It need to iterate a second time over the keys, because the group records
        #have to show up after the entity records in the final table and I couldnt think of a better solution >.<
        group_list = get_group_data(entry, grouped_entities.keys())
        for group in group_list:
            _id = group[args.identifier_key]
            for attribute in group_attributes:
                if attribute == args.feature_key:
                    continue
                try:    
                    val = group[attribute]
                    if isinstance(val, list):
                        val = '/'.join(v for v in val)
                    else:
                        val = group[attribute].replace(" ", "_")
                    record_string = '{}|{}|{}|{}'.format(_id, attribute, val, features_string)
                except KeyError:
                    record_string = '{}|{}|{}|{}'.format(_id, attribute, args.not_available, features_string)

                records.append(record_string)
        ret.append(records)
    return ret

def create_record_data1(json_data):
    '''
    Creates a record of the form entity_id|attribute|value|features
    for each entity, group and non-entity information piece in each game 
    and returns this as a list of lists of strings
    '''
    ret = []
    for entry in json_data:
        records = []
        #record_string = '{}|{}|{}|{}'
        #the table has to contain each entity and group and each entity/group attribute matched
        #to them, no matter if they actually *have* each attribtue. this will build the
        #internal table realization

        for _dict in entry:
            if _dict == args.non_entity_records_key:
                #create records for non entities
                for attribute in entry[_dict]:
                    record_string = '{}|{}|{}|{}'.format('N/A', attribute, entry[_dict][attribute], 'N/A')
                    #print(record_string)
                    records.append(record_string)
            elif _dict == args.entities_key or _dict == args.group_key:
                for entity in entry[_dict]:
                    #extract feature list
                    features_list = entry[_dict][entity][args.feature_key]
                    features_string = '/'.join(feat for feat in features_list)
                    #get unique entity id
                    idx = entry[_dict][entity][args.identifier_key]
                    #get attributes and values
                    for attribute in entry[_dict][entity]:
                        #skip features, because we caught them earlier
                        if attribute == args.feature_key:
                            continue
                        #if attribute is a list, make a new record for each list element
                        if isinstance(entry[_dict][entity][attribute], list):
                            for attr in entry[_dict][entity][attribute]:
                                record_string = '{}|{}|{}|{}'.format(idx, attribute, attr, features_string)
                        else:
                            #safety replace all whitespaces with underscores
                            val = entry[_dict][entity][attribute].replace(' ', '_')
                            record_string = '{}|{}|{}|{}'.format(idx, attribute, val, features_string)
                            records.append(record_string)
                        #print(record_string)  
            else: #for example summary
                continue
        ret.append(records)
    return ret      

def extract_summary_list(json_data):
    '''
    Extract the summary tokens as a list 
    '''
    summaries = []
    for entry in json_data:
        s = entry[args.summary_key]
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
        for entity in entry[args.entities_key]:
            idx = "e{}".format(entry[args.entities_key][entity][args.identifier_key])
            #try to get the naming attribute. as its not necessary, we have to failcheck
            try:
                name = entry[args.entities_key][entity][args.entity_text_attribute_key]
            except KeyError:
                name = args.not_available
            entity_dict[name] = idx
        #do the same for groups
        for group in entry[args.group_key]:
            idx = "g{}".format(entry[args.group_key][group][args.identifier_key])
            try:
                name = entry[args.group_key][group][args.group_text_attribute_key]
            except KeyError:
                name = args.not_available
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
    '''
    ret = dict()

    for group in entry[args.group_key].keys():
        g_list = []
        g_key = entry[args.group_key][group][args.identifier_key]
        for ent in entry[args.entities_key].keys():
            if(g_key in entry[args.entities_key][ent][args.grouping_key]):
                g_list.append(entry[args.entities_key][ent][args.identifier_key])
        ret[g_key] = g_list
    return ret

def get_all_attributes(entry):
    ''' 
    Returns two lists which contain all unique attributes of entities and groups respectively
    '''
    all_entity_attributes = set()
    all_group_attributes = set()
    
    for group in entry[args.group_key]:
        for key in entry[args.group_key][group].keys():
            all_group_attributes.add(key)
    for entity in entry[args.entities_key]:
        for key in entry[args.entities_key][entity].keys():
            all_entity_attributes.add(key)

    return sorted(list(all_entity_attributes)), sorted(list(all_group_attributes))

def get_group_list(entry):
    groups = set()
    for group in entry[args.group_key]:
        groups.add(entry[args.group_key][group][args.identifier_key])
    return sorted(list(groups))

def bgs(grouped_entity_dict):
    '''Returns the max amount of entities in a single group (biggest group size).'''
    return max(len(each) for each in grouped_entity_dict.values())

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
        grouped_entity_dict = get_entity_index(entry)
        group_list = get_group_list(entry)
        biggest_group_size = bgs(grouped_entity_dict) 

        entry_align = []
        for each_link in links:
            start_index, end_index, identifier, attribute = each_link
            _id = identifier[1:]
            #offsets represent the position of a reference to an entity/group - attribute pair in the data
            #|    independent  |||         entities w/o group         |||       entities in group 0          |||        entities in group 1         |||     group attributes  |
            #|                 |||     entity 3    ||       ...       |||     entity 0    ||     entity 1    |||     entity 1    ||     entity 2    |||  group 0  |  group 1  |
            #| iA0 | ... | iA3 ||| eA0 | ... | eA5 || ... | ... | ... ||| eA0 | ... | eA5 || ... | ... | ... ||| eA0 | ... | eA5 || eA0 | ... | eA5 ||| gA0 | gA1 | gA0 | gA2 |

            # eA0 here is the first entity attribute (here: 5 total)
            # gA0 is the first group attribute (here: 2 total)
            #entities that appear in more than one group get more than one entry
            #entity entries are grouped by groups (duh!) and sorted by index in group

            #offset is calculated as: max_amount_of_entity_attributes * (group_index * biggest_group_size + entity_index)
            #eg entity (idx 0) in group (idx 0), max 5 attributes and max 3 entities per group:
            # 5 * (0 * 3 + 0) = 0 --> of course the first entity doesnt need an offset
            # entity (idx 1) in group (idx 0), ...
            # 5 * (0 * 3 + 1) = 5 --> needs offset of 5 because these entries are occupied by entity idx 0 
            # entity (idx 2) in group (idx 1), ...
            # 5 * (1 * 3 + 2) = 25
            if identifier.startswith("e"): # entity
                key_offset = all_entity_attributes.index(attribute)
                for group in group_list:
                    current_group = grouped_entity_dict[str(group)]
                    if _id in current_group:
                        group_index = group_list.index(group)
                        entity_index = current_group.index(_id)
                        entry_offset = len(all_entity_attributes) * (group_index * biggest_group_size + entity_index)

            #group indices directly follow entity indices
            #base_offset = amount_of_groups * biggest_group_size * amount_of_entity_attributes
            #the entry offset = base_offset + group_index * amount_of_group_attributes
            #eg 2 groups, max 3  entities, each has 5 attributes
            #base_offset = 2 * 3 * 5 = 30
            #group idx 0, 3 group attributes
            #entry_offset = 30 + 0 * 3 = 30 --> first group, no further offset needed
            #group idx 1, ...
            #entry_offset = 30 + 1 * 3 = 33 --> first group needs 3 spaces for its attributes
            if identifier.startswith("g"): # group
                key_offset = all_group_attributes.index(attribute)
                group_index = group_list.index(_id)
                base_offset = len(group_list) * biggest_group_size * len(all_entity_attributes)
                entry_offset = base_offset + group_index * len(all_group_attributes)
            index_in_table = entry_offset + key_offset

            links_str = "{}:{}-{}".format(start_index, end_index, index_in_table)
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
                for entity in entry[args.entities_key]:
                    e = entry[args.entities_key][entity]
                    #search for the fitting entity in data
                    if e[args.identifier_key] == entity_type[1:]:
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
                for group in entry[args.group_key]:
                    g = entry[args.group_key][group]
                    if g[args.identifier_key] == entity_type[1:]:
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
                start_index, end_index, entry_key, type_key = each
                start_index = sent_start_token_index + start_index
                end_index = sent_start_token_index + end_index
                links.add((start_index, end_index, entry_key, type_key))
            sent_start_token_index += len(sent_words)
        link_list.append(links)

    return link_list

def extract_labels(table_list, final_links, summary_list, verbose=False):
    '''
    Unpacks the table information (created before via convert_links) and summary information into two 
    Lists of 0's and 1's for each entry. 
    '''
    assert len(table_list) == len(final_links) == len(summary_list) #allow for more summaries
    table_labels_list = []
    summary_labels_list = []

    for table, links, summary_content in zip(table_list, final_links,  summary_list):
        table_contents = [each.split('|')[2] for each in table]
        #print(table_contents)
        table_size = len(table_contents)
        summary_size = len(summary_content)
        selected_content_set = set()
        summary_entities_set = set()

        for link in links:
            parts = link.strip().split('-')
            assert len(parts) == 2
            position_in_table = int(parts[1])

            indices = parts[0].strip().split(':')
            assert len(indices) == 2
            from_index = int(indices[0])
            to_index = int(indices[1])

            assert position_in_table < table_size, "Pos {} Size {}".format(position_in_table, table_size)
            selected_content_set.add(position_in_table)

            for idx in range(from_index, to_index):
                assert idx < summary_size, idx
                summary_entities_set.add(idx)
    
        table_labels = [0] * table_size
        for each in selected_content_set:
            table_labels[each] = 1

        summary_labels = [0] * summary_size
        for each in summary_entities_set:
            summary_labels[each] = 1

        table_labels_list.append([str(label) for label in table_labels])
        summary_labels_list.append([str(label) for label in summary_labels])
    return table_labels_list, summary_labels_list

def main(args):
    
    json_data = json.load(open(args.data, "r"))
    table_list = create_record_data(json_data) 

    summary_list = extract_summary_list(json_data)

    entity_id_list = extract_entity_ids(json_data) 

    links = extract_links(json_data, summary_list, entity_id_list) 

    final_links= convert_links(json_data, links)

    table_labels_list, summary_labels_list = extract_labels(table_list, final_links, summary_list)

    #save all the funny files
    with open(args.output + ".gtable", "w") as outf:
        for game in table_list:
            assert all([len(item.split('|')) == 4 for item in game])
            outf.write("{}\n".format(' '.join(game)))
    outf.close()
    print("Wrote gtable!") if args.verbose else 0

    with open(args.output + ".summary", "w") as outf:
        for summary in summary_list:
            outf.write("{}\n".format(' '.join(summary)))
    outf.close()
    print("Wrote summary!") if args.verbose else 0

    with open(args.output + ".orig_summary", "w") as outf:
        for entry in json_data:
            outf.write("{}\n".format(' '.join(entry[args.summary_key])))
    outf.close()
    print("Wrote orig summary!") if args.verbose else 0

    with open(args.output + ".links", "w") as outf:
        for links in final_links:
            out_line = ' '.join(sorted(links, key = lambda x:int(x[:x.index(':')])))
            outf.write("{}\n".format(out_line))
    outf.close()
    print("Wrote links!") if args.verbose else 0

    with open(args.output + ".gtable_label", 'w') as outf:
        for table_labels in table_labels_list:
            outf.write("{}\n".format(' '.join(table_labels)))
    outf.close()
    print("Wrote gtable label!") if args.verbose else 0

    with open(args.output + ".summary_label", 'w') as outf:
        for summary_labels in summary_labels_list:
            outf.write("{}\n".format(' '.join(summary_labels)))
    outf.close()
    print("Wrote summary label!") if args.verbose else 0
    print("Data Extraction Done!")

if __name__ == '__main__':
    readme = """
    """
    parser = argparse.ArgumentParser(description=readme)
    parser.add_argument("-d", "--data",   required=True, help = "json data")
    parser.add_argument("-o", "--output", required=True, help = "output prefix")
    parser.add_argument('-v', "--verbose", action='store_true', help = "verbose")
    parser.add_argument("-language", default="English", help="Language of your summaries")

    #define important keys in the input data
    parser.add_argument("-summary_key", default="summary")
    parser.add_argument("-non_entity_records_key", default="non_entity_records")
    parser.add_argument("-identifier_key", default="identifier")
    parser.add_argument("-entities_key", default="entities")
    parser.add_argument("-entity_text_attribute_key", default="Name")
    parser.add_argument("-grouping_key", default="belongs_to")
    parser.add_argument("-group_key", default="groups")
    parser.add_argument("-group_text_attribute_key", default="Name")
    parser.add_argument("-feature_key", default="features")
    parser.add_argument("-not_available", default="N/A")

    args = parser.parse_args()

    main(args)