import json
import subprocess, shlex
import sys
import os
import search_two_thirds

with open('prereq_dict.json') as fp:
    prereq_dict = json.load(fp)
system_encoding = sys.stdout.encoding

def get_concepts(filepath):
    # make this platform independent
    print ('filepath is ', filepath)
    filename = os.path.basename(filepath)
    original_path = os.getcwd()
    os.chdir(os.path.abspath(os.path.join(filepath, os.pardir)))
    print ('changed directory to', os.getcwd())
    if sys.platform == 'win32':
        cmd = 'gswin64c -q -dNODISPLAY -dSAFER -dDELAYBIND -dWRITESYSTEMDICT -dSIMPLE -c save -f ps2ascii.ps ' + filename + ' -c quit'
        proc = subprocess.Popen(shlex.split(cmd, posix=False), stdout=subprocess.PIPE)  # don't need the posix option if the filesystem is not windows
    else:
        cmd = 'gs -q -dNODISPLAY -dSAFER -dDELAYBIND -dWRITESYSTEMDICT -dSIMPLE -c save -f ps2ascii.ps ' + filename + ' -c quit'
        proc = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE)  # don't need the posix option if the filesystem is not windows
    pdftext, stderr = proc.communicate()
    pdftext = str(pdftext).lower().replace(r'\n', '\n')
    abstract_text, abstract_index = 'No abstract found.', ''
    sentences = pdftext.split('\n')
    for index, sentence in enumerate(sentences):
        if 'abstract' in sentence.split():
            abstract_index = index
    temp_list = []
    if abstract_index:
        for sentence in sentences[abstract_index+1:]:
            temp_list.append(sentence)
            if '1. introduction' in sentence:
                break
        abstract_text = ' '.join(temp_list[:-1])
        abstract_text = abstract_text.strip().title()
    print ('command is', cmd)
    os.chdir(original_path)
    print ('changed back to', os.getcwd())
    # print ('text is', pdftext)
    concept_dict = {}
    for q in prereq_dict:
        if search_two_thirds.search(pdftext, q):
            concept_dict[q] = prereq_dict[q]
    if len(abstract_text) > 1500:
        abstract_text = abstract_text[:1500] + ' ...'

    return (concept_dict, abstract_text)
