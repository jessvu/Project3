## SI 206 2017
## Project 3
## Building on HW7, HW8 (and some previous material!)

##THIS STARTER CODE DOES NOT RUN!!


##OBJECTIVE:
## In this assignment you will be creating database and loading data 
## into database.  You will also be performing SQL queries on the data.
## You will be creating a database file: 206_APIsAndDBs.sqlite

import unittest
import itertools
import collections
import tweepy
import twitter_info # same deal as always...
import json
import sqlite3

## Your name: Jessica Vu
## The names of anyone you worked with on this project:

#####

##### TWEEPY SETUP CODE:
# Authentication information should be in a twitter_info file...
consumer_key = twitter_info.consumer_key
consumer_secret = twitter_info.consumer_secret
access_token = twitter_info.access_token
access_token_secret = twitter_info.access_token_secret
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

# Set up library to grab stuff from twitter with your authentication, and 
# return it in a JSON format 
api = tweepy.API(auth, parser=tweepy.parsers.JSONParser())

##### END TWEEPY SETUP CODE

## Task 1 - Gathering data

## Define a function called get_user_tweets that gets at least 20 Tweets 
## from a specific Twitter user's timeline, and uses caching. The function 
## should return a Python object representing the data that was retrieved 
## from Twitter. (This may sound familiar...) We have provided a 
## CACHE_FNAME variable for you for the cache file name, but you must 
## write the rest of the code in this file.

CACHE_FNAME = "206_APIsAndDBs_cache.json" #name of cache 
# Put the rest of your caching setup here:
try: #caching file name
    cache_file = open(CACHE_FNAME,'r')
    cache_contents = cache_file.read()
    cache_file.close()
    CACHE_DICTION = json.loads(cache_contents) #load json objects into dictonary
   	
except:
    CACHE_DICTION = {} #creates cache diectionary

# Define your function get_user_tweets here:
def get_user_tweets(user):
	if user in CACHE_DICTION: #pull data from cache if it's in there
		print("Data in the Cache")
		data = CACHE_DICTION[user]
		return data
	else: #else pull new data from twitter
		print("Fetching")
		results = api.user_timeline(screen_name=user) #get tweets from particular user
		CACHE_DICTION[user] = results
		data = CACHE_DICTION[user]
		cache_file = open(CACHE_FNAME, 'w')
		cache_file.write(json.dumps(CACHE_DICTION))
		cache_file.close()
	return CACHE_DICTION[user]

# Write an invocation to the function for the "umich" user timeline and 
# save the result in a variable called umich_tweets:

umich_tweets = get_user_tweets('@umich') #invokes get_user_tweets, gets 20 tweets from @umich


## Task 2 - Creating database and loading data into database
## You should load into the Users table:
# The umich user, and all of the data about users that are mentioned 
# in the umich timeline. 
# NOTE: For example, if the user with the "TedXUM" screen name is 
# mentioned in the umich timeline, that Twitter user's info should be 
# in the Users table, etc.
conn = sqlite3.connect("206_APIsAndDBs.sqlite") #database will be stored in 206_APIsAndDBs.sqlite
cur = conn.cursor() #creates cursor object, used to retrieve data row by row

cur.execute('DROP TABLE IF EXISTS Tweets')
cur.execute('CREATE TABLE Tweets (tweet_id TEXT PRIMARY KEY UNIQUE, text TEXT, user_posted TEXT, time_posted DATETIME, retweets INTEGER)')
#create Tweets table with following columns and their datatypes

cur.execute('DROP TABLE IF EXISTS Users')
cur.execute('CREATE TABLE Users (user_id TEXT PRIMARY KEY UNIQUE, screen_name TEXT, num_favs INTEGER, description TEXT)')
#create User table with following columns and their datatypes

for i in umich_tweets:
	tp1 = i["id"], i["text"], i["id_str"], i["created_at"], i["retweet_count"]
	cur.execute('INSERT INTO Tweets (tweet_id, text, user_posted, time_posted, retweets) VALUES(?,?,?,?,?)', tp1)
	#insert @umich user info into Tweets database

	cur.execute('SELECT * FROM Users WHERE user_id = (?)', (i["user"]["id_str"],)) 
	x = cur.fetchall() # gets all string ids to check for duplicates
	tp2 = i["user"]["id_str"], i["user"]["screen_name"], i["user"]["favourites_count"], i["user"]["description"]
	if len(x) == 0: #if user not in User table, insert user into Users table
		try:
			cur.execute('INSERT INTO Users (user_id, screen_name, num_favs, description) VALUES(?,?,?,?)', tp2)
		except:
			continue #if user already in table, continue to ensure all users unique
	if len(i['entities']['user_mentions']) > 0: #if mentioned users in cache insert them into Users table
		tp3 = i["id_str"], i["user"]["screen_name"], i["user"]["favourites_count"], i["user"]["description"]
		try:
			cur.execute('INSERT INTO Users (user_id, screen_name, num_favs, description) VALUES (?,?,?,?)',tp3)
		except: 
			continue

