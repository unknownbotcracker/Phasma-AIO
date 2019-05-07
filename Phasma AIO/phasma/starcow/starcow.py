import cfscrape, json, os, sqlite3, time, datetime, subprocess, random, threading
from pypresence import Presence
from bs4 import BeautifulSoup
from discord_webhook import DiscordEmbed, DiscordWebhook
from selenium import webdriver
import ssl, wget, socket, requests, sys
headers = {'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36', 
 'upgrade-insecure-requests':'1', 
 'referer':'https://www.starcowparis.com/', 
 'cache-control':'no-cache', 
 'accept-language':'it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7', 
 'accept-encoding':'utf-8', 
 'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3'}
proxyList = []
proxyIndex = 0

def loadProxy1(nomeFile):
    global proxyList
    f = open('' + nomeFile + '.txt')
    dividiStiProxy = f.readlines()
    tmp = dividiStiProxy.split('\n')
    for n in range(0, len(tmp)):
        if ':' in tmp[n]:
            temp = tmp[n]
            temp = temp.split(':')
            proxies = {'http':'http://' + temp[2] + ':' + temp[3] + '@' + temp[0] + ':' + temp[1] + '/', 
             'https':'http://' + temp[2] + ':' + temp[3] + '@' + temp[0] + ':' + temp[1] + '/'}
            proxyList.append(proxies)


def loadProxy2(nomeFile):
    f = open('' + nomeFile + '.txt')
    dividiStiProxy = f.read()
    tmp = dividiStiProxy.split('\n')
    for n in range(0, len(tmp)):
        if ':' in tmp[n]:
            temp = tmp[n]
            proxies = {'http':'http://' + temp,  'https':'http://' + temp}
            proxyList.append(proxies)


try:
    loadProxy1('proxies')
except:
    loadProxy2('proxies')

totalproxies = len(proxyList)
if int(totalproxies) == 0:
    print('Running localhost!')
else:
    print('Loaded %s proxies!' % totalproxies)
start = int(time.time())
os.chdir('..')
os.chdir('..')
data = json.loads(open('data/data.json').read())
try:
    RPC = Presence('536617509382782996')
    RPC.connect()
except:
    pass

def presence():
    version = data['main']['version']
    while True:
        try:
            RPC.update(state='Version ' + version, details='Running Phasma AIO...', large_image='phasma', start=start)
        except:
            pass


(threading.Thread(target=presence)).start()

def gettime():
    now = str(datetime.datetime.now())
    now = now.split(' ')[1]
    threadname = threading.currentThread().getName()
    threadname = str(threadname).replace('Thread', 'Task')
    now = '[' + str(now) + ']' + ' ' + '[' + str(threadname) + ']'
    return now


