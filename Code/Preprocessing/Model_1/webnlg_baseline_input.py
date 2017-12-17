import os
import random
import re
import json
import sys
import getopt
import subprocess
from collections import defaultdict

sys.path.append("/Users/anupamachingacham/Documents/Learning/M2_NLP_Lorraine/DeepLearning/SP-SYNTAX-PAR/Code/Preprocessing/")
# print(sys.path)
from XML_Parser.benchmark_reader import Benchmark

# Top directory where the files are going to be saved
TOP_DIR = 'preprocessed_data/'

with open('../delex_dict.json', encoding="utf8") as data_file:
    # The json file contains the categories from DBPedia. This file is now 111,11 Mb then it needs to be loaded only
    # once during the execution.
    DBPedia = json.load(data_file)


def select_files(topdir, category='', size=(1, 8), unseen=False):
    """
    Collect all xml files from a benchmark directory.
    :param topdir: directory with benchmark
    :param category: specify DBPedia category to retrieve texts for a specific category (default: retrieve all)
    :param size: specify size to retrieve texts of specific size (default: retrieve all)
    :return: list of tuples (full path, filename)
    """
    finaldirs = [topdir + '/' + str(item) + 'triples' for item in range(size[0], size[1])]
    finalfiles = []
    if unseen:
        finaldirs = [topdir]
    for item in finaldirs:
        finalfiles += [(item, filename) for filename in os.listdir(item)]
    if category:
        finalfiles = []
        for item in finaldirs:
            finalfiles += [(item, filename) for filename in os.listdir(item) if category in filename]
    return finalfiles


def delexicalisation(out_src, out_trg, category, properties_objects):
    """
    Perform delexicalisation.
    :param out_src: source string
    :param out_trg: target string
    :param category: DBPedia category
    :param properties_objects: dictionary mapping properties to objects
    :return: delexicalised strings of the source and target; dictionary containing mappings of the replacements made
    """
    # load the global variable in data
    data = DBPedia

    # replace all occurrences of Alan_Bean to ASTRONAUT in input
    delex_subj = data[category]
    delex_src = out_src
    delex_trg = out_trg
    # for each instance, we save the mappings between nondelex and delex
    replcments = {}

    replacement_text = ""

    multiple_triples = out_trg.split('<tripleToken>')

    delex_subj = [i.replace('_', ' ') for i in delex_subj]

    for (index, triple) in enumerate(multiple_triples):
        # <s,p,o>
        triplets = ([i for i in triple.split('<>')])

        # Check if the subject exists in JSON
        if (triplets[0] in delex_subj):

            find_text_1 = triplets[0]

            # Check is the Named entity already has a replacement text or not
            text = [k for (k, v) in replcments.items() if v == find_text_1]

            # check if the text[] is empty or not
            if text:
                replacement_text_1 = text[0]
                triplets[0] = replacement_text_1
            else:

                # If text[] is empty
                k = len(replcments)
                replacement_text_1 = "ENTITY-" + str(k + 1) + " " + category.upper()
                replcments[replacement_text_1] = ' '.join(find_text_1.split())

                triplets[0] = replacement_text_1

            # Replace the same in lex 'sentence' as well

            delex_src = re.sub(find_text_1, replacement_text_1, out_src, flags=re.I)

        # Check if the obkect exists in JSON
        if (triplets[2] in delex_subj):

            find_text_2 = triplets[2]

            # Check is the Named entity already has a replacement text or not
            text = [k for (k, v) in replcments.items() if v == find_text_2]

            # check if the text[] is empty or not
            if text:
                replacement_text_2 = text[0]
                triplets[2] = replacement_text_2

            else:

                # If text[] is empty
                k = len(replcments)
                replacement_text_2 = "ENTITY-" + str(k + 1) + " " + category.upper()
                replcments[replacement_text_2] = ' '.join(find_text_2.split())

                triplets[2] = replacement_text_2

            # Replace the same in lex 'sentence' as well

            delex_src = re.sub(find_text_2, replacement_text_2, delex_src, flags=re.I)

        multiple_triples[index] = '<>'.join(triplets)

    delex_trg = '<tripleToken>'.join(multiple_triples)

    delex_src = delex_src.strip()
    delex_trg = delex_trg.strip()

    for pro, obj in sorted(properties_objects.items()):

        obj_clean = ''.join(
            re.split('(\W)', obj.replace('_', ' ').replace('"', '')))  ## Changed the joining string from space to empty

        replacement_text = ""

        obj_clean = obj_clean.strip()

        # Improved search with regex
        if re.findall(re.escape(obj_clean), delex_src, re.IGNORECASE):

            # Check is the Named entity already has a replacement text or not
            text = [k for (k, v) in replcments.items() if v == obj_clean]

            if text:
                replacement_text = text[0]
            else:

                k = len(replcments)
                replacement_text = "ENTITY-" + str(k + 1) + " " + pro.upper()
                replcments[replacement_text] = ' '.join(obj_clean.split())

            delex_src = re.sub(obj_clean, replacement_text, delex_src, flags=re.I)

        # Improved search with regex
        if re.findall(re.escape(obj_clean), delex_trg, re.IGNORECASE):

            # multiple_triples = delex_trg.split('<tripleToken>')

            # Check is the Named entity already has a replacement text or not
            text = [k for (k, v) in replcments.items() if v == obj_clean]

            if text:
                replacement_text = text[0]
            else:

                k = len(replcments)
                replacement_text = "ENTITY-" + str(k + 1) + " " + pro.upper()
                replcments[replacement_text] = ' '.join(obj_clean.split())

            for (index, triple) in enumerate(multiple_triples):
                # <s,p,o>
                triplets = ([i for i in triple.split('<>')])

                if obj_clean in triplets[2]:
                    triplets[2] = replacement_text

                multiple_triples[index] = '<>'.join(triplets)

            delex_trg = '<tripleToken>'.join(multiple_triples)

    # possible enhancement for delexicalisation:
    # do delex triple by triple
    # now building | location | New_York_City New_York_City | isPartOf | New_York
    # is converted to
    # BUILDING location ISPARTOF City ISPARTOF City isPartOf ISPARTOF
    return delex_src, delex_trg, replcments


