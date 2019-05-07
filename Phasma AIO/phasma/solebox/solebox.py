import cfscrape, json, os, sqlite3, time, datetime, subprocess, random, threading
from pypresence import Presence
from bs4 import BeautifulSoup
from discord_webhook import DiscordEmbed, DiscordWebhook
from selenium import webdriver
import ssl, wget, socket, requests, sys
headers = {'authority':'www.solebox.com', 
 'scheme':'https', 
 'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3', 
 'accept-encoding':'gzip, deflate, br', 
 'accept-language':'it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7', 
 'cache-control':'max-age=0', 
 'upgrade-insecure-requests':'1', 
 'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'}
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
    s = requests.session()

    def send_webhook(webhook_url, title, price, inputsize, aid, image, url, paymentype):
        try:
            webhook = DiscordWebhook(url=webhook_url, content='')
            embed = DiscordEmbed(title='Solebox Checkout', color=11403055, url=url)
            embed.add_embed_field(name='Product', value=title)
            embed.add_embed_field(name='Product Price', value=price)
            embed.add_embed_field(name='Product Size', value=inputsize)
            embed.add_embed_field(name='Payment Type', value=paymentype)
            embed.set_image(url=str(image))
            embed.set_footer(text='Phasma AIO', icon_url='https://cdn.discordapp.com/attachments/542413665941585927/553897752485167124/PROFILE-TWITTER.png')
            embed.set_timestamp()
            webhook.add_embed(embed)
            webhook.execute()
            print(gettime() + ' [SUCCESS] -> Successfully sent success webhook!')
        except:
            print(gettime() + ' [ERROR] -> Failed sending success webhook! Please check data.json!')

    def send_error(webhook_url, title, price, inputsize, aid, image, url, paymentype):
        try:
            webhook = DiscordWebhook(url=webhook_url, content='')
            embed = DiscordEmbed(title='Solebox Failed Checkout', color=16711680, url=url)
            embed.add_embed_field(name='Product', value=title)
            embed.add_embed_field(name='Product Price', value=price)
            embed.add_embed_field(name='Product Size', value=inputsize)
            embed.add_embed_field(name='Payment Type', value=paymentype)
            embed.set_image(url=str(image))
            embed.set_footer(text='Phasma AIO',
              icon_url='https://cdn.discordapp.com/attachments/542413665941585927/553897752485167124/PROFILE-TWITTER.png')
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

    def monitor(url, inputsize, profile, payment):
        if 'https' not in url:
            kw = True
        else:
            kw = False
        if bool(proxyList) == True:
            s.proxies = random.choice(proxyList)
            print(gettime() + ' [STATUS] -> Checking proxy...')
            test = s.get('https://www.solebox.com/mein-konto/', headers=headers)
            if test.status_code not in (302, 200):
                print(gettime() + ' [ERROR] -> Proxy banned, status code %s' % test.status_code)
                time.sleep(3)
                monitor(url, inputsize, profile, payment)
            else:
                print(gettime() + ' [SUCCESS] -> Proxy working perfectly! Status code %s' % test.status_code)
        webhook_url = data['profile'][profile]['webhook']
        delay = data['main']['delay']

        def login():
            if bool(proxyList) == True:
                s.proxies = random.choice(proxyList)
            print(gettime() + ' [STATUS] -> Logging in...')
            lgn_email = data['profile'][profile]['solebox-email']
            lgn_psw = data['profile'][profile]['solebox-password']
            login_page = s.get('https://www.solebox.com/mein-konto/', headers=headers)
            soup = BeautifulSoup(login_page.text, 'html.parser')
            try:
                stoken = soup.find('input', {'name': 'stoken'})['value']
                print(gettime() + ' [STATUS] -> Login token: %s' % stoken)
            except:
                print(gettime() + ' [ERROR] -> Login token is None!')
                time.sleep(int(delay))
                login()

            login_post = s.post('https://www.solebox.com/index.php?',
              headers=headers, data={'stoken':stoken, 
             'lang':'0', 
             'listtype':'', 
             'actcontrol':'account', 
             'cl':'account', 
             'fnc':'login_noredirect', 
             'lgn_usr':lgn_email, 
             'lgn_pwd':lgn_psw})
            if login_post.status_code not in (302, 200):
                print(gettime() + ' [ERROR] -> Failed logging in! Status code %s' % login_post.status_code)
                time.sleep(int(delay))
                login()
            else:
                check = s.get('https://www.solebox.com/en/my-account/', headers=headers)
                soup = BeautifulSoup(check.text, 'html.parser')
                try:
                    check_lgn = soup.find('div', {'class': 'Content'}).text
                except:
                    print(gettime() + ' [ERROR] -> Failed logging in! Login credentials are wrong!')
                    time.sleep(int(delay))
                    login()

                print(gettime() + ' [SUCCESS] -> Logged in successfully with status code %s! Good job!' % login_post.status_code)

        print(gettime() + ' [STATUS] -> Accessing Solebox...')

        def kw_mode(url):
            search = s.get('https://www.solebox.com/index.php?lang=0&cl=alist&searchparam=' + str(url), headers=headers)
            soup = BeautifulSoup(search.text, 'html.parser')
            try:
                url = soup.find('a', {'class': 'fn'})
                title = url['title']
                url = url['href']
                return [
                 title, url]
            except:
                return 'notfound'

        def start():
            if bool(proxyList) == True:
                s.proxies = random.choice(proxyList)
            if kw == True:
                keyword = kw_mode(url)
                if keyword != 'notfound':
                    urlk = keyword[1]
                    titlek = keyword[0]
                    print(gettime() + ' [SUCCESS] -> Found product bro! %s' % titlek)
                    product = s.get(urlk, headers=headers)
                else:
                    print(gettime() + ' [STATUS] -> Waiting for product...')
                    start()
            else:
                product = s.get(url, headers=headers)
            if product.status_code not in (302, 200):
                print(gettime() + ' [ERROR] -> Failed scraping product! Status code %s' % product.status_code)
                time.sleep(int(delay))
                start()
            else:
                soup = BeautifulSoup(product.text, 'html.parser')
                try:
                    title = soup.find('h1', {'id': 'productTitle'}).text
                except:
                    print(gettime() + ' [ERROR] -> Oh no! Proxy seems working but it sees a blank page!')
                    time.sleep(int(delay))
                    start()

                try:
                    release = soup.find('div', {'class': 'release'}).text
                    print(gettime() + ' [STATUS] -> Waiting for release, good luck!')
                    time.sleep(int(delay))
                    start()
                except:
                    try:
                        aid_list = []
                        title = soup.find('h1', {'id': 'productTitle'}).text
                        price = soup.find('div', {'id': 'productPrice'}).text.strip()
                        image = soup.find('a', {'id': 'zoom1'})['href']
                        try:
                            size_box = soup.find('div', {'class': 'sizeBlock'})
                            sizes = size_box.find_all('div')
                            for id in sizes:
                                soup = BeautifulSoup(str(id), 'html.parser')
                                try:
                                    if 'inactive' not in str(id):
                                        aidd = soup.find('a', {'data-size-original': str(inputsize)})['id']
                                        aid_list.append(aidd)
                                    else:
                                        continue
                                except:
                                    pass

                        except:
                            print(gettime() + ' [ERROR] -> Failed scraping product!')
                            time.sleep(int(delay))
                            start()

                        soup = BeautifulSoup(product.text, 'html.parser')
                        lang = soup.find('input', {'name': 'lang'})['value']
                        aid = random.choice(aid_list)
                    except Exception as e:
                        try:
                            print(gettime() + ' [STATUS] -> Product is out of stock! Waiting for restock...')
                            time.sleep(int(delay))
                            start()
                        finally:
                            e = None
                            del e

                def atc():
                    print(gettime() + ' [STATUS] -> Adding to cart %s...' % aid)
                    print(gettime() + ' [STATUS] -> POSTING for ATC...')
                    atc_post = s.post('https://www.solebox.com/index.php', headers=headers, data={'aproducts[0][am]':'1', 
                     'lang':lang, 
                     'fnc':'changebasket', 
                     'isAjax':'1', 
                     'cl':'basket', 
                     'aproducts[0][aid]':aid})
                    if atc_post.status_code not in (302, 200):
                        print(gettime() + ' [ERROR] -> Oh no! ATC failed! Status code %s' % atc_post.status_code)
                        time.sleep(int(delay))
                        atc()
                    else:
                        print(gettime() + ' [SUCCESS] -> Successfully added to cart!')

                def paypal():
                    paymentype = 'PAYPAL'
                    print(gettime() + ' [STATUS] -> Checking out with PayPal...')
                    checkout = s.get('https://www.solebox.com/index.php?cl=payment',
                      headers=headers)
                    soup = BeautifulSoup(checkout.text, 'html.parser')
                    try:
                        stoken = soup.find('input', {'name': 'stoken'})['value']
                        print(gettime() + ' [SUCCESS] -> Successfully got PayPal token! %s' % stoken)
                    except:
                        print(gettime() + ' [ERROR] -> Payment token is None! Retrying...')
                        time.sleep(int(delay))
                        paypal()

                    checkout_post = s.post('https://www.solebox.com/index.php?lang=' + str(lang) + '&',
                      headers=headers, allow_redirects=True, data={'stoken':stoken, 
                     'lang':'1', 
                     'actcontrol':'payment', 
                     'cl':'payment', 
                     'fnc':'validatepayment', 
                     'paymentid':'globalpaypal', 
                     'userform':''})
                    if 'paypal' in checkout_post.url:
                        print(gettime() + ' [SUCCESS] -> Successfully checked out!')
                        send_webhook(webhook_url, title, price, inputsize, aid, image, url, paymentype)
                        print(gettime() + ' [STATUS] -> Opening Chrome...')
                        driver = webdriver.Chrome('data/chromedriver.exe')
                        driver.get('https://paypal.com')
                        driver.delete_all_cookies()
                        for c in s.cookies:
                            z = {'name':c.name,  'value':c.value,  'path':c.path}
                            driver.add_cookie(z)

                        driver.get(checkout_post.url)
                        input('')
                    else:
                        print(gettime() + ' [ERROR] -> Failed checking out!')
                        send_error(webhook_url, title, price, inputsize, aid, image, url, paymentype)
                        start()

                def cashinadvance():
                    paymentype = 'CASHINADVANCE'
                    print(gettime() + ' [STATUS] -> Going to payment...')
                    checkout = s.get('https://www.solebox.com/index.php?cl=payment', headers=headers)
                    soup = BeautifulSoup(checkout.text, 'html.parser')
                    try:
                        stoken = soup.find('input', {'name': 'stoken'})['value']
                        lang = soup.find('input', {'name': 'lang'})['value']
                    except:
                        print(gettime() + ' [ERROR] -> Unable to find checkout token!')
                        time.sleep(int(delay))
                        cashinadvance()

                    try:
                        cash = soup.find('label', {'for': 'payment_oxidpayadvance'}).text
                        payload = {'stoken':stoken, 
                         'lang':lang, 
                         'actcontrol':'payment', 
                         'cl':'payment', 
                         'fnc':'validatepayment', 
                         'paymentid':'oxidpayadvance', 
                         'userform':''}
                        method = s.post('https://www.solebox.com/index.php?lang=' + str(lang) + '&', headers=headers, data=payload, allow_redirects=True)
                        if method.status_code not in (302, 200):
                            print(gettime() + ' [ERROR] -> Error while submitting method! Status code: %s' % method.status_code)
                            time.sleep(int(delay))
                            cashinadvance()
                        else:
                            print(gettime() + ' [SUCCESS] -> Successfully selected payment method.')
                            print(gettime() + ' [STATUS] -> Getting order page...')
                            order = s.get('https://www.solebox.com/index.php?cl=order&lang=' + str(lang), headers=headers)
                            if order.status_code not in (302, 200):
                                print(gettime() + ' [ERROR] -> Failed getting order page... Status code: %s' % order.status_code)
                                time.sleep(int(delay))
                                cashinadvance()
                            else:
                                print(gettime() + ' [SUCCESS] -> Successfully got order page. Status code: %s' % order.status_code)
                                print(gettime() + ' [STATUS] -> Submitting order...')
                                soup = BeautifulSoup(order.text, 'html.parser')
                                try:
                                    stoken = soup.find('input', {'name': 'stoken'})['value']
                                    lang = soup.find('input', {'name': 'lang'})['value']
                                    sDeliveryAddressMD5 = soup.find('input', {'name': 'sDeliveryAddressMD5'})['value']
                                except:
                                    print(gettime() + ' [ERROR] -> Unable to get checkout token!')
                                    time.sleep(int(delay))
                                    cashinadvance()

                                order_payload = {'stoken':stoken, 
                                 'lang':lang, 
                                 'actcontrol':'order', 
                                 'cl':'order', 
                                 'fnc':'execute', 
                                 'challenge':'', 
                                 'sDeliveryAddressMD5':sDeliveryAddressMD5, 
                                 'ord_agb':'1', 
                                 'oxdownloadableproductsagreement':'0', 
                                 'oxserviceproductsagreement':'0', 
                                 'ord_agb':'1'}
                                pay = s.post('https://www.solebox.com/index.php?lang=' + str(lang) + '&', headers=headers, allow_redirects=True, data=order_payload)
                                print(gettime() + ' [SUCCESS] -> Successfully checked out.')
                                send_webhook(webhook_url, title, price, inputsize, aid, image, url, paymentype)
                                input('')
                    except:
                        print(gettime() + ' [ERROR] -> Unable to checkout with CAD!')
                        send_error(webhook_url, title, price, inputsize, aid, image, url, paymentype)
                        paypal()

                atc()
                if str(payment) == '1':
                    paypal()
                else:
                    cashinadvance()

        while True:
            login()
            start()
            time.sleep(600)

    activate()
    for line in open('phasma/solebox/tasks.txt'):
        url = line.split(';')[0].strip()
        inputsize = line.split(';')[1].strip()
        profile = line.split(';')[2].strip()
        payment = line.split(';')[3].strip()
        (threading.Thread(target=monitor, args=(url, inputsize, profile, payment))).start()


main()