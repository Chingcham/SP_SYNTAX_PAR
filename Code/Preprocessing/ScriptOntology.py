# This script Simplifies the file 'instance_types_en.nt'. The output is the file 'Simplified_Types.txt'
import json

instTypes = open('instance_types_en.nt', 'r')

i = 0
dict = {}

entityClass = ""
entityName = ""
iniPosName = 1
lastPosName = 0
iniPosClass = 0
lastPosClass = -2

while i < 28032000:

    line = instTypes.readline()

    if line == '':# eof
        break

    if ("http://schema.org/" in line):
        # Remove the string " <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> " from the file
        text = line.replace(' <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> ', '')
        text = text.replace('http://dbpedia.org/resource/', '')  # Remove the string "<http://dbpedia.org/resource/"
        text = text.replace('http://schema.org/', '')  # Remove the string "http://schema.org/"
        text = text.replace('> .', '>')  # Remove the  " ." at the end of each line
        # At This point we'll have <OBJECT> <ENTITY>

        lastPosName = text.find('><')
        iniPosClass = lastPosName + 2

        entityClass = text[iniPosClass:lastPosClass]
        entityName = text[iniPosName:lastPosName]

        # print("Class: " + entityClass + " Name: " + entityName)
        # print(i)  # Just to see the progress

        # verifies if already have that key on dictionary
        if entityClass in dict:
            dict[entityClass].append(entityName)
        else:  # if doesn't exist, create as vector
            dict[entityClass] = []
            dict[entityClass].append(entityName)
        i += 1

simpJson = open('Simplified_Types.json', 'w')
simpJson.writelines(json.dumps(dict, indent=2, sort_keys=True))
simpJson.close()
instTypes.close()
