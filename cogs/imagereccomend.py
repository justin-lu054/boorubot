import sqlite3
from collections import Counter 
from collections import defaultdict
from operator import itemgetter

#GETS THE N TOP RECCOMENDATIONS (BY K NEAREST NEIGHBORS AND COSINE SIMILARITY)
#IF NO FAVOURITES FOUND FOR USER, RETURNS FALSE
def getNRecommendations(user_id, source, n):
    db = sqlite3.connect("scrapedlinks.sqlite")
    cursor = db.cursor()

    #FILTER BY TOP 3 TAGS USING LIKE AND OR OPERATORS!!!!
    sql = ""
    if (source == "gelbooru"):
        sql = f"SELECT tags,link FROM sauceusers WHERE user_id={user_id}"
    else:
        sql = sql = f"SELECT tags,link FROM sauce34users WHERE user_id={user_id}"
    cursor.execute(sql)
    res = cursor.fetchall()
    if (len(res) == 0):
        return False
    tagStr = ""
    #keep record of the user's links
    userLinkList = []
    for tags, link in res: 
        tagStr += tags
        tagStr += " "
        userLinkList.append(link)
    tagList = tagStr.split()
    word1 = Counter(tagList).most_common(3)[0][0]
    word2 = Counter(tagList).most_common(3)[1][0]
    word3 = Counter(tagList).most_common(3)[2][0]
    userTagCount = defaultdict(lambda: 0, dict(Counter(tagList)))

    if (source == "gelbooru"):
        sql = f"SELECT * from sauce WHERE tags LIKE '%{word1}%' OR tags LIKE '%{word2}%' OR tags LIKE '%{word3}%'"
    else:
        sql = f"SELECT * from sauce34 WHERE tags LIKE '%{word1}%' OR tags LIKE '%{word2}%' OR tags LIKE '%{word3}%'"
    cursor.execute(sql)
    res = cursor.fetchall()

    linkScores = []
    linkMap = []
    for elem in res:
        link = elem[0]
        #CHECK IF LINK IS ALREADY IN FAVOURITES
        if link in userLinkList:
            continue
        tags = elem[1]
        linkTagCount = defaultdict(lambda: 0, dict(Counter(tags.split())))
        dot_product = 0
        userTagMag = 0
        linkTagMag = 0
        for key, val in userTagCount.items():
            dot_product += val * linkTagCount[key]
            userTagMag += val * val
        for key, val in linkTagCount.items():
            linkTagMag += val * val 
        userTagMag = pow(userTagMag, 1/2)
        linkTagMag = pow(linkTagMag, 1/2)
        cosine_sim = dot_product/(userTagMag * linkTagMag)
        linkMap.append([link, cosine_sim])
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
    return list(dict.fromkeys(links))

