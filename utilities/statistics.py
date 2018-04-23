# some functionalities to compute statistics

from pyspark.sql import SQLContext
from pyspark.sql.functions import rank, min, dense_rank, percent_rank, ntile, col
from pyspark.sql.window import Window
import csv

def get_total_pkts_flowid(df):

	# Group by Connections ID = IP Client, Server / Port Client, Server and Sum of pkts in Server and Client
	connect_pkts =  df.groupby(['#c_ip:1','c_port:2','s_ip:15','s_port:16','tag:132']).agg({'c_pkts_all:3':'sum','s_pkts_all:17':'sum'})

	# Get npackets per flow
	connect_pkts = connect_pkts.withColumn('total_pkts',connect_pkts['sum(c_pkts_all:3)'].__add__(connect_pkts['sum(s_pkts_all:17)']))

	return connect_pkts


def compute_ranking(df, ranges=None, bins=None):

	connect_pkts = get_total_pkts_flowid(df)

	if bins:
	   wSpec3 = Window.orderBy('total_pkts')
	   connect_ranks = connect_pkts.withColumn("rank", ntile(bins).over(wSpec3))
	   rank_count = connect_ranks.groupby('rank').agg({'rank':'count'})

	if ranges:
		rank = 1
		for range in ranges: 
		 	connect_ranks = connect_ranks.withColumn('rank',when( (connect_ranks['total_pkts'] >= range[0]) & (connect_ranks['total_pkts'] <= range[1]) , rank).otherwise(-1))
		 	rank += 1

	# add the rank to the subflows/rows of the original dataset
	df_rank = df.alias('a').join(connect_ranks.alias('b'), (col('a.#c_ip:1') == col('b.#c_ip:1')) & (col('a.c_port:2') == col('b.c_port:2')) & (col('a.s_ip:15') == col('b.s_ip:15')) & (col('a.s_port:16') == col('b.s_port:16')) & (col('a.tag:132') == col('b.tag:132')), how="left").select([col('a.'+ xx) for xx in df.columns] + [col('b.rank')])

	return df_rank, rank_count
