import csv
import json
import subprocess
import os
import sys
import getopt
from tabulate import tabulate


def get_final_results(dirpath):

    if dirpath[-1] == '/':
        dirpath = dirpath[0:-1]
    model_name = dirpath.split('/')[-1] + '/'

    model_dir = '../Baseline/OpenNMT-py/' + model_name
    evaluation_dir = model_name

    configurations = [item for item in os.listdir(model_dir)]

    fieldnames = ['Configuration', 'RNN_type', 'RNN_size', 'Epochs', 'ENC_layers', 'F1_dev', 'F1_unseen']

    with open(evaluation_dir + 'Configurations_Comparison.csv', 'w', encoding="utf8") as csvfile:
        table = [fieldnames]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for config in configurations:
            config_json = {}
            evaluation_dev = 0
            evaluation_unseen = 0
            with open(model_dir + config + '/configuration.json', encoding='utf8') as json_file:
                config_json = json.loads(json_file.read())

            with open(evaluation_dir + config + '/Dev_Evaluation_Results.csv', encoding='utf8') as dev_file:
                reader = csv.DictReader(dev_file)
                for row in reader:
                    type = row['Evaluation_Type']
                    if type == 'TOTAL':
                        evaluation_dev = float(row['F1'])
                        break

            with open(evaluation_dir + config + '/Unseen_Evaluation_Results.csv', encoding='utf8') as unseen_file:
                reader = csv.DictReader(unseen_file)
                for row in reader:
                    type = row['Evaluation_Type']
                    if type == 'TOTAL':
                        evaluation_unseen = float(row['F1'])
                        break
            writer.writerow({'Configuration': config, 'RNN_type': config_json['rnn_type'],
                             'RNN_size': config_json['rnn_size'], 'Epochs': config_json['epochs'],
                             'ENC_layers': config_json['enc_layers'], 'F1_dev': evaluation_dev,
                             'F1_unseen': evaluation_unseen})
            row_list = [config, config_json['rnn_type'], config_json['rnn_size'], config_json['epochs'],
                        config_json['enc_layers'], evaluation_dev, evaluation_unseen]
            table.append(row_list)

        # Create Latex Table
        with open(evaluation_dir + "Configurations_Comparison_Latex_Table.tex", 'w', encoding='utf8') as latex:
            latex.write(tabulate(table, headers="firstrow", tablefmt="latex"))

    return 0


def main(argv):
    usage = 'usage:\npython3 get_final_results.py -i <directory-path>' \
           '\ndirectory-path is the top directory where the evaluation results are saved'
    try:
        opts, args = getopt.getopt(argv, 'i:', ['inputdir='])
    except getopt.GetoptError:
        print(usage)
        sys.exit(2)
    input_data = False
    inputdir = None
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
    print('Directory path is ', inputdir)
    get_final_results(inputdir)


if __name__ == '__main__':
    main(sys.argv[1:])
