# some functionalities to process the datasets

from pyspark.sql import SQLContext
from pyspark.sql.functions import rank, min, dense_rank, percent_rank, ntile, col
from pyspark.sql.window import Window
import csv

def subsampling(df, sample_ratios):
	
	for ratio in sample_ratios:
		list = df.filter(df['rank']==i).rdd.takeSample(False, round((ratio)*df.count()), seed=0)