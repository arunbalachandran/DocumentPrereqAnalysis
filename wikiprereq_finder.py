from flask import Flask, request, render_template, json, redirect, jsonify
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
    if (ref_dist != 0):
        try:
            print ("The distance between", conceptA, "and", conceptB, "is ", ref_dist)
        except:
            print ("Cannot print concept")
    return (ref_dist, conceptB)

def get_concepts(filename):
    # is there an alternative?
    cmd = 'gswin64c -q -dNODISPLAY -dSAFER -dDELAYBIND -dWRITESYSTEMDICT -dSIMPLE -c save -f ps2ascii.ps ' + filename + ' -c quit > output.txt'
    os.system(cmd)
    with open('output.txt') as fp:
        keywords = fp.read().split()
    # future scope -> check bigrams and trigrams and also improve simple word checking using search library
    concepts = [concept for concept in set(keywords) if title_links.get(concept)]
    concept_prereq = {}
    if (concepts != []):
        for concept in concepts:    # find prerequisites for each concept
            # simplifying assumption that the links that you have in your page contain the thing that links to you
            concept_prereq[concept] = {}
        recursive_concept_fill(concept_prereq, depth=0, all_concepts=[i for i in concept_prereq])  # depth limited recursive concept fetch
        return concept_prereq
    else:
        print ('No known concepts exist!')
        return 0

def recursive_concept_fill(concept_dict, depth, all_concepts):
    if (depth >= 5):
        return
    # print ('all concepts at this level is ', str(all_concepts))
    for concept in concept_dict:
        # max concept is the prerequisite for that concept
        max_concept = max([ref_distance(concept, article) for article in title_links[concept] if title_links.get(article)], key=lambda x: x[0])
        # print ('max concept is ', max_concept)
        if (not max_concept or max_concept[1] in str(all_concepts)):
            return
        else:
            all_concepts.append(max_concept[1])   # unique concept that doesn't exist anywhere in the dicitonary
            concept_dict[concept][max_concept[1]] = {}
            recursive_concept_fill(concept_dict[concept], depth=depth+1, all_concepts=all_concepts)
