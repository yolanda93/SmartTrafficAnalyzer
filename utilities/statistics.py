# some functionalities to compute statistics
from pyspark.sql import SQLContext
from pyspark.sql import functions
from pyspark.ml.feature import Bucketizer
from pyspark.sql.functions import rank, min, dense_rank, percent_rank, ntile, col
from pyspark.sql.window import Window
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

### TSTAT - complete dataset using panda's data frames

def agg_class_flows(df_tstat):
	"""Compute total flows per pkt"""
	flows_class = pd.DataFrame({'count': df_tstat.groupby(['s_ip:15', '#c_ip:1', df_tstat[df_tstat.columns[-1]]]).size()}).reset_index()
	flows_class.columns = ['Server IP', 'Client IP', 'Tag', 'Total Flows']
	sum_flows_class = flows_class[['Tag', 'Total Flows']].groupby(['Tag'], as_index=False).sum()
	return sum_flows_class

def agg_class_pkts(df_tstat):
	"""Compute total server pkts, client pkts, port pkts per class"""
	flow_class = df_tstat.groupby(['tag:132']).sum()

	sum_cpkts_class = flow_class['c_pkts_all:3']
	sum_spkts_class = flow_class['s_pkts_all:17']

	#tag_2 = df.loc[df['tag:132']==2]	
	df_port = df_tstat.groupby(['tag:132','s_port:16']).sum()
	sum_ppkts_port = df_port['s_pkts_all:17']
	return sum_cpkts_class, sum_spkts_class, sum_ppkts_class


#### TSTAT - tmp complete dataset using pyspark data frames

def get_total_pkts_flowid(df):
	"""Compute total pkts per flow in tmp_complete"""

	# Group by Flow ID = IP Client, Server/Port Client, Server | Sum of pkts in server and client
	connect_pkts =  df.groupby(['#c_ip:1','c_port:2','s_ip:15','s_port:16']).agg({'c_pkts_all:3':'sum','s_pkts_all:17':'sum'})
	# Get total packets per flow
	connect_total_pkts = connect_pkts.withColumn('total_pkts',connect_pkts['sum(c_pkts_all:3)'].__add__(connect_pkts['sum(s_pkts_all:17)']))

	connect_total_pkts_flow = connect_total_pkts.withColumn("flow_id",functions.monotonically_increasing_id()) # assign a flow_id to each subflow belonging to the same flow

	return connect_total_pkts_flow.select("#c_ip:1","c_port:2","s_ip:15","s_port:16","total_pkts","flow_id")

def create_histogram(df, feature, buckets=None):
	"""
	Compute a bar chart histogram of a given feature
	buckets are either an array with widths of the bins of the histogram or the number of bins
	"""

	rdd_hist_data  = df.select(feature).rdd.flatMap(lambda x: x).histogram(buckets)

	heights = np.array(rdd_hist_data[1])
	full_bins = rdd_hist_data[0]
	mid_point_bins = full_bins[:-1]
	widths = [abs(i - j) for i, j in zip(full_bins[:-1], full_bins[1:])]
	bar = plt.bar(mid_point_bins, heights, width=widths, color='b')
	plt.show()

def compute_ranking(df, buckets=None, bins=None, feature):
	""" Rank the rows of df based on a given feature
	   		buckets is an array with the dfferent ranges used in ranking
	  		nbins will automatically compute the ranges used in ranking
	"""
	if bins:
        wSpec3 = Window.orderBy(feature)
        df_ranked = df_cnt_pkts.withColumn("rank", ntile(bins).over(wSpec3))

	if buckets:
		bucketizer = Bucketizer(splits=buckets,inputCol=feature, outputCol="rank")
		df_ranked = bucketizer.setHandleInvalid("keep").transform(df)

	return df_ranked


# Machine Learning

def plot_coefficients(classifier, feature_names, top_features=20):
 coef = classifier.coef_.ravel()
 top_positive_coefficients = np.argsort(coef)[-top_features:]
 top_negative_coefficients = np.argsort(coef)[:top_features]
 top_coefficients = np.hstack([top_negative_coefficients, top_positive_coefficients])
 # create plot
 plt.figure(figsize=(15, 5))
 colors = [‘red’ if c < 0 else ‘blue’ for c in coef[top_coefficients]]
 plt.bar(np.arange(2 * top_features), coef[top_coefficients], color=colors)
 feature_names = np.array(feature_names)
 plt.xticks(np.arange(1, 1 + 2 * top_features), feature_names[top_coefficients], rotation=60, ha=’right’)
 plt.show()


def plot_confusion_matrix(cm, classes,
                          normalize=False,
                          title='Confusion matrix',
                          cmap=plt.cm.Blues):
    """
    This function prints and plots the confusion matrix.
    Normalization can be applied by setting `normalize=True`.
    """
    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        print("Normalized confusion matrix")
    else:
        print('Confusion matrix, without normalization')

    print(cm)

    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=45)
    plt.yticks(tick_marks, classes)

    fmt = '.2f' if normalize else 'd'
    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, format(cm[i, j], fmt),
                 horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black")

    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')


#connect_pkts.describe().show()
#+-------+------------+------------------+-------------+------------------+------------------+------------------+------------------+------------------+
#|summary|     #c_ip:1|          c_port:2|      s_ip:15|         s_port:16|           tag:132|sum(s_pkts_all:17)| sum(c_pkts_all:3)|        total_pkts|
#+-------+------------+------------------+-------------+------------------+------------------+------------------+------------------+------------------+
#|  count|      124543|            124543|       124543|            124543|            124543|            124543|            124543|            124543|
#|   mean|        null| 44955.70561974579|         null|1014.4431882964117|1.1632448230731554| 274030.2181977309|119070.04885059778| 393100.2670483287|
#| stddev|        null|11400.023262159832|         null| 3137.842220858856|0.7685445575612441| 2838147.003392592|1084480.2510721278|3880853.7621902837|
#|    min|    1.3.0.10|              1025|     1.3.1.10|                25|                 0|                 0|                 1|                 1|
#|    max|172.16.1.197|             65535|98.139.28.144|             65403|                 3|         206006368|          80591343|         286597711|
#+-------+------------+------------------+-------------+------------------+------------------+------------------+------------------+------------------+

#connect_pkts.summary().show()
#+-------+------------+------------------+-------------+------------------+------------------+------------------+------------------+------------------+
#|summary|     #c_ip:1|          c_port:2|      s_ip:15|         s_port:16|           tag:132|sum(s_pkts_all:17)| sum(c_pkts_all:3)|        total_pkts|
#+-------+------------+------------------+-------------+------------------+------------------+------------------+------------------+------------------+
#|  count|      124543|            124543|       124543|            124543|            124543|            124543|            124543|            124543|
#|   mean|        null| 44955.70561974579|         null|1014.4431882964117|1.1632448230731554| 274030.2181977309|119070.04885059778| 393100.2670483287|
#| stddev|        null|11400.023262159832|         null| 3137.842220858856|0.7685445575612441| 2838147.003392592|1084480.2510721278|3880853.7621902837|
#|    min|    1.3.0.10|              1025|     1.3.1.10|                25|                 0|                 0|                 1|                 1|
#|    25%|        null|             38266|         null|               443|                 1|                25|                56|                91|
#|    50%|        null|             45882|         null|               443|                 1|                81|               168|               253|
#|    75%|        null|             53794|         null|               443|                 1|               489|               680|              1128|
#|    max|172.16.1.197|             65535|98.139.28.144|             65403|                 3|         206006368|          80591343|         286597711|
#+-------+------------+------------------+-------------+------------------+------------------+------------------+------------------+------------------+
