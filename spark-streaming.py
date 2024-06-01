import pyspark
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, sum as _sum
from pyspark.sql.types import StructType, StringType, IntegerType, TimestampType, StructField



if __name__ == "__main__":
     print(pyspark.__version__)
     
     # Configuring SparkSession
     spark = (SparkSession.builder
              .appName("Realtime Voting System")
              .config('spark.jars.packages', 'org.apache.spark:spark-sql-kafka-0-10_2.13:3.5.1') # Integrate Spark with Kafka
              .config('spark.jars', 'C:\Users\salla\VSC\personal-projects\Realtime-Voting-Project\postgresql-42.7.3.jar') # PostgreSQL driver
              .config('spark.sql.adaptive.enable', 'false') # Disable adaptive query execution
              .getOrCreate() 
              )
     
     vote_schema = StructType([
          StructField('voter_id', StringType(), True),
          StructField('candidate_id', StringType(), True),
          StructField('voting_time', StringType(), True),
          StructField('voter_name', StringType(), True),
          StructField('party_affiliation', StringType(), True),
          StructField('biography', StringType(), True),
          StructField('campaign_platform', StringType(), True),
          StructField('photo_url', StringType(), True),
          StructField('candidate_name', StringType(), True),
          StructField('date_of_birth', StringType(), True),
          StructField('gender', StringType(), True),
          StructField('nationality', StringType(), True),
          StructField('registration_number', StringType(), True),
          StructField('address', StructType([
               StructField('street', StringType(), True),
               StructField('city', StringType(), True),
               StructField('state', StringType(), True),
               StructField('country', StringType(), True),
               StructField('postcode', StringType(), True),
               ])),
          StructField('voter_id', StringType(), True),
          StructField('vote', IntegerType(), True),
          StructField('phone_number', StringType(), True),
          StructField('picture', StringType(), True),
          StructField('registered_age', StringType(), True),          
     ])
     
     votes_df = (spark.readStream
                 .format('kafka')
                 .option('kafka.bootstrap.servers', 'localhost:9092')
                 .option('subscribe', 'votes_topic')
                 .option('startingOffsets', 'earliest')
                 .load()
                 .selectExpr("CAST(value AS STRING )")
                 .select(from_json(col('value'), vote_schema).alias('data'))
                 .select('data.*')
                 )
     
     # Typecasting and Watermarking
     votes_df = votes_df.withColumn('voting_time', col('voting_time').cast(TimestampType())) \
          .withColumn('vote', col('vote').cast(IntegerType()))
     
     enriched_votes_df = votes_df.withWatermark('voting_time', '1 minute')
     
     # Aggregate votes per candidate 
     votes_per_candidates = enriched_votes_df.groupby('candidate_id', 'candidate_name', 'party_affiliation', 'photo_url').agg(_sum('vote').alias('total_votes'))
     
     # Aggregate votes for turnout by location
     turnout_by_location = enriched_votes_df.groupby('address.state').count().alias('total_votes')
     
     votes_per_candidates_to_kafka = (votes_per_candidates.selectExpr('to_json(struct(*)) AS value')
                                      .writeStream
                                      .format('kafka')
                                      .option('kafka.bootstrap.servers', 'localhost:9092')
                                      .option('topic', 'aggregated_votes_per_candidate')
                                      .option('checkpointLocation', 'C:\Users\salla\VSC\personal-projects\Realtime-Voting-Project\checkpoints\checkpoint1')
                                      .outputMode('update')
                                      .start()
                                      )
     
     turnout_by_location_to_kafka = (votes_per_candidates.selectExpr('to_json(struct(*)) AS value')
                                   .writeStream
                                   .format('kafka')
                                   .option('kafka.bootstrap.servers', 'localhost:9092')
                                   .option('topic', 'aggregated_turnout_by_location')
                                   .option('checkpointLocation', 'C:\Users\salla\VSC\personal-projects\Realtime-Voting-Project\checkpoints\checkpoint1')
                                   .outputMode('update')
                                   .start()
                                   )
     
     votes_per_candidates_to_kafka.awaitTermination()
     turnout_by_location_to_kafka.awaitTermination()