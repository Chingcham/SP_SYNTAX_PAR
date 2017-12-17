An RNN encoder that learns word and label annotation vectors in parallel;
***
# Semantic Parser
This project compares different approaches in delexicalisation for a Semantic Parser, with a RDF (Triple <suj, prop, obj>) representation, for instance:
- text: "Bibbo Bibbowski was created by American, Jerry Ordway."  
- triple representation: (Bibbo Bibbowski creator Jerry Ordway)(Jerry Ordway nationality Americans)  

Particulary, 64 different experiments were executed.  

# Folder structure
.
├── Code  
│   ├── Baseline  
│   ├── Evaluation  
│   └── Preprocessing  
└── Presentation  
    ├── Meeting1  
    ├── Meeting2  
    └── Meeting3  

| Folder Name | Description |
| ----------- | ----------- |
| Code/Baseline   | It contains the OpenNMT code, and the script to run 16  different configurations for training for each model |
| Code/Preprocessing   | It contains the data for training and evaluation. It also containts the different models for delexicalisation and their scripts to preprocess the data. In this folder the relexicalised version of the predictions for each model and each configuration are saved  |
| Code/Evaluation | It contains the results for each model and configuration. The results are given in csv and tex table files. |
| Presentation/Meeting<Number>| Here you can find the pdf and tex files of the presentations for each meeting|

# How many models and configurations are?
- **Models**  
  1. Model 1: The delexicalisation process uses the following replacement ``` ENTITY-N CATEGORY ```  
  2. Model 2: The delexicalisation process uses the following replacement ``` CATEGORY ```    
  3. Model 3: The delexicalisation process uses the following replacement ``` ENTITY-N ```    
  4. Model 4: The delexicalisation process uses the following replacement ``` ENTITY-N CATEGORY|UNKNOWN ```   
- **Configurations**  

| Configuration | RNN Type | RNN size | No. epochs | ENC layers |  
| ------------ | -------- | ---------| -----------| -----------|  
| Confi1   | LSTM   | 500 | 13 | 2 |  
| Confi2   | LSTM   | 500 | 20 | 2 |  
| Confi3   | LSTM   | 500 | 27 | 2 |  
| Confi4   | GRU   | 500 | 13 | 2 |  
| Confi5   | GRU   | 500 | 20 | 2 |  
| Confi6   | GRU   | 500 | 27 | 2 |  
| Confi7   | LSTM   | 500 | 13 | 5 |  
| Confi8   | GRU   | 500 | 13 | 5 |  
| Confi9   | LSTM   | 500 | 13 | 8 |  
| Confi10   | GRU   | 500 | 13 | 8 |  
| Confi11   | LSTM   | 700 | 13 | 2 |  
| Confi12   | GRU   | 700 | 13 | 2 |  
| Confi13   | LSTM   | 900 | 13 | 2 |  
| Confi14   | GRU   | 900 | 13 | 2 |  
| Confi15   | LSTM   | 700 | 20 | 5 |  
| Confi16   | GRU   | 700 | 20 | 5 |  

# How to execute the scripts?
All the files obtained during executions are available in their respective folder. However, if you still want to execute the scripts please following instructions. It is very important to maintain the folder structure. Since you want to re-run scripts, it is recommended to copy the model you want to execute in a new folder in Preprocessing folder and rename it.  

For example, lets say you want to execute Model_3, what it is recommended is to copy the folder Code/Preprocessing/Model_3 and rename it, after that delete ppreprocessed_data and relexicalised_predictions folders.

## 1. Preprocessing

In this step all the input data for traning, test (during training) and evaluation (of the resulting model) is preprocessed. The delexicalisation is done in this step. To execute this step please run the following command:  
```
cd Code/Preprocessing/Model_N
python webnlg_baseline_input.py -i ../data-directory/
```
../data-directory/ is the path to the directory where the input data is saved. This will create the folder prerpocessed_data with .lex and .triple files whit the preprocessed data, also .json files what contains the dictionaries to be used in the relexicalisation step.

## 2. Baseline/OpenNMT-py

Once the data has been preprocessed, the training process can be execute. This procedure uses a GPU, be sure you have an available GPU, if not this process cannot be execute. Please exexcute the following commands to execute the 16 different configurations for your model.   
```
cd Code/Baseline/OpenNMT-py/
python multiple_executions.py -i ../../Preprocessing/Model_N/
```
This will create 16 folders with the results for each configuration. Usually this procedure takes around 5 hours in a computer with a Nvidia GPU GT X1050 Ti 4GB DDR5, and a CPU Ci7 7700 HQ 6M Cache 2,8 GHz.

## 3. Relexicalisation

With the predictions, the next step is to relexicalise them. To do so it is neccessary to change multiple_relexicalisation.py in line 11 change the dir_path to ``` dir_path = '../../Baseline/OpenNMT-py/Model_N/' ``` .
After that you are ready to execute the relexicalisation:
```
cd Code/Preprocessing/Model_N/
python multiple_relexicalisation.py
```
This will generate the relexicalised version of the predictions for each configuration, those will be saved in relexicalised_predictions folder.  

## 4. Evaluation

Finally to evaluate the results of the model you should run the evaluation script. 
```
cd Code/Evaluation/
python Evaluation.py -i ../Preprocessing/Model_N/
```
This will create a new folder Model_N with the evaluation results for every configuration. This evaluations results are given in csv and tex (table) format. There you can find the values for accuracy, precision, recall and F1 measure.


Project Team: Maria Andrea Cruz Blandon, Anupama Chingacham
