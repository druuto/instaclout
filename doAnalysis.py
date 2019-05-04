import json
import numpy as np
import sqlite3
from sqlite3 import Error
from datetime import datetime
import glob
import pandas as pd
import itertools
import csv
from datetime import datetime
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import AdaBoostClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from scipy import stats

def get_part_of_day(hour):
	return (
		#morning
		0 if 5 <= hour <= 11
		else
		#afternoon
		1 if 12 <= hour <= 17
		else
		#evening
		2 if 18 <= hour <= 22
		else
		#night
		3
	)


def MultipleLinearRegression(X, y, linear_model):

	lm = linear_model
	### DO NOT TOUCH THIS PORTION OF THE CODE###
	params = np.append(lm.intercept_,lm.coef_)
	predictions = lm.predict(X)

	newX = np.append(np.ones((len(X),1)), X, axis=1)
	MSE = (sum((y-predictions)**2))/(len(newX)-len(newX[0]))

	var_b = MSE*(np.linalg.inv(np.dot(newX.T,newX)).diagonal())
	sd_b = np.sqrt(var_b)
	ts_b = params/ sd_b

	p_values =[2*(1-stats.t.cdf(np.abs(i),(len(newX)-1))) for i in ts_b]

	myDF3 = pd.DataFrame()
	myDF3["Coefficients"],myDF3["Standard Errors"],myDF3["t values"],myDF3["Probabilites"] = [params,sd_b,ts_b,p_values]
	print(myDF3)


db = ['data3.db', 'combined_2018.db', 'posts2017.db']
for d in db:
	conn = sqlite3.connect(d)
	c = conn.cursor()
	print(d)
	c.execute('SELECT location_id, location_slug, num_pics, likes, comment_count, timestring, accessibility_caption, caption, id FROM posts;')

	result = c.fetchall()

	# slug to id
	location_ids = {}
	curr_id = 0

	IMAGE_STRING = "Image may contain:"

	# stores row in csv
	X = []
	y = []
	for x in result:
		id = str(x[-1])
		# Certain databases have the id starting with ./
		if(d!='data3.db'):
			id = '\"./' + id + '\"'
		# Query followers
		c.execute('SELECT followers FROM users WHERE id = ' +id+  ';')
		row = c.fetchone()
		if(row==None):
			continue
		f = row[0]
		oth = []
		#Append number of followeres
		oth.append(f)
		# Skip if post has less than 30 likes or less than one comment
		if(int(x[3])<30 or int(x[4])<1):
			continue
		#Skip if location is null
		if (x[1] == '' or x[1] == None):
			continue
		# num_pics
		oth.append(x[2])

		# # timestring (as timestamp)
		datetime_object = datetime.strptime(x[5], '%Y-%m-%d %H:%M:%S')
		oth.append(get_part_of_day(datetime_object.hour))
		#Append if at the beach
		if('beach' in x[1]):
			oth.append(1)
		else:
			oth.append(0)
		#Append if at disne
		if('disney' in x[1]):
			oth.append(1)
		else:
			oth.append(0)
		#Skip if no accessibility_caption
		if(x[6]==None or IMAGE_STRING not in x[6]):
			continue
		else:
			arra = []
			#Append if person in picture
			if("person" in x[6]):
				arra.append(1)
			elif("people" in x[6]):
				arra.append(1)
			else:
				arra.append(0)
			#Append if selfie
			if("selfie" in x[6]):
				arra.append(1)
			else:
				arra.append(0)
			for a in arra:
				row.append(a)
				oth.append(a)
		if(x[7]==None):
			oth.append(0)
		else:
			oth.append(len(x[7]))
		X.append(oth)
		y.append(x[3])
	conn.close()

X = np.array(X).astype(np.float64)
y = np.array(y).astype(np.float64)
print(len(X))
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = .125)
regr = RandomForestRegressor(n_estimators=500)
regr.fit(X_train,y_train)
print(regr.feature_importances_)
training_prediction = regr.predict(X_train)
testing_prediction = regr.predict(X_test)
print("Random Forest Training R-Squared: %.4f" % (regr.score(X_train, y_train)))
print("Random Forest Training MSE: %.2f" % mean_squared_error(y_train, training_prediction))
print("Random Forest Testing MSE: %.2f" % mean_squared_error(y_test, testing_prediction))
clf = AdaBoostClassifier(n_estimators=100)
clf.fit(X_train, y_train)
training_prediction = clf.predict(X_train)
testing_prediction = clf.predict(X_test)
print("Boosted Random Forest Training R-Squared: %.4f" % (clf.score(X_train, y_train)))
print("Boosted Random Forest Training MSE: %.2f" % mean_squared_error(y_train, training_prediction))
print("Boosted Random Forest Testing MSE: %.2f" % mean_squared_error(y_test, testing_prediction))
linear_model = LinearRegression().fit(X_train,y_train)
training_prediction = linear_model.predict(X_train)
testing_prediction = linear_model.predict(X_test)
MultipleLinearRegression(X_test, y_test, linear_model)
print("Regression Training R-Squared: %.4f" % (linear_model.score(X_train, y_train)))
print("Regression Training MSE: %.2f" % mean_squared_error(y_train, training_prediction))
print("Regression Testing MSE: %.2f" % mean_squared_error(y_test, testing_prediction))
