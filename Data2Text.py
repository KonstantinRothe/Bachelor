import argparse
import subprocess
import sys
import random
import os

def data_extraction(args):
    print("Extracting data...")
    #check args
    '''
    parser.add_argument("-d", "--data",   required=True, help = "json data")
    parser.add_argument("-o", "--output", required=True, help = "output prefix")
    parser.add_argument('-v', "--verbose", action='store_true', help = "verbose")
    parser.add_argument("-language", default="English", help="Language of your summaries")
    --> 
    Input data.json 
    Output data.gtable, data.summary, data.gtable_label, data.summary_label
    '''
    subprocess.call([sys.executable, args.data_extractor, '-d', args.data, '-o', args.output_prefix])
    print("Extracting data done!")
    #start args.data_extractor


def vocab_extraction(args):
    print("Extracting vocab...")
    #check args
    '''
    parser.add_argument("-t", '--table', dest = 'table', help = "table data") --> .gtable file
    parser.add_argument("-s", '--summary', dest = 'summary', help = "summary data") --> .summary file
    -->
    Input data.gtable, data.summary
    Output data.gtable_vocab, data.summary_vocab
    '''
    #start vocab_extractor
    subprocess.call([sys.executable, args.vocab_extractor, '-t', args.table, '-s', args.summary])
    print("Extracting vocab done!")

def split_train_valid_data(args):
    '''
    Input 
    .gtable, .gtable_label, .summary, .summary_label files, training to validating data ratio
    Output 
    train.gtable, train.gtable_label, train.summary, train.summary_label (train_ratio of Input)
    valid.gtable, valid.gtable_label, valid.summary, valid.summary_label (1-train_ratio of Input)
    '''
    print("Splitting...")
    # basically do
    # full_data = list(zip(gtable, gtable_label, summary, summary_label))
    # random.shuffle(full_data)
    # gtable, gtable_label, summary, summary_label = zip(*full_data)  # * = "unzip"
    # split = int(split_ratio * len(gtable))
    # train_gtable = gtable[:split], valid_gtable = gtable[split:]
    # and so on with other lists
    assert 0 < args.split_ratio < 1, "split_ratio has to be in (0,1)"

    #get the file contents
    gtable_file = open(args.table, "r").read()
    gtable_label_file = open(args.table_label, "r").read()
    summary_file = open(args.summary, "r").read()
    summary_label_file = open(args.summary_label, "r").read()

    #split the content into lists, each for every entry
    gtable = gtable_file.strip().split("\n")
    gtable_label = gtable_label_file.strip().split("\n")
    summary = summary_file.strip().split("\n")
    summary_label = summary_label_file.strip().split("\n")

    assert len(gtable) == len(gtable_label) == len(summary) == len(summary_label)

    #zip and randomize the data with the same order
    full_data = list(zip(gtable, gtable_label, summary, summary_label))
    random.shuffle(full_data)

    #calculate splitting point
    split = int(args.split_ratio * len(gtable))

    #split data into training and validation sets
    train_data = full_data[split:]
    valid_data = full_data[:split]

    #unzip data
    train_gtable, train_gtable_label, train_summary, train_summary_label = zip(*train_data)
    valid_gtable, valid_gtable_label, valid_summary, valid_summary_label = zip(*valid_data)
    

    #save the files
    #train
    with open(args.output_prefix+"_train.gtable", 'w') as outf:
        for table in train_gtable:
            outf.write("{}\n".format(table))
    outf.close()

    with open(args.output_prefix+"_train.gtable_label", 'w') as outf:
        for table in train_gtable_label:
            outf.write("{}\n".format(table))
    outf.close()

    with open(args.output_prefix+"_train.summary", 'w') as outf:
        for table in train_summary:
            outf.write("{}\n".format(table))
    outf.close()

    with open(args.output_prefix+"_train.summary_label", 'w') as outf:
        for table in train_summary_label:
            outf.write("{}\n".format(table))
    outf.close()

    #valid
    with open(args.output_prefix+"_valid.gtable", 'w') as outf:
        for table in valid_gtable:
            outf.write("{}\n".format(table))
    outf.close()

    with open(args.output_prefix+"_valid.gtable_label", 'w') as outf:
        for table in valid_gtable_label:
            outf.write("{}\n".format(table))
    outf.close()

    with open(args.output_prefix+"_valid.summary", 'w') as outf:
        for table in valid_summary:
            outf.write("{}\n".format(table))
    outf.close()

    with open(args.output_prefix+"_valid.summary_label", 'w') as outf:
        for table in valid_summary_label:
            outf.write("{}\n".format(table))
    outf.close()
    print("Splitting done!") 

