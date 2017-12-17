import csv
import subprocess
import os
import sys
import getopt
from tabulate import tabulate


def multiple_evaluations(dir_path):
    if dir_path[-1] == "/":
        dir_path = dir_path[0:-1]
    model_name = dir_path.split('/')[-1] + '/'

    # Create model directory
    subprocess.call("mkdir " + model_name, shell=True)

    # Dev data
    source_triple_dev = dir_path + '/preprocessed_data/dev-webnlg-all-notdelex.triple'
    info_dev = dir_path + '/preprocessed_data/dev-eval_info-all-notdelex.txt'

    # Unseen data
    source_triple_unseen = dir_path + '/preprocessed_data/unseen-webnlg-all-notdelex.triple'
    info_unseen = dir_path + '/preprocessed_data/unseen-eval_info-all-notdelex.txt'

    # Categories
    # Seen
    with open(info_dev,"r", encoding="utf8") as devEval:
        Evaluation_dev = [line.replace('\n','').split(' ') for line in devEval]
        temp_dev_set = set()
        for (index, item) in enumerate(Evaluation_dev):
            temp_dev_set.add(item[1])
        seenCategories = list(temp_dev_set)

    # Unseen
    with open(info_unseen, "r", encoding="utf8") as devEval:
        Evaluation_unseen = [line.replace('\n', '').split(' ') for line in devEval]
        temp_unseen_set = set()
        for (index, item) in enumerate(Evaluation_unseen):
            temp_unseen_set.add(item[1])
        unseenCategories = list(temp_unseen_set)

    configurations = [item for item in os.listdir(dir_path + '/relexicalised_predictions/')]

    for conf in configurations:
        # Data
        prediction_dev = dir_path + '/relexicalised_predictions/' + conf + '/dev_relexicalised_predictions_triples.txt'
        prediction_unseen = dir_path + '/relexicalised_predictions/' + conf + \
                            '/unseen_relexicalised_predictions_triples.txt'

        # Create directory for each configuration
        subprocess.call("mkdir " + model_name + conf, shell=True)
        evaluation(source_triple_dev, prediction_dev, Evaluation_dev, seenCategories, model_name + conf + '/Dev_')
        evaluation(source_triple_unseen, prediction_unseen, Evaluation_unseen, seenCategories,
                   model_name + conf+ '/Unseen_', UNSEEN=(conf=="config1"))


def tripleEvaluation(indices, Ground_truths, Predictions, FLAG=False):
    matches = []
    token = '<tripleToken>'

    # To evaluate the triples, Recall and Precision are used.
    # FP (False Positive): is a triple predicted but wrong
    # FN (False Negative): is a triple that was not predicted, is missed. For example: the goal is t1 t2 t3 and
    # the prediction is t1 t2 then t3 will be missed and therefore counted as FN
    # TP (True Positive): is a correct predicted triple
    # TN (True Negative): will never be more than 0

    TP = 0
    TN = 0
    FP = 0
    FN = 0
    total = 0

    # Informative data
    # total_match: total of correct predictions (100% accuracy)
    # total_less: total predictions with less triples than the goal
    # total_more: total predictions with more triples than the goal
    total_match = 0
    total_less = 0
    total_more = 0

    for i in indices:
        ground_triples = Ground_truths[i].split(token)
        prediction_triples = Predictions[i].split(token)

        total_tr_goal = len(ground_triples)
        total_tr_prediction = len(prediction_triples)


        if total_tr_goal > total_tr_prediction:
            FN += total_tr_goal - total_tr_prediction
            total += total_tr_goal
            if FLAG:
                print("total_p: "+ str(total_tr_prediction) + " total_g: " + str(total_tr_goal))
                print(ground_triples)
                print(prediction_triples)
            total_less += 1
        else:
            total += total_tr_prediction

        if total_tr_prediction > total_tr_goal:
            total_more += 1

        correct_seen_triples = []
        local_TP = 0
        for prediction in prediction_triples:
            if prediction in correct_seen_triples:
                FP += 1

            if prediction in ground_triples:
                TP += 1
                local_TP += 1
                correct_seen_triples.append(prediction)
            else:
                FP += 1
        if total_tr_prediction == total_tr_goal:
            if local_TP == total_tr_goal:
                total_match += 1

    # Recall, Precision, F1, ACC
    R = "{:.3f}".format(TP / (TP + FN)) if (TP + FN) > 0 else "NA"
    P = "{:.3f}".format(TP / (TP + FP)) if (TP + FP) > 0 else "NA"
    F1 = "{:.3f}".format(2*TP / (2*TP + FP + FN)) if (TP + FP + FN) > 0 else "NA"
    ACC = "{:.3f}".format((TP + TN) / total) if total > 0 else "NA"

    return (len(indices), {'R': R, 'P': P, 'F1': F1, 'ACC': ACC,
                           'TOTAL_TRIPLES': total, 'FP': FP, 'FN': FN, 'TP': TP, 'TN': TN, "CLOSE_MATCH": total_match,
                           'TOTAL_MORE_TR': total_more, 'TOTAL_LESS_TR': total_less})


