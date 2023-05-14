import requests,os,re,time,json5
from os import path,makedirs
from bs4 import BeautifulSoup as bs

def correctSingleQuoteJSON(s):
    rstr = ""
    escaped = False
    for c in s:
        if c == "'" and not escaped: c = '"'  # replace single with double quote
        elif c == "'" and escaped: rstr = rstr[:-1]  # remove escape character before single quotes
        elif c == '"':c = '\\' + c # escape existing double quotes
        escaped = (c == "\\") # check for an escape character
        rstr += c # append the correct jsonss
    return rstr

def scrape(sku):
    #create sub_folder if not exists
    subdir = path.join(path.join(os.getcwd(),'output'),sku)
    if not path.exists(subdir):
        makedirs(subdir)

    #get request from the url
    url = f'https://www2.hm.com/en_my/productpage.{sku}.html'
    headers = {'User-agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_3_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'}
    try:
        req = requests.get(url,headers=headers)
    except:
        time.sleep(2)
        req = requests.get(url,headers=headers)

    req_status = req.status_code
    count = 0
    while req_status != 200:
        print('reattempt to get request')
        if count <= 10:
            time.sleep(1)
            req=requests.get(url,headers=headers)
            req_status = req.status_code
            count += 1
        else: return f'Request Failed, status code: {req_status}'
    
    soup = bs(req.content, 'html.parser')

    #get productArticleDetails
    data  = soup.find_all("script")
    data = list(filter(lambda x:re.search('var productArticleDetails =',str(x)),data))
    data = ''.join(list(map(str,data))).replace('<script>','').replace('</script>','')
    content = re.search("productArticleDetails = ({\r\n.[\S\s]*.})",data)

    #if not found, write error message to a txt file 
    if content is None:
        err_msg = f'sku : {sku} not found.'
        err_file = path.join(subdir,f'err: {err_msg}.txt')
        with open(err_file, 'w') as handler: 
            handler.write(err_msg) 
        return f'Attempt to scrape for {sku} failed: {sku} not found.'
    
    content = content.group(1)
    content = correctSingleQuoteJSON(content).replace('\\"','"')
    content = content.replace("isDesktop ? ", "")
    content = re.sub(r' : "//.*"', '', content)
    content = json5.loads(content)

    img_list = content[f'{sku}']['images']
    # video_list = content[f'{sku}']['video']

    # if not video_list: print('empty')
    # if video_list: print(f'{sku} got video_list')

    for index,each_url in enumerate(img_list):
        img_url = 'https:{url}'.format(url=each_url['image'])
        img_path = path.join(subdir,f'{sku}_{index}.jpg')
        try:
            img_req = requests.get(img_url)
        except:
            time.sleep(2)
            img_req = requests.get(img_url)

        img_req_status = img_req.status_code
        cnt = 0
        while img_req_status != 200:
            print('reattempt to get request img')
            if cnt <= 10:
                time.sleep(1)
                img_req = requests.get(url,headers=headers)
                img_req_status = img_req.status_code
                cnt += 1
            else: return f'Request Failed, status code: {img_req_status}'

        img_data = img_req.content
        with open(img_path, 'wb') as handler: 
            handler.write(img_data) 

    return f'Attempt to scrape for {sku} succeeded'
