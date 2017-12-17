import sys
import getopt
from webnlg_baseline_input import input_files


def main(argv):
    usage = 'usage:\npython3 gener_relex.py -i <data-directory> -f <prediction-file> -d <rplc_list-file>' \
           '\ndata-directory is the directory where you unzipped the archive with data' \
            '\nprediction-file is the path to the generated file baseline_predictions.txt ' \
            '(e.g. documents/baseline_predictions.txt)' \
            '\nrplc_list-file is the path to the generated file rplc_list_dev_order.json or ' \
            'rplc_list_unseen_order.json'

    try:
        opts, args = getopt.getopt(argv, 'i:f:d:', ['inputdir=', 'filedir=', 'relexfile='])
    except getopt.GetoptError:
        print(usage)
        sys.exit(2)
    input_data = False
    input_filepath = False
    input_relexpath = False
    for opt, arg in opts:
        if opt in ('-i', '--inputdir'):
            inputdir = arg
            input_data = True
        elif opt in ('-f', '--filedir'):
            filepath = arg
            input_filepath = True
        elif opt in ('-d', '--relexfile'):
            relexpath = arg
            input_relexpath = True
        else:
            print(usage)
            sys.exit()
    if not input_data or not input_filepath or not input_relexpath:
        print(usage)
        sys.exit(2)
    print('Input directory is', inputdir)
    print('Path to the file is', filepath)
    print('Path to relexicalisation dictionary file is', relexpath)
    input_files(inputdir, filepath, relexpath, relex=True)

if __name__ == "__main__":
    main(sys.argv[1:])
