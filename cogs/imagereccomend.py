import sqlite3
from collections import Counter 

#GETS THE N TOP RECCOMENDATIONS (BY K NEAREST NEIGHBORS AND COSINE SIMILARITY METRIC)
#IF NO FAVOURITES FOUND FOR USER, RETURNS FALSE
def getNRecommendations(user_id, source, n):
    db = sqlite3.connect("scrapedlinks.sqlite")
    cursor = db.cursor()

    #Fetch information from the user's favourited images and tags
    sql = ""
    if (source == "gelbooru"):
        sql = f"SELECT tags,link FROM sauceusers WHERE user_id={user_id}"
    else:
        sql = sql = f"SELECT tags,link FROM sauce34users WHERE user_id={user_id}"
    cursor.execute(sql)
    res = cursor.fetchall()
    if (len(res) == 0):
        return False

    #Keep track of the most commonly occurring tags in the user's favourite images
    tagStr = ""
    #keep record of the user's favourited images
    userLinkList = []

    #Iterate through all the user's favourite images and their respective tags
    for tags, link in res: 
        tagStr += tags
        tagStr += " "
        userLinkList.append(link)
    tagList = tagStr.split()
    #Fetch the three most commonly occurring tags (used for preliminary filtering)
    word1 = Counter(tagList).most_common(3)[0][0]
    word2 = Counter(tagList).most_common(3)[1][0]
    word3 = Counter(tagList).most_common(3)[2][0]

    #Create a user profile vector with the number of occurences of each tag in all of the user's favourite images
    userTagCount = dict(Counter(tagList))

    #Fetch all of the images containing any of the user's 3 most commonly occurring tags
    if (source == "gelbooru"):
        sql = f"SELECT * from sauce WHERE tags LIKE '%{word1}%' OR tags LIKE '%{word2}%' OR tags LIKE '%{word3}%'"
    else:
        sql = f"SELECT * from sauce34 WHERE tags LIKE '%{word1}%' OR tags LIKE '%{word2}%' OR tags LIKE '%{word3}%'"
    cursor.execute(sql)
    res = cursor.fetchall()

    #Holds evaluation metrics
    linkScores = []
    linkMap = []

    for elem in res:
        link = elem[0]
        #Check if image is already in user's favourites
        if link in userLinkList:
            continue
        tags = elem[1]
        #We generate a tag count vector for all the tags of each image
        linkTagCount = dict(Counter(tags.split()))

        #Each image will have a tag vector looking that looks like {"tag1": 1, "tag2": 1, "tag3": 1, ....}
        #The user profile vector will also look like {"tag1": (some number), "tag2": (some number) ...}

        #This algorithm will treat each tag as an axis in cartesian space, and we will treat both dictionaries as vectors.
        #We will use the cosine value of the angle between the vectors as a similarity metric
        dot_product = sum(userTagCount[tag] * linkTagCount.get(tag, 0) for tag in userTagCount)
        
        userTagMag = pow(sum(userTagCount[tag] * userTagCount[tag] for tag in userTagCount), 0.5)
        linkTagMag = pow(sum(linkTagCount[tag] * linkTagCount[tag] for tag in linkTagCount), 0.5)

        #manually compute cosine sim
        cosine_sim = dot_product/(userTagMag * linkTagMag)
        #Maps links to a cosine similarity score for reverse lookup
        linkMap.append([link, cosine_sim])
        #We will only append the cosine sim scores so we have a single dimension list that can be quickly sorted
        linkScores.append(cosine_sim)
        linkScores.sort(reverse=True)
    
    links = []
    if(n >= len(linkScores)):
        n = len(linkScores) - 1
        
    for score in linkScores[0:n]:
        for pair in linkMap:
            if (pair[1] == score):
                links.append(pair[0])
    cursor.close()
    db.commit()
    db.close()
    return list(dict.fromkeys(links))[0:n]

