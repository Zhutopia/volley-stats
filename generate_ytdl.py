import sys
import requests
from bs4 import BeautifulSoup

def generate_file(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text)
    description = soup.find('meta', attrs={'name': 'description'})
    print(description.attrs['content'])
    return
    link = soup.find_all(name="title")[0]
    print(soup.prettify())
    title = str(link)
    title = title.replace("<title>","")
    title = title.replace("</title>","")
    title_split = title.split()
    description = str(soup.find_all(name="content"))
    print(title_split)
    url_name = title_split[0] + '_' + ''.join(title_split[2:-2])

    print(url_name)

    url_name = url
    file_name = url_name + '_downloader.sh'
    with open(file_name,'w') as f:
        f.write('yt-dlp '+ url)

if __name__ == "__main__":
    if len(sys.argv) == 2:
        generate_file(sys.argv[1])
    else:
        print(sys.argv)