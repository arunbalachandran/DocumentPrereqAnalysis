import scholar
from bs4 import BeautifulSoup

querier = scholar.ScholarQuerier()
settings = scholar.ScholarSettings()
querier.apply_settings(settings)

query = scholar.SearchScholarQuery()

def get_query_html(query_txt):
    query.set_words(query_txt)
    html_output = querier.send_query(query)
    # html_txt = open('test.html').read()
    soup = BeautifulSoup(html_output, "html.parser")
    # get rid of unnecessary divs
    soup.find(id="gs_ab").decompose()
    soup.find(id="gs_hdr").decompose()
    # soup.find(id="gs_hdr_lt").decompose()
    soup.find(id="gs_gb").decompose()
    soup.find(id="gs_lnv").decompose()
    soup.find(id="gs_ccl_bottom").decompose()
    # get rid of the links which were not required anyway
    list_divs = soup.findAll("div", {"class": "gs_fl"})
    list_auth = soup.findAll('div', {'class': 'gs_rs'})

    # get rid of scripts
    for script in soup.head.findAll('script'):
        try:
            script.decompose()
        except:
            pass

    for script in soup.body.findAll('script'):
        try:
            script.decompose()
        except:
            pass
    # get rid of breaks
    print ('getting rid of breaks')
    # for div in list_auth:
    #     for element in div.findAll('br'):
    #         element.unwrap()
    #     print (str(div), 'should have no breaks')
    # get rid of hrefs
    for div in list_divs:
        list_links = div.find_all('a')
        for link in list_links:
            if link.get('href'):
                if 'http' not in link['href']:
                    print ('link is ', str(link))
                    # input()
                    if 'Cited' not in link.text:
                        link.decompose()
                    else:
                        link['href'] = '#'
                    # link['href'] = '#'
    # get rid of author links
    list_auth_on_scholar = soup.findAll("div", {"class": "gs_a"})
    for auth in list_auth_on_scholar:
        try:
            auth.a['href'] = '#'
    return str(soup)