def evaluation(source_triple, prediction, Evaluations, seenCategories, path, UNSEEN=False):
    with open(source_triple,"r", encoding="utf8") as devGround:
        Ground_truths = [line for line in devGround]

    total = [i for i in range(len(Ground_truths))]

    with open(prediction,"r", encoding="utf8") as devPred:
        Predictions = [line for line in devPred]

    seenTriples = []
    unseenTriples = []
    numberTriples = {}
    categoryTriples = {}

    for (index,eachEval) in enumerate(Evaluations):
        tripleCount = int(eachEval[0])
        tripleCategory = eachEval[1]

        if(tripleCategory in seenCategories):
            seenTriples.append(index)
        else:
            unseenTriples.append(index)

        if(tripleCount in numberTriples.keys()):
            numberTriples[tripleCount].append(index)
        else:
            numberTriples[tripleCount] = [index]

        if(tripleCategory in categoryTriples.keys()):
            categoryTriples[tripleCategory].append(index)
        else:
            categoryTriples[tripleCategory] = [index]

    totalResults = tripleEvaluation(total, Ground_truths, Predictions)
    seenResults = tripleEvaluation(seenTriples, Ground_truths, Predictions)
    unseenResults = tripleEvaluation(unseenTriples, Ground_truths, Predictions)

    groupedTriples = [(key,categoryTriples[key]) for key in sorted(categoryTriples)]
    groupedindices = [i for i in groupedTriples]

    categoryResults = [("Category "+str(c),tripleEvaluation(i, Ground_truths, Predictions)) for (c,i) in groupedindices]

    countedTriples = [(key,numberTriples[key]) for key in sorted(numberTriples)]
    groupedindices = [i for i in countedTriples]

    countResults = [("Triples count "+str(c),tripleEvaluation(i, Ground_truths, Predictions, FLAG=(c==1 and UNSEEN)))
                    for (c,i) in groupedindices]

    with open(path + 'Evaluation_Results.csv', 'w', encoding="utf8") as csvfile:
        fieldnames = ["Evaluation_Type","TOTAL_ENTRIES","CLOSE_MATCH", "TOTAL_MORE_TR", "TOTAL_LESS_TR",
                      "TOTAL_TRIPLES", "FN", "FP", "TP", "TN", "ACC", "R", "P", "F1"]
        table = [fieldnames]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for (row, label) in [(totalResults, "TOTAL"), (seenResults, "SEEN"), (unseenResults, "UNSEEN")]:
            writer.writerow({"Evaluation_Type" : label ,"TOTAL_ENTRIES" : row[0],
                         "ACC" : row[1]['ACC'], "R": row[1]['R'], "P": row[1]['P'],
                         "F1": row[1]['F1'], "TOTAL_TRIPLES": row[1]['TOTAL_TRIPLES'],
                         "FN": row[1]['FN'], "FP": row[1]['FP'], "TP": row[1]['TP'],
                         "TN": row[1]['TN'], "CLOSE_MATCH": row[1]['CLOSE_MATCH'],
                         "TOTAL_MORE_TR": row[1]['TOTAL_MORE_TR'],
                         "TOTAL_LESS_TR": row[1]['TOTAL_LESS_TR']})
            # fill table
            row_list = [label, row[0], row[1]['CLOSE_MATCH'], row[1]['TOTAL_MORE_TR'], row[1]['TOTAL_LESS_TR'],
                        row[1]['TOTAL_TRIPLES'], row[1]['FN'], row[1]['FP'], row[1]['TP'], row[1]['TN'], row[1]['ACC'],
                        row[1]['R'], row[1]['P'], row[1]['F1']]
            table.append(row_list)


        for row in [categoryResults, countResults]:
            for (index, item) in enumerate(row):
                writer.writerow({"Evaluation_Type" : item[0].upper() ,"TOTAL_ENTRIES" : item[1][0],
                          "ACC" : item[1][1]['ACC'], "R": item[1][1]['R'], "P": item[1][1]['P'], "F1": item[1][1]['F1'],
                          "TOTAL_TRIPLES": item[1][1]['TOTAL_TRIPLES'], "FN": item[1][1]['FN'], "FP": item[1][1]['FP'],
                          "TP": item[1][1]['TP'], "TN": item[1][1]['TN'],
                          "CLOSE_MATCH": item[1][1]['CLOSE_MATCH'],
                          "TOTAL_MORE_TR": item[1][1]['TOTAL_MORE_TR'],
                          "TOTAL_LESS_TR": item[1][1]['TOTAL_LESS_TR']})
                # fill table
                row_list = [item[0].upper(), item[1][0], item[1][1]['CLOSE_MATCH'], item[1][1]['TOTAL_MORE_TR'],
                            item[1][1]['TOTAL_LESS_TR'], item[1][1]['TOTAL_TRIPLES'], item[1][1]['FN'],
                            item[1][1]['FP'], item[1][1]['TP'], item[1][1]['TN'], item[1][1]['ACC'], item[1][1]['R'],
                            item[1][1]['P'], item[1][1]['F1']]
                table.append(row_list)

        # Create Latex Table
        with open(path + "Latex_Table.tex" , 'w', encoding='utf8') as latex:
            latex.write(tabulate(table, headers = "firstrow",tablefmt="latex"))



def main(argv):
    usage = 'usage:\npython3 Evaluation.py -i <directory-path>' \
           '\ndirectory-path is the top directory where the preprocessed data is saved'
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
    print('Directory path is ', inputdir)
    multiple_evaluations(inputdir)


if __name__ == "__main__":
    main(sys.argv[1:])