def create_source_target(b, options, dataset, delex=True):
    """
    Write target and source files, and reference files for BLEU.
    :param b: instance of Benchmark class
    :param options: string "delex" or "notdelex" to label files
    :param dataset: dataset part: train, dev, test
    :param delex: boolean; perform delexicalisation or not
    :return: if delex True, return list of replacement dictionaries for each example
    """
    source_out = []
    target_out = []
    rplc_list = []  # store the dict of replacements for each example
    eval_info = []  # store the number of triples a lex has and its category. This information will be used in evaluation
    for entr in b.entries:
        tripleset = entr.modifiedtripleset
        lexics = entr.lexs
        category = entr.category
        for lex in lexics:
            triples_list = []
            properties_objects = {}
            for triple in tripleset.triples:
                triples_str = triple.s + '<>' + triple.p + '<>' + triple.o
                properties_objects[triple.p] = triple.o
                triples_list.append(triples_str)
            # A token is added to have separated triples instead of linearised triples. This will be helpful for
            # evaluation, since the order of the triples should not matter for the evalaution but the triples themselves
            triples = '<tripleToken>'.join(triples_list)
            triples = triples.replace('_', ' ').replace('"', '')
            # separate punct signs from text
            # CHANGED to handle semantic parser
            out_src = ''.join(re.split('(\W)', lex.lex))
            out_trg = ''.join(re.split('(\W)', triples))

            if delex:
                out_src, out_trg, rplc_dict = delexicalisation(out_src, out_trg, category, properties_objects)
                rplc_list.append(rplc_dict)
            # delete white spaces
            # delete token used to identify subject, property and object of a triple. '<>'
            out_src = out_src.replace('<>', ' ')
            out_trg = out_trg.replace('<>', ' ')
            source_out.append(' '.join(out_src.split()))
            target_out.append(' '.join(out_trg.split()))
            # create entry for eval_info
            eval_info.append((len(tripleset.triples), category))

    # shuffle two lists in the same way
    random.seed(10)
    if delex:
        corpus = list(zip(source_out, target_out, rplc_list, eval_info))
        random.shuffle(corpus)
        source_out, target_out, rplc_list, eval_info = zip(*corpus)
    else:
        corpus = list(zip(source_out, target_out, eval_info))
        random.shuffle(corpus)
        source_out, target_out, eval_info = zip(*corpus)

    # CHANGED to handle semantic parser
    with open(TOP_DIR + dataset + '-webnlg-' + options + '.lex', 'w+', encoding="utf8") as f:
        f.write('\n'.join(source_out))
    with open(TOP_DIR + dataset + '-webnlg-' + options + '.triple', 'w+', encoding="utf8") as f:
        f.write('\n'.join(target_out))

    # create file used for evaluation. This will help to divide the information into categoies and number of triples
    scr_refs = defaultdict(list)
    if (dataset == 'dev' or dataset == 'unseen') and not delex:
        with open(TOP_DIR + dataset + '-eval_info-' + options + '.txt', 'w+', encoding="utf8")as f:
            eval_info_str = [str(info[0]) + ' ' + info[1] for info in eval_info]
            f.write('\n'.join(eval_info_str))

    # create files with rplc_list information to be used later during relexicalisation
    if (dataset == 'dev' or dataset == 'unseen') and options == 'all-delex':
        rplc_list_dict = {'rplc_list': rplc_list}
        with open(TOP_DIR + 'rplc_list_' + dataset + '_order.json', 'w+', encoding="utf8") as f:
            json.dump(rplc_list_dict, f)

    return rplc_list


