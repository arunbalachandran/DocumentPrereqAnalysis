import json
import subprocess, shlex
import sys
import os
from whoosh.index import create_in
from whoosh.fields import *
from whoosh.qparser import QueryParser

with open('prereq_dict_super.json') as fp:
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
    # pdftext = str(pdftext).lower()
    pdftext = str(pdftext).lower().replace(r'\n', '\n')
    abstract_text, abstract_index = 'No abstract found.', ''
    # abstract_text, abstract_index = '', ''
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
    if len(abstract_text) > 1500:
        abstract_text = abstract_text[:1500] + ' ...'
    schema = Schema(title=TEXT(stored=True), path=ID(stored=True), content=TEXT)
    ix = create_in("indexdir", schema)
    writer = ix.writer()
    writer.add_document(title=u"Temp Document", path=u"tempdocuments",
                        content=pdftext)
    writer.commit()
    concept_dict = {}
    with ix.searcher() as searcher:
        for q in prereq_dict:
            query = QueryParser("content", ix.schema).parse(q)
            results = searcher.search(query)
            if (len(results) > 0):
                concept_dict[q] = prereq_dict[q]
                print ('for query', q, results)
    deletion_list = []
    for i in concept_dict:
        temp_dict = {}
        for j in concept_dict:
            if j != i:
                temp_dict[j] = concept_dict[j]
        # if "'" + i + "'" in str(temp_dict):
        if i in str(temp_dict):  # may remove other nodes
            deletion_list.append(i)
    if deletion_list:
        for j in deletion_list:
            del concept_dict[j]
    return (concept_dict, abstract_text)
