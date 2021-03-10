#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2019-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#


"""
Example: python data/vocab.txt data/train.txt
vocab.txt: 1stline=word, 2ndline=count
"""

import os
import numpy as np
import sys
import argparse
import torch

from src.data.dictionary import Dictionary

def print_args(args):
    print("table:\t{}".format(args.table))
    print("table_label:\t{}".format(args.table_label))
    print("table_vocab:\t{}".format(args.table_vocab))

def main(args):
    if args.table_label is None:
        args.table_label = args.table + "_label"
    if args.table_vocab is None:
        args.table_vocab = args.table + "_vocab"

    assert os.path.isfile(args.table)
    assert os.path.isfile(args.table_label)
    assert os.path.isfile(args.table_vocab)

    print_args(args)

    table_dico = Dictionary.read_vocab(args.table_vocab)
    
    table_data = Dictionary.index_table(args.table, args.table_label, table_dico, args.table+".pth")

if __name__ == '__main__':
    readme = ""
    parser = argparse.ArgumentParser(description=readme)
    parser.add_argument('--table', help = "table data")
    parser.add_argument('--table_label', help = "table label")
    parser.add_argument('--table_vocab', help = "table vocab")
    args = parser.parse_args()
    main(args)
    

