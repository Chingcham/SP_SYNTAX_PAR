"""
    Performs the relexicalisation over the output of the different models results (translate.py)
    predictions_dev.txt predictions_unseen.txt
"""
import subprocess
import os


# Configuration
# change the name of the model in accordance with the parent directory
dir_path = '../../Baseline/OpenNMT-py/Model_1/'
configurations = [item for item in os.listdir(dir_path) if os.path.isdir(os.path.join(dir_path, item))]
relex_dir = 'relexicalised_predictions/'

# Create relex_dir
subprocess.call("mkdir " + relex_dir, shell=True)

parts = ['dev', 'unseen']

for config in configurations:
    for part in parts:
        predictions_file = dir_path + config + "/predictions_" + part + ".txt"
        rplc_file = "preprocessed_data/rplc_list_" + part + "_order.json"
        subprocess.call("python webnlg_relexicalise.py -i ../data-directory/ -f " + predictions_file +
                        " -d " + rplc_file , shell=True)
        # Rename file
        subprocess.call("mv relexicalised_predictions_triples.txt " + part + "_relexicalised_predictions_triples.txt",
                        shell=True)
        # Move to corresponding directory
        directory = relex_dir + config
        subprocess.call("mkdir " + directory, shell=True)
        subprocess.call("mv " + part + "_relexicalised_predictions_triples.txt " + directory, shell=True)