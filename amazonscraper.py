from amazon.api import AmazonAPI
import os
# config = {
# 'access_key': 'AKIAJCPOBYH5S64QRKMQ',
# 'secret_key': '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',
# 'associate_tag': 'suhaspatil-20',
# 'locale': 'us'
# }

config = {
'access_key': os.environ.get('AMAZON_ACCESS'),
'secret_key': os.environ.get('AMAZON_SECRET'),
'associate_tag': os.environ.get('AMAZON_ASSOCIATE'),
'locale': os.environ.get('AMAZON_LOCALE')
}

def get_products(keyword):
    amazon = AmazonAPI(config['access_key'], config['secret_key'], config['associate_tag'])
    products = amazon.search(Keywords=keyword, SearchIndex='All')
    html_list = []
    for book in products:  # probably limits itself to 50 books
        html = '''<div class='product-box'><a target="_blank" href="{}"><img src="{}" width="120" height="160"></a><div class="product-title"><h3>{}</h3><p class="product-price">{} {}<br></p></div></div>'''.format(book.detail_page_url,
                                                                  book.large_image_url,
                                                                  book.title, book.price_and_currency[1], book.price_and_currency[0])
        html_list.append(html)
    return ''.join(html_list[:10])
