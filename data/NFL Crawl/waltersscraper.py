from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import re
import os
from io import StringIO
from html.parser import HTMLParser
import glob

'''Thanks to Oliver Le Floch from https://stackoverflow.com/questions/753052/strip-html-from-strings-in-python for this solution'''
class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = StringIO()
    def handle_data(self, d):
        self.text.write(d)
    def get_data(self):
        return self.text.getvalue()

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


def getSummaries():
    '''Saves all the texts from walters website to a designated file'''
    #walter has collected nfl reviews from the years 2008 to 2020
    for year in range(8, 20):
        #there are up to 20 play weeks in each year
        for week in range(1, 20):
            url = "https://walterfootball.com/nflreview20{:02d}_{:02d}.php".format(year, week)
            print("Trying to access {}...".format(url))
            try:
                req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
                page = urlopen(req).read()
                soup = BeautifulSoup(page, "html.parser")
                
                #get all game names. these may be inside of <li> tags but are definetly marked by <b> tags. 
                #because walter is a **** that doesnt understand common sense and programming he sometimes has the last (or even more?) 
                #line of his report in the same <li> tag as the matchup (team names + scores)
                #I have to get all the text between the first and last <b> [Team] [Score], [Team] [Score] </b>, no matter in which list item they are stored
                #saves the semi-useful texts of the website to a file, hopefully this works for every paeg...
                fulltext = ""
                f =  open("reviews20{:02d}w{:02d}.txt".format(year, week), "w")
                for el in soup.find_all('div', id="MainContentBlock"):
                    fulltext += str(el)

                f.write(fulltext)
                f.close()
                print("Success!")
            except Exception:
                import traceback
                print(traceback.format_exc())
                continue

def format(filename):
    '''Formats the text review by removing all html tags'''
    f = open(filename)
    n = open('formatted\\'+filename[len('unformatted\\'):], "w")
    print(f.readline())
    for line in f:
        #this is to keep the matchup as a separator
        l = strip_tags(line)
        #after this there may be some leftover shit-html because the code from walterfootball really sucks 
        l = re.sub(".+>", '', l)
        l = re.sub("^.*'\);", '', l)

        #removes in-text multiple new lines
        l = re.sub("^\n$\n", '', l)

        #Add some special symbols to signify a new report is beginning
        l = re.sub(r'\w* \d{1,2}, \w* \d{1,2}\s*\n', '### \\g<0>', l)

        #remove leading and trailing whitespaces
        if(not l.isspace()):
            n.write(l)
    print("Done removing html for file {}".format(filename))
    f.close()
    n.close()

def review2File(filename):
    '''Creates a new file for each game review'''
    f = open(filename, "r").read()
    
    for rev in f.split('###'):
        #print(rev[0:100])
        pattern = r"^.+ \d{1,2}, .+ \d{1,2} *"
        if(re.search(pattern, rev)):
        #if(rev and rev.startswith('###')):
            revFileName = ''
            for sym in rev:
                if(not sym == '\n'):
                    revFileName += sym
                else: 
                    break
            #print(revFileName)
            revFileName = revFileName.replace(', ', '-').rstrip()+'_'+filename[len('clutterless\\reviews'):]
            n = open('reviews\\'+revFileName, 'w')
            n.write(rev)
            n.close()
            print("Done splitting {}".format(filename))


def stripFile(filename):
    '''Strips all leading and tailing whitespaces from the reviews'''
    f = open(filename, 'r').readlines()
    n = open('stripped\\'+filename[len('formatted\\'):len('formatted\\reviews2008w01.txt')], 'w')
    for line in f:
        #this strips all the leading whitespaches from each line and also streamlines the review delimiter
        line = re.sub('^\\s*#{3}\\s*', '###', line)
        line = re.sub('^\\s*', '', line)
        line = line.replace('document.write('');', '')
        n.write(line)
    print('Stripped file {}'.format(filename))
    n.close()

def removeClutter(filename):
    '''My fucking god this website is literally the worst piece of software I ever had to see'''
    f = open(filename, 'r').read()
    bsRegex = r"For thoughts on (.|\n)*'\);"  
    bs2Regex = r"For thoughts on .*$"
    bs3Regex = r"\n(?!\w* \d{1,2}, \w* \d{1,2}\s*\n).*@.*\n\(Edit.+(?=\n)" #this hopefully removes the one to two lines if the report was written by someone else
    n = re.sub(bsRegex, "", f)
    n = re.sub(bs2Regex, "", n)
    n = re.sub(bs3Regex, "", n)
    newFile = open('clutterless\\'+filename[len('stripped\\'):], 'w')
    newFile.write(n)
    newFile.close()
    print("Done removing clutter from {}".format(filename))
#getSummaries()
#format("reviews2008w01.txt")


#for file in glob.glob('unformatted\\'+"*.txt"):
#    format(file)

#for file in glob.glob('formatted\\'+"*.txt"):
#    stripFile(file)

for file in glob.glob('stripped\\'+"*.txt"):
    removeClutter(file)

for file in glob.glob('clutterless\\'+"*.txt"):
    review2File(file)



