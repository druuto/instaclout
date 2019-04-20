import numpy as np
import pandas as pd
import random
import csv
from sklearn import linear_model
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from scipy import stats

def split_data(data, prob):
    """Split data into fractions [prob, 1 - prob]"""
    results = [], []
    for row in data:
        results[0 if random.random() < prob else 1].append(row)
    return results

def train_test_split(x, y, test_pct):
	"""Split the features X and the labels y into x_train, x_test and y_train, y_test
	designated by test_pct. A common convention in data science is to do a 80% training
	data 20% test data split"""
	data = zip(x, y)								# pair corresponding values
	train, test = split_data(data, 1 - test_pct)    # split the data set of pairs
	x_train, y_train = zip(*train)					# magical un-zip trick
	x_test, y_test = zip(*test)
	return x_train, x_test, y_train, y_test

location_index, location_id, location_name, num_pics, likes, comment count, timestring, hashtag_count
features = ['location_index', 'location_id', 'location_name', 'location_type', 'num_pics', 'timestring', 'hashtag_count']

label = 'cnt'


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


if __name__=='__main__':

	# DO not change this seed. It guarantees that all students perform the same train and test split
	random.seed(1)
	# Setting p to 0.2 allows for a 80% training and 20% test split
	p = 0.2
	X = []
	y = []
	#############################################
	# TODO: open csv and read data into X and y #
	#############################################
	def load_file(file_path):
	    X = []
	    y = []
	    with open(file_path, 'r', encoding='latin1') as file_reader:
	        reader = csv.reader(file_reader, delimiter=',', quotechar='"')
	        next(reader)
	        # location_index, location_id, location_name, num_pics, likes, comment count, timestring, hashtag_count
	        for row in reader:
	        	if row == []:
	        		continue
	        	else:
	        		explanatory_var = []
	        		explanatory_var.append(float(row[features.index('num_pics')]))
	        		explanatory_var.append(float(row[features.index('location_type')]))
	        		explanatory_var.append(float(row[features.index('continent')]))
	        		explanatory_var.append(float(row[features.index('hashtag_count')]))
	        		X.append(explanatory_var)
	        		bike_share_cnt = int(row[len(row)-1])
	        		y.append(bike_share_cnt)
	    return np.array(X, dtype='float64'), np.array(y, dtype='float64')

	X, y = load_file("locations.csv")
			

	##################################################################################
	# TODO: use train test split to split data into x_train, x_test, y_train, y_test #
	#################################################################################
	res = train_test_split(X,y,p)
	x_train = res[0]
	x_test = res[1]
	y_train = res[2]
	y_test = res[3]

	##################################################################################
	# TODO: Use Sci-Kit Learn to create the Linear Model and Output R-squared
	#################################################################################
 
	# Prints out the Report
	my_model = LinearRegression().fit(x_train, y_train)
	res = MultipleLinearRegression(x_train, y_train, my_model)


	# TODO: print linear_model score
	print("r squared value is {}".format(my_model.score(x_test, y_test)))
	print("training MSE value is {}".format(mean_squared_error(y_train, my_model.predict(x_train))))
	print("testing MSE value is {}".format(mean_squared_error(y_test, my_model.predict(x_test))))



