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
    soup.head.findAll('title')[0].decompose()    # get rid of title
    # get rid of scripts
    for script in soup.head.findAll('script'):
        try:
            script.decompose()
        except:
            pass

    # get rid of meta elements in head
    for meta in soup.head.findAll('meta'):
        try:
            meta.decompose()
        except:
            pass

    # get rid of style elements in head
    for style in soup.head.findAll('meta'):
        try:
            style.decompose()
        except:
            pass

    for script in soup.body.findAll('script'):
        try:
            script.decompose()
        except:
            pass

    # getting rid of style elements inside body (invalid html supposedly)
    for style in soup.body.findAll('style'):
        try:
            style.decompose()
        except:
            pass

    # get rid of breaks
    print ('getting rid of breaks')
    for div in list_auth:
        for element in div.findAll('br'):
            element.unwrap()
        # print (str(div), 'should have no breaks')
    # get rid of hrefs
    for div in list_divs:
        list_links = div.find_all('a')
        for link in list_links:
            if link.get('href'):
                if 'http' not in link['href']:
                    # print ('link is ', str(link))
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
        except:
            pass
            # print ('couldnt assign href to ', auth.a)

    # this may or may not work - decompose the main gs_top div
    soup.find(id="gs_top").unwrap()
    soup.find(id="gs_md_s").decompose()
    soup.find(id="gs_md_w").decompose()
    soup.find(id="gs_ab_anchor").decompose()
    soup.find(id="gs_rdy").decompose()
    soup.find(id="gs_bdy").unwrap()
    soup.find(id="gs_ccl").unwrap()
    soup.find(id="gs_ccl_top").decompose()
    soup.find(id="gs_ccl_results").unwrap()

    # make the list of floating pdf link divs float to the right of their respective links
    list_pdf_divs = soup.findAll("div", {"class": "gs_ggs"})
    for div in list_pdf_divs:
        div['style'] = 'float: right;'
    # get rid of the saving message
    list_save_divs = soup.findAll("span", {"class": "gs_nph"})
    for div in list_save_divs:
        div.decompose()
    return str(soup)

# print ('Does div class still exist', soup.findAll('div', {'class': 'gs_rs'}))
# with open('test123.html', 'w') as fp:
#     fp.write(str(soup))
