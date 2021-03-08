import argparse
import subprocess
import sys
import random

def data_extraction(args):
    print("data_extraction")
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
    #start args.data_extractor


def vocab_extraction(args):
    print("vocab")
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

def split_train_valid_data(args, train_ratio):
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
    # split = int(train_ratio * len(gtable))
    # train_gtable = gtable[:split], valid_gtable = gtable[split:]
    # and so on with other lists
    assert 0 < train_ratio <= 1, "train ratio has to be in (0,1]"
    gtable_file = open(args.table, "r").read()
    gtable_label_file = open(args.table_label, "r").read()
    summary_file = open(args.summary, "r").read()
    summary_label_file = open(args.summary_label, "r").read()

    gtable = gtable_file.strip().split("\n")
    gtable_label = gtable_label_file.strip().split("\n")
    summary = summary_file.strip().split("\n")
    summary_label =summary_label_file.strip().split("\n")
    
    print(" gtable {} | gtable_label {} | summary {} | summary_label {}".format(len(gtable), len(gtable_label), len(summary), len(summary_label)))

    assert len(gtable) == len(gtable_label) == len(summary) == len(summary_label)
    full_data = list(zip(gtable, gtable_label, summary, summary_label))
    random.shuffle(full_data)

    split = int(train_ratio * len(gtable))

    train_data = full_data[split:]
    valid_data = full_data[:split]
    train_gtable, train_gtable_label, train_summary, train_summary_label = zip(*train_data)
    valid_gtable, valid_gtable_label, valid_summary, valid_summary_label = zip(*valid_data)
    
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
    print("binarize")
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
    subprocess.call([sys.executable, args.summary_preprocessor, '--summary', args.summary, '--summary_vocab', args.summary_vocab_file, '--summary_label', args.summary_label])
    subprocess.call([sys.executable, args.table_preprocessor, '--table', args.table, '--table_vocab', args.gtable_vocab_file, '--table_label', args.gtable_label])

def start_model(args):
    print("Starting model...")
    '''

    '''

def main(args):
    print("go")
    data_extraction(args)

    vocab_extraction(args)

    split_train_valid_data(args, 0.5)

    #binarize_data(args)

    #start_model(args)

if __name__ == '__main__':
    readme = """
    TODO: Remove testing defaults!
    """
    string = "test1"

    parser = argparse.ArgumentParser(description=readme)
    parser.add_argument("-data", "-d", default="newformat.json", help = "Input data as JSON (see format)")
    parser.add_argument("-data_extractor", "-de", default="UDE.py", help="Script which turns your table data into files readable to your model")
    parser.add_argument("-vocab_extractor", "-ve", default="extract_vocab.py", help="Script which creates the vocabulary of your summaries")

    parser.add_argument("-output_prefix", "-o", help="output prefix")

    parser.add_argument("-table", "-t", default=string+".gtable", help="Table data")
    parser.add_argument("-summary", "-s", default=string+".summary", help="summary data")

    parser.add_argument("-table_label", default=string+".gtable_label", help="Table label data")
    parser.add_argument("-summary_label", default=string+".summary_label", help="Summary label file location")


    parser.add_argument("-verbose", action="store_true", help="Verbose Mode")
    parser.add_argument("-l", "-language", default="English", help="Language of your summaries")


    args = parser.parse_args()

    if args.output_prefix is None:
        file_prefix = args.data.split('.')[0]
        args.output_prefix = file_prefix

        if args.table is None:
            args.table = '{}.gtable'.format(file_prefix)

        if args.summary is None:
            args.summary = '{}.summary'.format(file_prefix)

    
    main(args)