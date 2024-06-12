import json
import random

import psycopg2
import requests
from confluent_kafka import SerializingProducer

from database import create_tables, insert_candidates, insert_voters

GENERATE_USER_URL = 'https://randomuser.me/api/?nat=nl'
PARTIES = ["Labour_Party", "Farmer_Party", "Party_Party"]

random.seed(21)

 
def generate_candidate_data(candidate_index, total_parties):
    response = requests.get(GENERATE_USER_URL + '&gender=' + ('female' if candidate_index %2 == 1 else 'male'))
     
    if response.status_code == 200:
        candidate_data = response.json()['results'][0]
        
        return {
            'candidate_id': candidate_data['login']['uuid'],
            'candidate_name': f"{candidate_data['name']['first']} {candidate_data['name']['last']}",
            'party_affiliation': PARTIES[candidate_index % total_parties],
            'biography': 'Biography of the candidate',
            'campaign_platform': 'Key campaign promises',
            'photo_url': candidate_data['picture']['large']
        }
    else: 
        return "Error fetching candidate data!"
    
def generate_voter_data():
    response = requests.get(GENERATE_USER_URL)
    
    if response.status_code == 200:
        voter_data = response.json()['results'][0]
        
        return {
            'voter_id': voter_data['login']['uuid'],
            'voter_name': f"{voter_data['name']['first']} {voter_data['name']['last']}",
            'date_of_birth': voter_data['dob']['date'],
            'gender': voter_data['gender'],
            'nationality': voter_data['nat'],
            'registration_number': voter_data['login']['username'],
            'address': {
                'street': f"{voter_data['location']['street']['number']} {voter_data['location']['street']['name']}",
                'city': voter_data['location']['city'],
                'state': voter_data['location']['state'],
                'country': voter_data['location']['country'],
                'postcode': voter_data['location']['postcode'],
            },
            'email': voter_data['email'],
            'phone_number': voter_data['phone'],
            'picture': voter_data['picture']['large'],
            'registered_age': voter_data['registered']['age']
        }
    else:
        return "Error fetching voter data!"

 
def delivery_report(err, msg):
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")

if __name__ == "__main__":
    producer = SerializingProducer({'bootstrap.servers': 'localhost:9092'})
    
    try:
        conn = psycopg2.connect(
            dbname="voting",
            user="postgres",
            password="postgres",
            host="localhost",
            port="5432"
        )        
        cur = conn.cursor()
        
        create_tables(conn, cur)
        cur.execute(
            """
            SELECT * FROM candidates
            """
        )
        
        candidates = cur.fetchall()
        
        if len(candidates) == 0:
            for i in range(3):
                candidate = generate_candidate_data(i, 3)
                
                insert_candidates(conn, cur, candidate)
                continue          

                
        for i in range(50):
            voter = generate_voter_data()
            insert_voters(conn, cur, voter)
            
            producer.produce(
                "voters_topic",
                key=voter['voter_id'],
                value=json.dumps(voter),
                on_delivery=delivery_report
            )
            
            print('Produced voter {}, data:{}'.format(i, voter))
            producer.flush()
            
                      
    except Exception as e:
        print(e)