conn.commit() #save (commit) the changes
## You should load into the Tweets table: 
# Info about all the tweets (at least 20) that you gather from the 
# umich timeline.
# NOTE: Be careful that you have the correct user ID reference in 
# the user_id column! See below hints.


## HINT: There's a Tweepy method to get user info, so when you have a 
## user id or screenname you can find alllll the info you want about 
## the user.

## HINT: The users mentioned in each tweet are included in the tweet 
## dictionary -- you don't need to do any manipulation of the Tweet 
## text to find out which they are! Do some nested data investigation 
## on a dictionary that represents 1 tweet to see it!


## Task 3 - Making queries, saving data, fetching data

# All of the following sub-tasks require writing SQL statements 
# and executing them using Python.

# Make a query to select all of the records in the Users database. 
# Save the list of tuples in a variable called users_info.


users_info = cur.execute('SELECT * FROM Users')
users_info = users_info.fetchall() #returns list of all records


# Make a query to select all of the user screen names from the database. 
# Save a resulting list of strings (NOT tuples, the strings inside them!) 
# in the variable screen_names. HINT: a list comprehension will make 
# this easier to complete! 
screen_names = cur.execute('SELECT screen_name FROM Users')
screen_names = screen_names.fetchall() #returns list of all user screen names
screen_names = [''.join(name) for name in screen_names] #joins tuples in list for a list of just strings
#for name in screen_names:
	#screen_names = ''.join(name)



# Make a query to select all of the tweets (full rows of tweet information)
# that have been retweeted more than 10 times. Save the result 
# (a list of tuples, or an empty list) in a variable called retweets.
retweets = cur.execute('SELECT * FROM Tweets WHERE retweets > 10')
retweets = retweets.fetchall() #returns list of all tweets


# Make a query to select all the descriptions (descriptions only) of 
# the users who have favorited more than 500 tweets. Access all those 
# strings, and save them in a variable called favorites, 
# which should ultimately be a list of strings.
favorites = cur.execute('SELECT description FROM Users WHERE num_favs > 500')
favorites = favorites.fetchall() #returns list of all descriptions who have favorited more than 500 tweets
favorites = [''.join(tweet) for tweet in favorites] #joins tuples in list for a list of just strings


# Make a query using an INNER JOIN to get a list of tuples with 2 
# elements in each tuple: the user screenname and the text of the 
# tweet. Save the resulting list of tuples in a variable called joined_data2.
joined_data = cur.execute('SELECT Users.screen_name, Tweets.text FROM Users INNER JOIN Tweets ON Users.user_id = Tweets.user_posted')
joined_data = joined_data.fetchall() #returns list of tuples with user screenname and text of tweet from Tweets and Users table

# Make a query using an INNER JOIN to get a list of tuples with 2 
# elements in each tuple: the user screenname and the text of the 
# tweet in descending order based on retweets. Save the resulting 
# list of tuples in a variable called joined_data2.

joined_data2 = cur.execute('SELECT Users.screen_name, Tweets.text FROM Users INNER JOIN Tweets ON Users.user_id = Tweets.user_posted ORDER BY Tweets.retweets DESC')
joined_data2 = joined_data2.fetchall() #returns list of tuples with user screenname and text of tweet from Tweets and Users table in descending order


### IMPORTANT: MAKE SURE TO CLOSE YOUR DATABASE CONNECTION AT THE END 
### OF THE FILE HERE SO YOU DO NOT LOCK YOUR DATABASE (it's fixable, 
### but it's a pain). ###

###### TESTS APPEAR BELOW THIS LINE ######
###### Note that the tests are necessary to pass, but not sufficient -- 
###### must make sure you've followed the instructions accurately! 
######
print("\n\nBELOW THIS LINE IS OUTPUT FROM TESTS:\n")


