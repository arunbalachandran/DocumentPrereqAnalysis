import http.client, urllib.request, urllib.parse, urllib.error, base64
import os
import json
headers = {
    # Request headers
    'Ocp-Apim-Subscription-Key': os.environ.get('ACADEMIC_KEY'),
}

# import microsoft_knowledge_api
# microsoft_knowledge_api.get_paper_data('computer vision')

def get_paper_data(topic_name):
    topic_name = topic_name.lower()
    try:    # first interpret the query and convert to microsoft format
        params = urllib.parse.urlencode({
            # Request parameters
            'query': 'papers in ' + topic_name,
            'complete': '0',
            'count': '1',
            'model': 'latest',
        })
        conn = http.client.HTTPSConnection('westus.api.cognitive.microsoft.com')
        conn.request("GET", "/academic/v1.0/interpret?%s" % params, "{body}", headers)
        response = conn.getresponse()
        # data = response.read()
        str_response = response.read().decode('utf-8')
        data = json.loads(str_response)
        query_to_evaluate = data['interpretations'][0]['rules'][0]['output']['value']
        print('interpreted query', str_response)
        # now evaluate the query
        params = urllib.parse.urlencode({
            # Request parameters
            'expr': query_to_evaluate,
            'model': 'latest',
            'count': '10',
            'offset': '0',
            'attributes': 'Ti,Y,CC,AA.AuN',
        })
        conn.request("GET", "/academic/v1.0/evaluate?%s" % params, "{body}", headers)
        response = conn.getresponse()
        str_response = response.read().decode('utf-8')
        data = json.loads(str_response)
        print('evaluated query is', data)  # data that needs to be interpreted
        conn.close()
        # now generate div elements
        div_str = "<div class='first-div' style='padding-top:2%'>"
        print ('data entities exists? ', data.get('entities', 'false'))
        for i in data['entities']:
            print ('Current entity is', i)
            div_str += "<div class='inner-div' style='padding-top:4%'>"
            print ('currently here 1', div_str)
            div_str += "<p class='title'><b>" + i['Ti'].title() + "</b></p>"
            print ('currently here 2', div_str)
            div_str += "<p class='authors' >Authors are "
            print ('currently here 3', div_str)
            print ('author is', i['AA'])
            div_str += i['AA'][0]['AuN'].title()
            print ('currently here 4', div_str)
            if len(i['AA']) != 1:
                div_str += ' et al.,'
            div_str += "</p>"
            print ('currently here 5', div_str)
            div_str += "<p class='citation' style='display: inline-block;'>Cited by " + str(i['CC']) + " people </p>"
            div_str += "<p class='pub-year' style='display: inline; float: right;'>Published in year " + str(i['Y']) + "</p>"
            div_str += "</div>"
        div_str += "</div>"
        print ('Html being returned is', div_str)
        return div_str
    except Exception as e:
        error_string = 'Error in fetching MCS data'
        # print("[Errno {0}] {1}".format(e.errno, e.strerror))
        return error_string
