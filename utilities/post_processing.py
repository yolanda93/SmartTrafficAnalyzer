# some functionalities to process the datasets

from pyspark.sql import SQLContext
from pyspark.sql import functions
from pyspark.sql.functions import rank, min, dense_rank, percent_rank, ntile, col, row_number
from pyspark.sql.window import Window
from utilities import statistics
import csv

def subsampling(spark_ctx, sql_context, df, ranges=None, bins=None, sample_ratios=None, take_first=None):
	"""
	tcp_complete datasets
	range is an array of tuples
	take_first is an array of tuples of the n first flows to be taken in each interval
	sample_ratio applies a subsampling ratio to each interval
	"""
	df = statistics.get_total_pkts_flowid(df)

	df_ranked = statistics.compute_ranking(df, ranges, bins,'total_pkts')

	subsampled = sql_context.createDataFrame(spark_ctx.emptyRDD(), df_ranked.schema)

	ranks = len(ranges) if ranges else bins

	if sample_ratios:

		for i, ratio in zip(range(ranks),sample_ratios):
				subsampled = subsampled.union(df_ranked.filter(df_ranked['rank']==i+1).sample(False, float(ratio), seed=0))

	elif take_first:

		for i, ntake in zip(range(ranks),take_first):

			df_ranked_filtered = df_ranked.filter(df_ranked['rank']==i+1)

			if ntake == 'n':
				subsampled = subsampled.union(df_ranked_filtered)

			else:
				window = Window.partitionBy("flow_id").orderBy(col("first:29").desc())

				subsampled = subsampled.union(df_ranked_filtered.withColumn("r", functions.row_number().over(window)).where(col("r") <= ntake).drop('r'))

	return subsampled
