from amazon.api import AmazonAPI

config = {
# set this to your key value
}

def get_products(keyword):
    amazon = AmazonAPI(config['access_key'], config['secret_key'], config['associate_tag'])
    products = amazon.search(Keywords=keyword, SearchIndex='All')
    html_list = []
    for book in products:  # probably limits itself to 50 books
        html = '''<div class='product-box'>
                    <a target="_blank" href="{}">
                      <img src="{}" width="120" height="160">
                    </a>
                    <div class="product-title">
                      <h3>{}</h3>
                      <p class="product-price">{} {}<br></p>
                    </div>
                  </div>'''.format(book.detail_page_url,
                                   book.large_image_url,
                                   book.title, book.price_and_currency[1], book.price_and_currency[0])
        html_list.append(html)
    return ''.join(html_list[:10])
