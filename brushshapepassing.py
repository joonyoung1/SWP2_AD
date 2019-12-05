from bs4 import BeautifulSoup
import requests


html = requests.get("http://pngimg.com/search/?page=%d&search=leaf" %(1))
soup = BeautifulSoup(html.text, 'html.parser')
html.close()


data1_list=soup.findAll('div')
src_list = []
for data1 in data1_list:
    k =(data1.findAll('img'))
    if k != []:
        img_src = k[-1]['src']
        if img_src[-3:-2] == 'p':
            src_list.append(img_src)

print(src_list)
