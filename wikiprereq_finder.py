import json
import subprocess, shlex
import sys
import os

with open('title_links.json') as title_link_dict:
    title_links = json.load(title_link_dict)
system_encoding = sys.stdout.encoding

def weights(conceptA, conceptB):
    if (conceptA in title_links[conceptB]):
        return 1
    return 0

def relation(conceptA, conceptB):
    if (conceptB in title_links[conceptA]):
        return 1
    return 0

def ref_distance(conceptA, conceptB):
    total_weightsA, total_weightsB = 0, 0
    ref_dist = 0.0

    for article in title_links:
        total_weightsA += weights(article, conceptA)
        total_weightsB += weights(article, conceptB)

    if total_weightsA == 0:
        total_weightsA += 1
    elif total_weightsB == 0:
        total_weightsB += 1

    for article in title_links:
        ref_dist += relation(article, conceptB)*weights(article, conceptA)/total_weightsA - relation(article, conceptA)*weights(article, conceptB)/total_weightsB
    if (ref_dist != 0):  # how are the print statements working?
        try:
            print ("The distance between", conceptA, "and", conceptB, "is ", ref_dist)
        except:
            print ("Cannot print concept")
    return (ref_dist, conceptB)

# Search whether the node exists in other nodes as subset
def recursive_search(dictionary, search_key):
    for key in dictionary:
        if key != search_key and "'"+search_key+"'" in str(dictionary[key]):  # don't search for yourself
            return True
    return False

def get_concepts(filepath):
    # make this platform independent
    os.chdir(os.path.join(os.path.abspath(sys.path[0]), 'docs'))
    cmd = 'gswin64c -q -dNODISPLAY -dSAFER -dDELAYBIND -dWRITESYSTEMDICT -dSIMPLE -c save -f ps2ascii.ps ' + filepath + ' -c quit'
    proc = subprocess.Popen(shlex.split(cmd, posix=False), stdout=subprocess.PIPE)  # don't need the posix option if the filesystem is not windows
    pdftext, stderr = proc.communicate()
    pdftext = str(pdftext).lower()
    print ('error is ', str(stderr))
    print ('keywords are ', str(pdftext))
    # print ('keywords are', pdftext)
    # os.system(cmd)
    # with open('output.txt') as fp:
    #    keywords = fp.read().split()
    # future scope -> check bigrams and trigrams and also improve simple word checking using search library
    # how do I reduce the number of concepts? or maybe implement a hide functionality for nodes
    concepts_with_count = []
    for concept in title_links:
        if concept.lower() in pdftext:
            concepts_with_count.append((concept, pdftext.count(concept.lower())))
        elif concept.replace('_', ' ').lower() in pdftext:
            concepts_with_count.append((concept, pdftext.count(concept.replace('_', ' ').lower())))
    # concepts = [concept for concept in title_links if concept.lower() in pdftext or ' '.join(concept.split('_')).lower() in pdftext]
    concepts = [concept[0] for concept in concepts_with_count if concept[1] > 2]    # keep this count variable for experiment
    # remove unnecessary concepts
    concepts = [concept for concept in concepts if concept not in ['(', ')', '{', '}', '[', ']']]
    concept_prereq = {}
    if (concepts != []):
        for concept in concepts:    # find prerequisites for each concept
            concept_prereq[concept] = {}
        sys.stdout.write('\n'+str(concept_prereq)+'\n')
        # simplifying assumption that the links that you have in your page contain the thing that links to you
        # for concept in concept_prereq:
        recursive_concept_fill(concept_prereq, depth=0, all_concepts=concepts) # depth limited recursive concept fetch
        deletion_list = []
        for search_key in concept_prereq:
            if recursive_search(concept_prereq, search_key):
                deletion_list.append(search_key)
        print ('deletion list is', deletion_list)
        # input()
        for key in deletion_list:
            del(concept_prereq[key])
        return concept_prereq
    return concepts  # if none exist

def recursive_concept_fill(concept_dict, depth, all_concepts):
    if (depth >= 5):
        return
    for concept in concept_dict:
        # max concept is the prerequisite for that concept
        print ('concept is ', concept, 'with dict', concept_dict)
        if (title_links.get(concept) != None):
            # super rare case
            list_articles = [ref_distance(concept, article) for article in title_links[concept] if title_links.get(article)]
            if list_articles != []:
                max_concept = max(list_articles , key=lambda x: x[0])
                # need to verify the pruning logic
                # if (max_concept and max_concept[1] not in str(all_concepts)):
                if (max_concept):
                    all_concepts.append(max_concept[1])   # unique concept that doesn't exist anywhere in the dicitonary
                    concept_dict[concept][max_concept[1]] = {}
                    recursive_concept_fill(concept_dict[concept], depth=depth+1, all_concepts=all_concepts)