def relexicalise(predfile, rplc_list):
    """
    Take a file from seq2seq output and write a relexicalised version of it.
    :param rplc_list: list of dictionaries of replacements for each example (UPPER:not delex item)
    :return: list of predicted sentences
    """
    relex_predictions = []
    with open(predfile, 'r', encoding="utf8") as f:
        predictions = [line for line in f]
    for i, pred in enumerate(predictions):
        # replace each item in the corresponding example
        rplc_dict = rplc_list[i]
        relex_pred = pred
        for key in sorted(rplc_dict):
            # Problem with space, is not replaced when the key is followed by \n.
            # Without the space, the replacement should be straightforward
            relex_pred = relex_pred.replace(key, rplc_dict[key])
        relex_predictions.append(relex_pred)

    with open('relexicalised_predictions_triples.txt', 'w+', encoding="utf8") as f:
        for prediction in relex_predictions:
            f.write(prediction)

    return relex_predictions


def input_files(path, filepath=None, relexpath=None, relex=False):
    """
    Read the corpus, write train and dev files.
    :param path: directory with the WebNLG benchmark
    :param filepath: path to the prediction file with sentences (for relexicalisation)
    :param relex: boolean; do relexicalisation or not
    :return:
    """
    parts = ['train', 'dev', 'unseen']
    options = ['all-delex', 'all-notdelex']  # generate files with/without delexicalisation

    if relex and relexpath:
        # Should perform relexicalisation
        with open(relexpath, 'r', encoding="utf8") as f:
            rplc_list = json.load(f)['rplc_list']
        relexicalise(filepath, rplc_list)
    else:
        # Create top directory where the files are going to be saved
        subprocess.call("mkdir " + TOP_DIR, shell=True)

        # Should perform delexicalisation
        for part in parts:
            for option in options:
                if part == 'unseen':
                    files = select_files(path + part, unseen=True)
                else:
                    files = select_files(path + part, size=(1, 8))
                b = Benchmark()
                b.fill_benchmark(files)
                if option == 'all-delex':
                    rplc_list = create_source_target(b, option, part, delex=True)
                    print('Total of {} files processed in {} with {} mode'.format(len(files), part, option))
                elif option == 'all-notdelex':
                    rplc_list = create_source_target(b, option, part, delex=False)
                    print('Total of {} files processed in {} with {} mode'.format(len(files), part, option))

    print('Files necessary for training/evaluating are written on disc.')


def main(argv):
    usage = 'usage:\npython3 webnlg_baseline_input.py -i <data-directory>' \
            '\ndata-directory is the directory where you unzipped the archive with data'
    try:
        opts, args = getopt.getopt(argv, 'i:', ['inputdir='])
    except getopt.GetoptError:
        print(usage)
        sys.exit(2)
    input_data = False
    for opt, arg in opts:
        if opt in ('-i', '--inputdir'):
            inputdir = arg
            input_data = True
        else:
            print(usage)
            sys.exit()
    if not input_data:
        print(usage)
        sys.exit(2)
    print('Input directory is ', inputdir)
    input_files(inputdir)


if __name__ == "__main__":
    main(sys.argv[1:])