class Task1(unittest.TestCase):
	def test_umich_caching(self):
		fstr = open("206_APIsAndDBs_cache.json","r")
		data = fstr.read()
		fstr.close()
		self.assertTrue("umich" in data)
	def test_get_user_tweets(self):
		res = get_user_tweets("umsi")
		self.assertEqual(type(res),type(["hi",3]))
	def test_umich_tweets(self):
		self.assertEqual(type(umich_tweets),type([]))
	def test_umich_tweets2(self):
		self.assertEqual(type(umich_tweets[18]),type({"hi":3}))
	def test_umich_tweets_function(self):
		self.assertTrue(len(umich_tweets)>=20)

class Task2(unittest.TestCase):
	def test_tweets_1(self):
		conn = sqlite3.connect('206_APIsAndDBs.sqlite')
		cur = conn.cursor()
		cur.execute('SELECT * FROM Tweets');
		result = cur.fetchall()
		self.assertTrue(len(result)>=20, "Testing there are at least 20 records in the Tweets database")
		conn.close()
	def test_tweets_2(self):
		conn = sqlite3.connect('206_APIsAndDBs.sqlite')
		cur = conn.cursor()
		cur.execute('SELECT * FROM Tweets');
		result = cur.fetchall()
		self.assertTrue(len(result[1])==5,"Testing that there are 5 columns in the Tweets table")
		conn.close()
	def test_tweets_3(self):
		conn = sqlite3.connect('206_APIsAndDBs.sqlite')
		cur = conn.cursor()
		cur.execute('SELECT tweet_id FROM Tweets');
		result = cur.fetchall()
		self.assertTrue(result[0][0] != result[19][0], "Testing part of what's expected such that tweets are not being added over and over (tweet id is a primary key properly)...")
		if len(result) > 20:
			self.assertTrue(result[0][0] != result[20][0])
		conn.close()


	def test_users_1(self):
		conn = sqlite3.connect('206_APIsAndDBs.sqlite')
		cur = conn.cursor()
		cur.execute('SELECT * FROM Users');
		result = cur.fetchall()
		self.assertTrue(len(result)>=2,"Testing that there are at least 2 distinct users in the Users table")
		conn.close()
	def test_users_2(self):
		conn = sqlite3.connect('206_APIsAndDBs.sqlite')
		cur = conn.cursor()
		cur.execute('SELECT * FROM Users');
		result = cur.fetchall()
		self.assertTrue(len(result)<20,"Testing that there are fewer than 20 users in the users table -- effectively, that you haven't added duplicate users. If you got hundreds of tweets and are failing this, let's talk. Otherwise, careful that you are ensuring that your user id is a primary key!")
		conn.close()
	def test_users_3(self):
		conn = sqlite3.connect('206_APIsAndDBs.sqlite')
		cur = conn.cursor()
		cur.execute('SELECT * FROM Users');
		result = cur.fetchall()
		self.assertTrue(len(result[0])==4,"Testing that there are 4 columns in the Users database")
		conn.close()

class Task3(unittest.TestCase):
	def test_users_info(self):
		self.assertEqual(type(users_info),type([]),"testing that users_info contains a list")
	def test_users_info2(self):
		self.assertEqual(type(users_info[0]),type(("hi","bye")),"Testing that an element in the users_info list is a tuple")

	def test_track_names(self):
		self.assertEqual(type(screen_names),type([]),"Testing that screen_names is a list")
	def test_track_names2(self):
		self.assertEqual(type(screen_names[0]),type(""),"Testing that an element in screen_names list is a string")

	def test_more_rts(self):
		if len(retweets) >= 1:
			self.assertTrue(len(retweets[0])==5,"Testing that a tuple in retweets has 5 fields of info (one for each of the columns in the Tweet table)")
	def test_more_rts2(self):
		self.assertEqual(type(retweets),type([]),"Testing that retweets is a list")
	def test_more_rts3(self):
		if len(retweets) >= 1:
			self.assertTrue(retweets[1][-1]>10, "Testing that one of the retweet # values in the tweets is greater than 10")

	def test_descriptions_fxn(self):
		self.assertEqual(type(favorites),type([]),"Testing that favorites is a list")
	def test_descriptions_fxn2(self):
		self.assertEqual(type(favorites[0]),type(""),"Testing that at least one of the elements in the favorites list is a string, not a tuple or anything else")
	def test_joined_result(self):
		self.assertEqual(type(joined_data[0]),type(("hi","bye")),"Testing that an element in joined_result is a tuple")



if __name__ == "__main__":
	unittest.main(verbosity=2)