def binarize_data(args):
    print("Binarizing...")
    '''

    -->
    Preprocess Summary Data
    Input data.summary, data.summary_vocab, data.summary_label
    Output data.summary.pth

    Preprocess Table Data
    Input data.gtable, data.gtable_vocab, data.gtable_label
    Output data.gtable.pth
    '''
    #check args
    #start binarize
    if args.split_data:
        #train
        subprocess.call([sys.executable, args.summary_preprocessor, '--summary', args.output_prefix+"_train.summary", '--summary_vocab', args.output_prefix+".summary_vocab", '--summary_label', args.output_prefix+"_train.summary_label"])
        subprocess.call([sys.executable, args.table_preprocessor, '--table', args.output_prefix+"_train.gtable", '--table_vocab', args.output_prefix+".gtable_vocab", '--table_label', args.output_prefix+"_train.gtable_label"])
        #valid
        subprocess.call([sys.executable, args.summary_preprocessor, '--summary', args.output_prefix+"_valid.summary", '--summary_vocab', args.output_prefix+".summary_vocab", '--summary_label', args.output_prefix+"_valid.summary_label"])
        subprocess.call([sys.executable, args.table_preprocessor, '--table', args.output_prefix+"_valid.gtable", '--table_vocab', args.output_prefix+".gtable_vocab", '--table_label', args.output_prefix+"_valid.gtable_label"])
    else:
        subprocess.call([sys.executable, args.summary_preprocessor, '--summary', args.summary, '--summary_vocab', args.output_prefix+".summary_vocab", '--summary_label', args.output_prefix+".summary_label"])
        subprocess.call([sys.executable, args.table_preprocessor, '--table', args.table, '--table_vocab', args.output_prefix+".gtable_vocab", '--table_label', args.output_prefix+".gtable_label"])
    print("Done binarizing!")

def start_model(args):
    print("Starting model...")
    '''
    Starts the model with the arguments given by parameters.cfg

    '''
    assert os.path.isfile(args.model), args.model
    #replace newlines with spaces. newlines make the parameters.cfg file more readable for humans, but the newline character "\n" is very annoying to deal with otherwise
    #also since the argname and argval are in a single line, we have to split them as well
    raw_model_params = open(args.model_parameters, "r").read().replace("\n", " ")
    model_params = raw_model_params.split(", ")
    subprocess.call([sys.executable, args.model]+ model_params)

def check_dependencies():
    print("Checking dependencies...")

def main(args):
    #data_extraction(args)

    #vocab_extraction(args)

    if args.split_data:
        split_train_valid_data(args)
    binarize_data(args)

    #start_model(args)

if __name__ == '__main__':
    readme = """
    Data To Text Framework by Konstantin Rothe.
    
    """
    string = "data/NFL Crawl/final data/small_NFL"

    parser = argparse.ArgumentParser(description=readme)
    parser.add_argument("-data", "-d", default=string+".json", help = "Input data as JSON (see format)")

    parser.add_argument("-data_extractor", "-de", default="scripts/UDE.py", help="Script which turns your table data into files readable to your model")
    parser.add_argument("-vocab_extractor", "-ve", default="scripts/extract_vocab.py", help="Script which creates the vocabulary of your summaries")

    parser.add_argument("-summary_preprocessor", "-sp", default="model/preprocess_summary_data.py")
    parser.add_argument("-table_preprocessor", "-tp", default="model/preprocess_table_data.py")

    parser.add_argument("-table", "-t", default=string+".gtable", help="Table data")
    parser.add_argument("-summary", "-s", default=string+".summary", help="summary data")

    parser.add_argument("-table_label", default=string+".gtable_label", help="Table label data")
    parser.add_argument("-summary_label", default=string+".summary_label", help="Summary label file location")

    parser.add_argument("-output_prefix", "-o", help="output prefix")

    parser.add_argument("-model", "-m", default="model/train.py", help="Starting point of your model.")
    parser.add_argument("-model_parameters", "-mp", default="config/model_params.cfg", help="Starting parameters for your model")

    parser.add_argument("-split_data", default=True, help="Set to True if you want to split your data set into train and valid.")
    parser.add_argument("-split_ratio", default=0.5, help="Train to validation ratio.")

    parser.add_argument("-verbose", default=False, action="store_true", help="Verbose Mode")
    parser.add_argument("-l", "-language", default="English", help="Language of your summaries")
    parser.add_argument("-check_dependencies", "-cp", default=False, help="Check dependencies and install libraries that may be missing?")

    args = parser.parse_args()

    if args.output_prefix is None:
        args.output_prefix = args.data.split('.')[0]

        if args.table is None:
            args.table = '{}.gtable'.format(args.output_prefix)

        if args.summary is None:
            args.summary = '{}.summary'.format(args.output_prefix)

    
    main(args)