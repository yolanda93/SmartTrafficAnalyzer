# some functionalities to process the datasets

from pyspark.sql import SQLContext
from pyspark.sql.functions import rank, min, dense_rank, percent_rank, ntile, col
from pyspark.sql.window import Window
import statistics
import csv

def subsampling(df, ranges=None, bins=None, sample_ratios=None, take_first=None):
	"""
	tcp_complete datasets
	range is an array of tuples
	"""
	connect_pkts = statistics.get_total_pkts_flowid(df)

	df_ranked = statistics.compute_ranking(connect_pkts, ranges, bins)

	subsampled = sqlContext.createDataFrame(sc.emptyRDD(), df_ranked.schema)
	
	if sample_ratios:

		for i, ratio in zip(range(len(ranges)),sample_ratios):
				subsampled = subsampled.union(df_ranked.filter(df_ranked['rank']==i).sample(False, round(ratio), seed=0))

	elif take_first:

		for i, ntake in zip(range(len(ranges)),take_first):
			if ntake == 'n':
				ratio = df_ranked.count()
			else:
				ratio = round(ntake / df_ranked.count())

		subsampled = subsampled.union(df_ranked.filter(df_ranked['rank']==i).sample(False, round(ratio), seed=0))

	return subsampled