def main():
    s = cfscrape.create_scraper()

    def send_webhook(webhook_url, title, price, size, sku, url):
        try:
            webhook = DiscordWebhook(url=webhook_url, content='')
            embed = DiscordEmbed(title='Starcow Checkout', color=11403055, url=url)
            embed.add_embed_field(name='Product', value=title)
            embed.add_embed_field(name='Product Price', value=price)
            embed.add_embed_field(name='Product Size', value=size)
            embed.add_embed_field(name='Product PID', value='||' + str(sku) + '||')
            embed.add_embed_field(name='Payment Type', value='PAYPAL')
            embed.set_footer(text='Phasma AIO', icon_url='https://cdn.discordapp.com/attachments/542413665941585927/553897752485167124/PROFILE-TWITTER.png')
            embed.set_timestamp()
            webhook.add_embed(embed)
            webhook.execute()
            print(gettime() + ' [SUCCESS] -> Successfully sent success webhook!')
        except:
            print(gettime() + ' [ERROR] -> Failed sending success webhook! Please check data.json!')

    def send_error(webhook_url, title, price, size, sku, url):
        try:
            webhook = DiscordWebhook(url=webhook_url, content='')
            embed = DiscordEmbed(title='Starcow Failed Checkout', color=16711680, url=url)
            embed.add_embed_field(name='Product', value=title)
            embed.add_embed_field(name='Product Price', value=price)
            embed.add_embed_field(name='Product Size', value=size)
            embed.add_embed_field(name='Product PID', value='||' + str(sku) + '||')
            embed.add_embed_field(name='Payment Type', value='PAYPAL')
            embed.set_footer(text='Phasma AIO', icon_url='https://cdn.discordapp.com/attachments/542413665941585927/553897752485167124/PROFILE-TWITTER.png')
            embed.set_timestamp()
            webhook.add_embed(embed)
            webhook.execute()
        except:
            pass

    def activate():
        key = data['main']['key']
        print(gettime() + ' [STATUS] -> Activating key...')
        r = requests.get('http://209.97.184.199:8000/verify1?key=' + str(key))
        r = json.loads(r.text)
        if r['status'] == '0':
            print(gettime() + ' [ERROR] -> This key was already verified!')
            input('')
            sys.exit()
        if r['status'] == '1':
            print(gettime() + ' [SUCCESS] -> Valid key!')
        if r['status'] == '2':
            print(gettime() + ' [ERROR] -> This key is invalid...')
            input('')
            sys.exit()
        if r['status'] == '3':
            print(gettime() + " [ERROR] -> This key wasn't verified on Discord!")
            input('')
            sys.exit()

    def monitor(url, size, profile):
        print(gettime() + ' [STATUS] -> Accessing Starcow...')
        name = data['profile'][profile]['name']
        surname = data['profile'][profile]['surname']
        email = data['profile'][profile]['email']
        street1 = data['profile'][profile]['street-1']
        street2 = data['profile'][profile]['street-2']
        street3 = data['profile'][profile]['street-3']
        birthday = data['profile'][profile]['birthday']
        phone = data['profile'][profile]['phone']
        zipcode = data['profile'][profile]['zipcode']
        city = data['profile'][profile]['city']
        province = data['profile'][profile]['province']
        country = data['profile'][profile]['country']
        webhook_url = data['profile'][profile]['webhook']
        delay = data['main']['delay']
        if 'https' not in url:
            kw = True
        else:
            kw = False

        def atc(atc_url):
            try:
                atc_get = s.get(atc_url, headers=headers)
            except Exception as e:
                try:
                    print(gettime() + ' [ERROR] -> %s' % e)
                    time.sleep(int(delay))
                    atc(atc_url)
                finally:
                    e = None
                    del e

            if atc_get.status_code not in (200, 302):
                print(gettime() + ' [ERROR] -> Failed adding to cart, status code: %s...' % atc_get.status_code)
                time.sleep(int(delay))
                atc(atc_url)
            else:
                print(gettime() + ' [SUCCESS] -> ATC Successful!')

        def paypal():
            print(gettime() + ' [STATUS] -> Opening PayPal...')
            driver = webdriver.Chrome(executable_path='data/chromedriver.exe')
            driver.get('https://paypal.com')
            driver.delete_all_cookies()
            print(gettime() + ' [STATUS] -> Checking Out...')
            try:
                checkout = s.get('https://www.starcowparis.com/modules/paypal/express_checkout/payment.php?express_checkout=payment_cart&current_shop_url=https://www.starcowparis.com/commande?&bn=PRESTASHOP_ECM?cop=bestnotify', headers=headers, allow_redirects=True)
            except Exception as e:
                try:
                    print(gettime() + ' [ERROR] -> %s' % e)
                finally:
                    e = None
                    del e

            for c in s.cookies:
                z = {'name':c.name, 
                 'value':c.value,  'path':c.path}
                driver.add_cookie(z)

            if 'paypal' not in checkout.url:
                print(gettime() + ' [ERROR] -> Checkout Failed!')
                return
            else:
                print(gettime() + ' [SUCCESS] -> Successfully checked out.')
                driver.get(checkout.url)
                input('')
                return True

        def start(url, size):
            try:
                if bool(proxyList) == True:
                    s.proxies = random.choice(proxyList)
                if kw == True:
                    starcow = s.get('https://www.starcowparis.com/recherche?search_query=' + str(url) + '&orderby=position&orderway=desc', headers=headers)
                    soup = BeautifulSoup(starcow.text, 'html.parser')
                    try:
                        title = soup.find('h5', {'class': 'product-title'}).text.strip()
                        print(gettime() + ' [SUCCESS] -> Found product: %s' % title)
                        url = soup.find('a', {'title': title})['href']
                    except:
                        print(gettime() + ' [STATUS] -> Waiting for product...')
                        time.sleep(int(delay))
                        start(url, size)

                    try:
                        product = s.get(url, headers=headers)
                    except Exception as e:
                        try:
                            print(gettime() + ' [ERROR] -> %s' % e)
                            time.sleep(int(delay))
                            start(url, size)
                        finally:
                            e = None
                            del e

                    if product.status_code not in (200, 302):
                        print(gettime() + ' [ERROR] -> Error getting product! Status Code:', product.status_code)
                        time.sleep(int(delay))
                        start(url, size)
                if product is not None:
                    soup = BeautifulSoup(product.text, 'html.parser')
                    try:
                        title = soup.find('h1', {'class': 'name-product'}).text
                    except Exception as e:
                        try:
                            print(gettime() + ' [ERROR] -> %s' % e)
                            time.sleep(int(delay))
                            start(url, size)
                        finally:
                            e = None
                            del e

                    price = soup.find('span', {'itemprop': 'price'}).text
                    print(gettime() + ' [STATUS] -> Searching for SKU...')
                    id_product = url.split('/')[4].split('-')[0]
                    size_box = soup.find_all('script', {'type': 'text/javascript'})[0]
                    size_box = str(size_box)
                    size_box = size_box.split('combinations = ')[1].split(';')[0]
                    size_box = json.loads(size_box)
                    ids = []
                    attr = []
                    for id in size_box:
                        ids.append(id)

                    for e in ids:
                        e = str(e)
                        sizee = size_box[e]['attributes_values']
                        group = str(sizee).split(':')[0].split('{')[1].replace("'", '')
                        sizee = str(sizee).split(':')[1].split('}')[0].replace("'", '')
                        attribute = size_box[e]['attributes']
                        attribute = str(attribute)
                        attribute = attribute.split('[')[1].split(']')[0]
                        stock = size_box[e]['quantity']
                        if str(size) in str(sizee):
                            if int(stock) == 0:
                                print(gettime() + ' [ERROR] -> Waiting for restock...')
                                time.sleep(int(delay))
                                start(url, size)
                            else:
                                attr.append(attribute)
                                atc_url = 'https://www.starcowparis.com/panier?id_product=' + id_product + '&add=1&id_product_attribute=' + str(e) + '&group_' + str(group) + '=' + str(attribute) + '&Submit'
                                atc(atc_url)
                                pay = paypal()
                                if pay == None:
                                    sku = str(e)
                                    send_error(webhook_url, title, price, size, sku, url)
                                    input('')
                                else:
                                    sku = str(e)
                                    send_webhook(webhook_url, title, price, size, sku, url)
                                    input('')
                        else:
                            continue

                if bool(attr) == False:
                    print(gettime() + ' [ERROR] -> Waiting for restock...')
                    time.sleep(int(delay))
                    start(url, size)
            except Exception as e:
                try:
                    print(e)
                    monitor(url, size, profile)
                finally:
                    e = None
                    del e

        start(url, size)

    activate()
    for line in open('phasma/starcow/tasks.txt', 'r'):
        url = line.split(';')[0].strip()
        size = line.split(';')[1].strip()
        profile = line.split(';')[2].strip()
        (threading.Thread(target=monitor, args=(url, size, profile))).start()


main()