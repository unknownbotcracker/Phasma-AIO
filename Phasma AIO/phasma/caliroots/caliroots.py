import cfscrape, json, os, sqlite3, time, datetime, subprocess, random, threading
from pypresence import Presence
from bs4 import BeautifulSoup
from discord_webhook import DiscordEmbed, DiscordWebhook
from selenium import webdriver
import ssl, wget, socket, requests, sys
headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36', 
 'upgrade-insecure-requests':'1', 
 'cache-control':'no-cache', 
 'accept-language':'it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7', 
 'accept-encoding':'utf-8', 
 'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3', 
 'scheme':'https', 
 'authority':'caliroots.com', 
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
    s = cfscrape.create_scraper()

    def send_webhook(webhook_url, url, sku, title, inputsize):
        try:
            webhook = DiscordWebhook(url=webhook_url, content='')
            embed = DiscordEmbed(title='Caliroots Checkout', color=11403055, url=url)
            embed.add_embed_field(name='Product', value=title)
            embed.add_embed_field(name='Size', value=inputsize)
            embed.add_embed_field(name='PID', value=str(sku))
            embed.set_footer(text='Phasma AIO', icon_url='https://cdn.discordapp.com/attachments/542413665941585927/553897752485167124/PROFILE-TWITTER.png')
            embed.set_timestamp()
            webhook.add_embed(embed)
            webhook.execute()
            print(gettime() + ' [SUCCESS] -> Successfully sent success webhook!')
        except:
            print(gettime() + ' [ERROR] -> Failed sending success webhook! Please check data.json!')

    def send_error(webhook_url, url, sku, title, inputsize):
        try:
            webhook = DiscordWebhook(url=webhook_url, content='')
            embed = DiscordEmbed(title='Caliroots Failed Checkout', color=16711680, url=url)
            embed.add_embed_field(name='Product', value=title)
            embed.add_embed_field(name='Size', value=inputsize)
            embed.add_embed_field(name='PID', value=str(sku))
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

    def monitor(url, inputsize, profile):
        if bool(proxyList) == True:
            s.proxies = random.choice(proxyList)
        webhook_url = data['profile'][profile]['webhook']
        delay = data['main']['delay']
        print(gettime() + ' [STATUS] -> Accessing Caliroots...')

        def start():
            product = s.get(url, headers=headers)
            if product.status_code not in (302, 200):
                print(gettime() + ' [ERROR] -> Unable to access Caliroots! Status code %s' % product.status_code)
                time.sleep(int(delay))
                start()
            soup = BeautifulSoup(product.text, 'html.parser')
            try:
                title = soup.find('h1').text
            except:
                print(gettime() + ' [ERROR] -> Unable to scrape product!')
                time.sleep(int(delay))
                start()

            pids = soup.find('select', {'name': 'id'})
            pids = pids.find_all('option')
            pids_list = []
            for id in pids[1:]:
                try:
                    pid = str(id).split('value=')[1].split('>')[0].replace('"', '').strip()
                    sizee = str(id).split('US')[1].split('<')[0].strip()
                    if str(inputsize) == sizee:
                        print(gettime() + ' [STATUS] -> Adding to cart ' + title + ' [' + pid + ']' + '...')
                        pids_list.append(pid)
                    else:
                        continue
                except:
                    print(gettime() + ' [ERROR] -> Waiting for restock...')
                    time.sleep(int(delay))
                    start()

            try:
                sku = random.choice(pids_list)
            except:
                print(gettime() + ' [ERROR] -> Waiting for restock...')
                time.sleep(int(delay))
                start()

            def atc():
                atc_get = s.get('https://caliroots.com/cart/add?id=' + sku + '&partial=ajax-cart', headers=headers)
                if atc_get.status_code not in (302, 200):
                    print(gettime() + ' [ERROR] -> Failed adding to cart! Status code %s' % atc_get.status_code)
                    time.sleep(int(delay))
                    atc()
                else:
                    print(gettime() + ' [SUCCESS] -> ATC Successful! Status code %s' % atc_get.status_code)

            def paypal():
                print(gettime() + ' [STATUS] -> Checking out...')
                pay = s.get('https://caliroots.com/express/checkout/49', allow_redirects=True, headers=headers)
                if 'paypal' in pay.url:
                    print(gettime() + ' [SUCCESS] -> Successfully checked out!')
                    send_webhook(webhook_url, url, sku, title, inputsize)
                    print(gettime() + ' [STATUS] -> Opening Chrome...')
                    driver = webdriver.Chrome('data/chromedriver.exe')
                    driver.get('https://paypal.com')
                    driver.delete_all_cookies()
                    for c in s.cookies:
                        z = {'name':c.name,  'value':c.value,  'path':c.path}
                        driver.add_cookie(z)

                    driver.get(pay.url)
                    input('')
                else:
                    print(gettime() + ' [ERROR] -> Failed checkout!')
                    send_error(webhook_url, url, sku, title, inputsize)

            atc()
            paypal()

        start()

    activate()
    for line in open('phasma/caliroots/tasks.txt'):
        url = line.split(';')[0].strip()
        inputsize = line.split(';')[1].strip()
        profile = line.split(';')[2].strip()
        (threading.Thread(target=monitor, args=(url, inputsize, profile))).start()


main()