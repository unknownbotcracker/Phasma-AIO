import cfscrape, json, os, sqlite3, time, datetime, subprocess, random, threading
from pypresence import Presence
from bs4 import BeautifulSoup
from discord_webhook import DiscordEmbed, DiscordWebhook
from selenium import webdriver
import ssl, wget, socket, requests, cloudscraper, sys
headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36', 
 'origin':'https://www.holypopstore.com', 
 'cache-control':'no-cache', 
 'connection':'keep-alive'}
headers1 = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36', 
 'origin':'https://www.holypopstore.com', 
 'cache-control':'no-cache', 
 'x-requested-with':'XMLHttpRequest', 
 'connection':'keep-alive'}
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
            RPC.update(state='Version ' + version, details='Running Phasma AIO...',
              large_image='phasma',
              start=start)
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

    def send_webhook(webhook_url, url, title, img, size, pid):
        try:
            webhook = DiscordWebhook(url=webhook_url, content='')
            embed = DiscordEmbed(title='Holypop Checkout', color=11403055, url=url)
            embed.add_embed_field(name='Product', value=title)
            embed.add_embed_field(name='Product PID', value=pid)
            embed.add_embed_field(name='Product Size', value=size)
            embed.set_image(url=str(img))
            embed.set_footer(text='Phasma AIO', icon_url='https://cdn.discordapp.com/attachments/542413665941585927/553897752485167124/PROFILE-TWITTER.png')
            embed.set_timestamp()
            webhook.add_embed(embed)
            webhook.execute()
        except:
            pass

    def send_error(webhook_url, url, title, img, size, pid):
        try:
            webhook = DiscordWebhook(url=webhook_url, content='')
            embed = DiscordEmbed(title='Holypop Failed Checkout', color=16711680, url=url)
            embed.add_embed_field(name='Product', value=title)
            embed.add_embed_field(name='Product PID', value=pid)
            embed.add_embed_field(name='Product Size', value=size)
            embed.set_image(url=str(img))
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
        webhook_url = data['profile'][profile]['webhook']
        delay = data['main']['delay']
        print(gettime() + ' [STATUS] -> Accessing Holypop...')

        def login():
            holypop_email = data['profile'][profile]['holypop-email']
            holypop_password = data['profile'][profile]['holypop-password']
            if bool(proxyList) == True:
                s.proxies = random.choice(proxyList)
            print(gettime() + ' [STATUS] -> Logging in...')
            login_post = s.post('https://www.holypopstore.com/index.php', headers=headers1, data={'controller':'auth', 
             'action':'authenticate', 
             'type':'standard', 
             'extension':'holypop', 
             'credential':holypop_email, 
             'password':holypop_password, 
             'version':'139'})
            r = json.loads(login_post.text)
            if 'True' or 'true' in r:
                check = s.get('https://www.holypopstore.com/it/account', headers=headers)
                soup = BeautifulSoup(check.text, 'html.parser')
                try:
                    soup.find('div', {'class': 'account-form row'}).text
                    print(gettime() + ' [SUCCESS] -> Successfully logged in.')
                except:
                    print(gettime() + ' [ERROR] -> Failed logging in! Please check your credentials!')
                    time.sleep(int(delay))
                    login()

            else:
                print(gettime() + ' [ERROR] -> Login failed. Status Code %s' % login_post.status_code)
                time.sleep(int(delay))
                login()

        login()

        def scrape():
            if bool(proxyList) == True:
                s.proxies = random.choice(proxyList)
            product = s.get(url, headers=headers)
            soup = BeautifulSoup(product.text, 'html.parser')
            try:
                title = soup.find('h1').text
                try:
                    soup.find('div', {'class': 'counter-container'}).text
                    print(gettime() + ' [STATUS] -> Waiting for release...')
                    time.sleep(int(delay))
                    scrape()
                except:
                    pass

                img = soup.find('img', {'class': 'item-image'})['src']
            except:
                print(gettime() + ' [ERROR] -> Failed scraping product!')
                time.sleep(int(delay))
                scrape()

            print(gettime() + ' [STATUS] -> Searching for PID...')
            js = soup.find_all('script', {'type': 'text/javascript'})[2]
            js = json.loads(str(js).split('var preloadedStock = ')[1].replace(';', '').split('var preloadedRelatedItems = ')[0])
            pids = []
            print('Sizes in Stock')
            for id in js:
                pid = str(id).split(':')[1].split(',')[0].replace("'", '').strip()
                sizee = str(id).split('variant')[1].split(',')[0].split(':')[1].replace("'", '').split('US')[0].strip()
                print(pid + ' | ' + sizee)
                if size == 'random':
                    pids.append(pid)
                else:
                    if str(size) == str(sizee):
                        pids.append(pid)
                    else:
                        continue

            try:
                atcpid = random.choice(pids)
            except:
                print(gettime() + ' [ERROR] -> Waiting for restock...')
                time.sleep(int(delay))
                scrape()

            def atc():
                print(gettime() + ' [STATUS] -> Adding to cart %s...' % atcpid)
                atc_post = s.post('https://www.holypopstore.com/index.php', headers=headers1, data={'controller':'orders', 
                 'action':'addStockItemToBasket', 
                 'stockItemId':atcpid, 
                 'quantity':'1', 
                 'extension':'holypop', 
                 'version':'139'})
                r = json.loads(atc_post.text)
                if atc_post.status_code not in (302, 200):
                    print(gettime() + ' [ERROR] -> ATC Failed! Status code %s' % atc_post.status_code)
                    time.sleep(int(delay))
                    atc()
                if 'true' or 'True' in r['success']:
                    print(gettime() + ' [SUCCESS] -> ATC Successful!')
                    print(gettime() + ' [STATUS] -> Getting checkout...')
                else:
                    print(gettime() + ' [ERROR] -> ATC Failed!')
                    time.sleep(int(delay))
                    atc()

            def address():
                checkout_get = s.get('https://www.holypopstore.com/it/orders/review', headers=headers)
                if checkout_get.status_code not in (302, 200):
                    print(gettime() + ' [ERROR] -> Failed getting checkout! Status code %s' % checkout_get.status_code)
                    time.sleep(int(delay))
                    address()
                soup = BeautifulSoup(checkout_get.text, 'html.parser')
                try:
                    js = str(checkout_get.text).split('var preloadedAddresses = ')[1].split('</script>')[0].replace(';', '')
                    js = json.loads(js)[0]
                    addressid = js['id']
                    jsship = str(checkout_get.text).split('var preloadedShippers = ')[1].split('</script>')[0].replace(';', '')
                    js1 = json.loads(jsship)[0]
                    shipid = js1['id']
                    shipid2 = str(js1).split('[')[1].split(':')[1].split(',')[0].replace('"', '').replace("'", '').strip()
                except:
                    print(gettime() + ' [ERROR] -> Failed scraping checkout!')
                    time.sleep(int(delay))
                    address()

                print(gettime() + ' [STATUS] -> Updating payment...')
                print(gettime() + ' Address ID: ' + str(addressid) + ' | Shipper ID: ' + str(shipid) + ' | Shipper Account ID: ' + str(shipid2))
                update = s.post('https://www.holypopstore.com/index.php', headers=headers1, data={'secretly':'false', 
                 'hardErrorize':'false', 
                 'billingAddressId':addressid, 
                 'shippingAddressId':addressid, 
                 'newAddresses':'0', 
                 'requestInvoice':'0', 
                 'notes':'', 
                 'paymentMethodId':'1', 
                 'paymentMethodAccountId':'1', 
                 'shipments[0][addressId]':addressid, 
                 'shipments[0][shipperId]':shipid, 
                 'shipments[0][shipperAccountId]':shipid2, 
                 'toDisplay':'1', 
                 'extension':'holypop', 
                 'controller':'orders', 
                 'action':'review', 
                 'clearSession':'0', 
                 'version':'139'})
                r = json.loads(update.text)
                if 'true' or 'True' in r['success']:
                    print(gettime() + ' [SUCCESS] -> Successfully updated payment!')
                    print(gettime() + ' [STATUS] -> Submitting address...')
                else:
                    print(gettime() + ' [ERROR] -> Failed updating payment!')
                    time.sleep(int(delay))
                    address()
                pay = s.post('https://www.holypopstore.com/index.php', headers=headers1, allow_redirects=True, data={'secretly':'false', 
                 'hardErrorize':'true', 
                 'billingAddressId':addressid, 
                 'shippingAddressId':addressid, 
                 'newAddresses':'0', 
                 'requestInvoice':'0', 
                 'notes':'', 
                 'paymentMethodId':'1', 
                 'paymentMethodAccountId':'1', 
                 'shipments[0][addressId]':addressid, 
                 'shipments[0][shipperId]':shipid, 
                 'shipments[0][shipperAccountId]':shipid2, 
                 'toDisplay':'0', 
                 'extension':'holypop', 
                 'controller':'orders', 
                 'action':'save', 
                 'version':'139'})
                r = json.loads(pay.text)
                if 'true' or 'True' in r['success']:
                    print(gettime() + ' [SUCCESS] -> Successfully submitted address!')
                else:
                    print(gettime() + ' [ERROR] -> Failed submitting address!')
                    time.sleep(int(delay))
                    address()
                print(gettime() + ' [STATUS] -> Checking out...')
                r = json.loads(pay.text)['payload']['orderId']
                pay = s.get('https://www.holypopstore.com/it/orders/checkout/' + str(r) + '?paymentMethodId=1&paymentMethodAccountId=1', headers=headers, allow_redirects=True)
                if 'paypal' not in pay.url:
                    pid = atcpid
                    send_error(webhook_url, url, title, img, size, pid)
                    print(gettime() + ' [ERROR] -> Checkout failed!')
                    time.sleep(int(delay))
                    address()
                else:
                    pid = atcpid
                    send_webhook(webhook_url, url, title, img, size, pid)
                    print(gettime() + ' [SUCCESS] -> Successfully checked out!')
                    driver = webdriver.Chrome('data/chromedriver.exe')
                    driver.get('https://paypal.com')
                    driver.delete_all_cookies()
                    for c in s.cookies:
                        z = {'name':c.name,  'value':c.value,  'path':c.path}
                        driver.add_cookie(z)

                    driver.get(pay.url)
                    input('')

            atc()
            address()

        scrape()

    activate()
    for line in open('phasma/holypop/tasks.txt'):
        url = line.split(';')[0].strip()
        size = line.split(';')[1].strip()
        profile = line.split(';')[2].strip()
        (threading.Thread(target=monitor, args=(url, size, profile))).start()


main()