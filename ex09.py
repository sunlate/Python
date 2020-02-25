# -*- coding: utf-8 -*-
#EX624 EX09
#Author: LeiSun

import urllib3
from bs4 import BeautifulSoup
from operator import itemgetter
from wordcloud import WordCloud, STOPWORDS
import string
import matplotlib.pyplot as plt

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
###   Read url    ####
http=urllib3.PoolManager()
url='https://www.rottentomatoes.com/m/fantastic_beasts_the_crimes_of_grindelwald/reviews/?page='
response=http.request('GET',url)
# print (response.status)
# print (response.data)

#Load the page into your “soup”
soup=BeautifulSoup(response.data,'lxml')

###   Identify the total number of pages ####
pageNo = soup.find("span",attrs={"class":"pageInfo"}).get_text()
pageNo = int(pageNo.split(" ")[-1])
# print (pageNo)


###   Collect review and respective score  ####

#initializing the list of words
mylist = []
reviewlist=[]
scorelist=[]  
#Create a dictionary of standardize scores
mydict={"A+": 1, "A": 0.96, "A-": 0.92, "B+": 0.89, "B": 0.86, "B-": 0.82,"C+": 0.79, "C": 0.76, "C-": 0.72, "D+": 0.69, "D": 0.66, "D-": 0.62}

###   Loop through each page, creating a new soup every time   ####
for i in range(1,pageNo+1):
    resp=http.request('GET',url+str(i))
    # print (resp.data[:100])
    newSoup=BeautifulSoup(resp.data,'lxml')
    #Create a list of review text 
    for row in newSoup.find_all('div',attrs={"class":"the_review"}):
        review=row.text
        reviewlist.append(review)
# print (reviewlist) 
    #Create a list of scores  
    for line in soup.find_all('div',attrs={"class":"small subtle"}):
        score=line.text.replace(" Full Review | Original Score: ", "")#Remove useless text
        score=score.replace(" Full Review ","")#Remove useless text
        if score in mydict.keys():
                scorelist.append(mydict[score])
        #Standardize scores. Replace nominal scores with numerical values: A+ = 1, A = 0.96, A- = 0.92, B+ = 0.89, B = 0.86, B- = 0.82, C+ = 0.79, C = 0.76, C- = 0.72, D+ = 0.69, D = 0.66, D- = 0.62
        elif score !='':
            if "/" in score:
                x,y=score.strip().split("/")
                score=float(x)/float(y)
                scorelist.append(score)
            #set invalid score to 0
            else:#if only one number,it is invalid, eg:2.5
                scorelist.append(0)
        else:
            scorelist.append(0)#set 0 to no rating reviews
# print (scorelist)


###   Generate a list of lists[review,score]  ####   

#Create a list of lists [review, score], where “review” is the review text content and “score” is the rate given for each review. This score can be a nominal grade, fraction or can be missing                             
for i in range (0,len(reviewlist)-1):
    if scorelist[i]==0:#remove the reviews with no rating
        continue
    else:
        mylist.append([reviewlist[i],scorelist[i]])

###Sort list of lists by ranking scores####
sortedList=sorted(mylist,key=itemgetter(1),reverse=True)
print ('Sort list ')
print (sortedList)

###   Print Top 20 and Bottom 20 reviews lists   ####

#Clean stop words using the stopword_en.txt file
#populating the list of stopwords
stopwords_file = open('stopwords_en.txt','r') 
stopwords=[]
for word in stopwords_file:
    stopwords.append(word.strip())

#Create words frequency list    
def word_freq(line):
    words=[]
    for text_file in line:
        parts = text_file.strip().split()
        for word in parts:
            if word.lower() not in stopwords and len(word) > 2:
                words.append(word.lower())
    return words    

#Create lists for top score reviews and bottom score reviews

topReviews=[]
for textTop in sortedList[:20]:
    topReviews.append(textTop[0])#Use only the text part of the reviews list of lists
print ('Top 20 reviews lists: ')
print (topReviews)

botReviews=[]
for textBot in sortedList[-20:]:
    botReviews.append(textTop[0])
print ('Bottom 20 reviews lists: ')
print (botReviews)

#function for calculate words frequency         
def word_freq(file):
    wordList=[]
    for text in file:
        parts=text.strip().split()
        for word in parts:
            if word.lower() not in stopwords and len(word) >2:
                table=str.maketrans({key:None for key in string.punctuation})#remove punctuation
                s=word.translate(table)
                wordList.append(s.lower())
    return wordList    

topWords=word_freq(topReviews)
botWords=word_freq(botReviews)

###   Create a word cloud for each of reviews lists   #####
def show_wordcloud(data,name):
    words_strimg = ' '.join(data)
    # Creating and updating the stopword list
    stpwords = set(STOPWORDS)
    stpwords.add('will')
    stpwords.add('said')
    stpwords.add('for')
    
    #Eliminate words providing no insight
    stpwords.add('film')
    stpwords.add('movie')
    stpwords.add('feel')
    stpwords.add('feels')
    stpwords.add('full')
    stpwords.add('review')
    #Eliminate words for producer and flim name information
    stpwords.add('grindelwald')
    stpwords.add('potter')
    stpwords.add('rowling')
    stpwords.add('beasts')
    stpwords.add('fantastic')
    #Defining the wordcloud parameters
    wc = WordCloud(background_color="white", max_words=2000,
                stopwords=stpwords)
    # Generate word cloud
    wc.generate(words_strimg)
    # Show the cloud
    plt.imshow(wc)
    plt.axis('off')
    plt.title("Word cloud of "+name)
    # plt.savefig(name+".png",bbox_inches='tight')
    plt.show()   
    
show_wordcloud(topWords,'Top Review')  
# show_wordcloud(botWords,'Bottom Review')  
 
response.close()
