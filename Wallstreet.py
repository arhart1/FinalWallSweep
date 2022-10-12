import praw
import pandas as pd
import csv
import json
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import os

#Post limit selection
sn = int(input("Please select post limit: "))
search = False
sr = ''
rLimit = sn
 
#Open the stocks json file and save to a dict
f = open('nasdaq_stocks.json')
data = json.load(f)
f.close()

reddit_read_only = praw.Reddit(client_id="llvTBy2FzFIQQRh4ukwMHg",         # your client id
                               client_secret="JbiED47CLhMop3YQnngMtdD63ANGSw",      # your client secret
                               user_agent="Nearby_Ad_7159 ")        # your user agent
 
# Scraping the top posts of the current month
subreddit = reddit_read_only.subreddit("wallstreetbets")
posts = subreddit.hot(limit = rLimit)

calculations = rLimit * len(data)

#Layout of dictionaries
posts_dict = {"Title": [], "Post Text": [],
              "ID": [], "Score": [],
              "Total Comments": [], "Post URL": []
              }
 
locate_dict = {"Title": [], "Post URL":[], "Stock":[], "Score":[]}
stocksUsed = []
counter = 0

print('Searching... \n')

for post in posts:
    # Title of each post
    posts_dict["Title"].append(post.title)
     
    # Text inside a post
    posts_dict["Post Text"].append(post.selftext)
     
    # Unique ID of each post
    posts_dict["ID"].append(post.id)
     
    # The score of a post
    posts_dict["Score"].append(post.score)
     
    # Total number of comments inside the post
    posts_dict["Total Comments"].append(post.num_comments)
     
    # URL of each post
    posts_dict["Post URL"].append(post.url)

    #Check if a post contains stock name

    for stock in data:
        counter = counter + 1
        stk = stock['stock']
                
        if (((' ' + stk + ' ') in post.title) or (('$' + stk) in post.title)or ((stk + ' ') in post.title) or ((' ' + stk + ' ') in post.selftext)or (('$' + stk) in post.selftext) or ((stk + ' ') in post.selftext)):
            locate_dict["Title"].append(post.title)
            locate_dict["Post URL"].append(post.url)
            locate_dict["Stock"].append(stk)  
            locate_dict["Score"].append(0)

            if stk not in stocksUsed:
                stocksUsed.append(stk)

    if ((counter /10) % (calculations) == 0):
        print('*', end ='')

print("\n")
print(stocksUsed)
print("Calculations: " + str(counter))
# Saving the data in a pandas dataframe
top_posts = pd.DataFrame(posts_dict)

check_posts = pd.DataFrame(locate_dict)
check_posts = check_posts.drop_duplicates()

count = 0
scores = []

final_scores = dict.fromkeys(stocksUsed, 0)
final_counts = dict.fromkeys(stocksUsed, 0)

for row in check_posts.itertuples():
    sid = SentimentIntensityAnalyzer()
    sentiment_dict = sid.polarity_scores(row.Title)
    
    scores.append(sentiment_dict['compound'])

    #Update total score (not average) and update counts
    for key, value in final_scores.items():
        if key == row.Stock:
            final_scores[key] = final_scores[key] + sentiment_dict['compound']
            final_counts[key] = final_counts[key] + 1

    print(row.Title + "\n")

    print("Overall sentiment dictionary is : ", sentiment_dict)
    print("sentence was rated as ", sentiment_dict['neg']*100, "% Negative")
    print("sentence was rated as ", sentiment_dict['neu']*100, "% Neutral")
    print("sentence was rated as ", sentiment_dict['pos']*100, "% Positive")
 
    print("Sentence Overall Rated As", end = " ")
 
    # decide sentiment as positive, negative and neutral
    if sentiment_dict['compound'] >= 0.05 :
        print("Positive")
 
    elif sentiment_dict['compound'] <= - 0.05 :
        print("Negative")
 
    else :
        print("Neutral")
    print("\n")
    count = count + 1

print("Final Counts: \n")
print(final_counts)

#Update final scores and round them
for key, value in final_scores.items():
    final_scores[key] = round(final_scores[key] / final_counts[key],4)

#*********************Debugging Console Info*********************
print("Final Scores: \n")
print(final_scores)

print("\n" + str(count))

check_posts = check_posts.assign(points = scores)

print(check_posts)
top_posts.to_csv('myData.csv')

#*****************************************************************

sortedCounts = dict(sorted(final_counts.items(), key = lambda x:x[1]))
sortedFinal = dict(sorted(final_scores.items(), key = lambda x:x[1]))
print("Sorted: ")
print(sortedFinal)

#Menu UI and options
menu = True
while menu:
    print("\n##     ## ######## ##    ## ##     ## \n###   ### ##       ###   ## ##     ## \n#### #### ##       ####  ## ##     ## \n## ### ## ######   ## ## ## ##     ## \n##     ## ##       ##  #### ##     ## \n##     ## ##       ##   ### ##     ## \n##     ## ######## ##    ##  #######  \n")
    menSel = int(input("\n1. Most Positive\n2. Most Negative\n3. Most Discussed\n4. Search\n5. Exit\n Selection: "))
    os.system('cls')

    if menSel == 1:
        print("Most Positive Stock: ")
        print(list(sortedFinal.items())[-1])
        print('')
    elif menSel == 2:
        print("Most Negative Stock: ")
        print(list(sortedFinal.items())[0])
        print('')
    elif menSel == 3:
        print("Most Discussed Stock: ")
        print(list(sortedCounts.items())[-1])
        print('')
    elif menSel == 4:
        #Search for specific stock
        searchSel = input("Stock: ")

        if searchSel not in stocksUsed:
            print("No available data.")
        else:
            print("Score: ")
            searchKey = list(sortedFinal.keys()).index(searchSel)
            print(list(sortedFinal.items())[searchKey])

            print("Count: ")
            searchKey = list(sortedCounts.keys()).index(searchSel)
            print(list(sortedCounts.items())[searchKey])

    elif menSel == 5:
        menu = False
    else:
        print("Invalid selection.")