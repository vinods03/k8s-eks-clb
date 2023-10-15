import json
import pickle
import numpy as np
import pymysql
import time
import sys
import boto3
from flask import Flask, request

ssm = boto3.client('ssm', region_name = 'us-east-1')
rds_db_password_parameter = ssm.get_parameter(Name='/rds/password')
rds_db_password = rds_db_password_parameter['Parameter']['Value']
# print('The rds db password is ', rds_db_password)

# Set the database credentials
host = 'database-1.cy9jvehoizhi.us-east-1.rds.amazonaws.com'
port = 3306
user = 'admin'
password = rds_db_password
database = 'ml_db'

model_name = 'diamond_price_dt_model.pkl'
diamond_price_model = pickle.load(open(model_name,'rb'))

app = Flask(__name__)

@app.route('/health_check', methods = ['GET'])
def health_checker(event = None, context = None):

# We will use database availibility + our table availibility for health check
# Below chunk is commented out, because even when health check fails (simulated through querying an incorrect table), print(r) returns status code 200

    try:       
        connection = pymysql.connect(
            host = host,
            port = port,
            user = user,
            password = password,
            database = database
           )
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM ml_db.diamond_price_app limit 1')
        results = cursor.fetchall()
        for result in results:
          print(result)
        return "Health check has completed"
        
    finally:
         connection.close()


@app.route('/diamond_price_predict', methods = ['POST'])
def diamond_price_predictor(event = None, context = None):
    
        print('the model name is ', model_name)
        
        processing_timestamp = time.time()
        run_id = int(processing_timestamp - (processing_timestamp % 60))
        
        data = request.get_json()
        
        carat = data['carat']
        cut = data['cut']
        color = data['color']
        clarity = data['clarity']
        depth = data['depth']
        tbl = data['table']
        x = data['x']
        y = data['y']
        z = data['z']
        
        cut_Fair = 0
        cut_Good = 0
        cut_Ideal = 0
        cut_Premium = 0
        cut_VeryGood = 0
    
        color_D = 0
        color_E = 0
        color_F = 0
        color_G = 0
        color_H = 0
        color_I = 0
        color_J = 0
        
        clarity_I1 = 0
        clarity_IF = 0
        clarity_SI1 = 0
        clarity_SI2 = 0
        clarity_VS1 = 0
        clarity_VS2 = 0
        clarity_VVS1 = 0
        clarity_VVS2 = 0
                    
        if cut == 'Fair':
            cut_Fair = 1
        elif cut == 'Good':
            cut_Good = 1
        elif cut == 'Ideal':
            cut_Ideal = 1
        elif cut == 'Very Good':
            cut_VeryGood = 1
        elif cut == 'Premium':
            cut_Premium = 1
        else:
            cut_Good = 1
                
                
        if color == 'D':
            color_D = 1
        elif color == 'E':
            color_E = 1
        elif color == 'F':
            color_F = 1
        elif color == 'G':
            color_G = 1
        elif color == 'H':
            color_H = 1
        elif color == 'I':
            color_I = 1
        elif color == 'J':
            color_J = 1
        else:
            color_G = 1
                
                        
        if clarity == 'I1':
            clarity_I1 = 1
        elif clarity == 'IF':
            clarity_IF = 1
        elif clarity == 'SI1':
            clarity_SI1 = 1
        elif clarity == 'SI2':
            clarity_SI2 = 1
        elif clarity == 'VS1':
            clarity_VS1 = 1
        elif clarity == 'VS2':
            clarity_VS2 = 1
        elif clarity == 'VVS1':
            clarity_VVS1 = 1
        elif clarity == 'VVS2':
            clarity_VVS2 = 1
        else:
            clarity_SI2 = 1
             
               
        input_to_model = np.array([[
             carat,
             depth,
             tbl,
             x,
             y,
             z,
             cut_Fair,
             cut_Good,
             cut_Ideal,
             cut_Premium,
             cut_VeryGood,
             color_D,
             color_E,
             color_F,
             color_G,
             color_H,
             color_I,
             color_J,
             clarity_I1,
             clarity_IF,
             clarity_SI1,
             clarity_SI2,
             clarity_VS1,
             clarity_VS2,
             clarity_VVS1,
             clarity_VVS2
            ]])
            
        print('input_to_model is ', input_to_model)
        
        try:        
            diamond_price_arr = diamond_price_model.predict(input_to_model)
            print('Prediction is successful')
            # print(type(diamond_price_arr))
        except Exception as e:
            print('Prediction failed. The exception is ', e)
            
        try: 
            diamond_price = diamond_price_arr.tolist()[0]
            print('Extracted the predicted value successfully')
            # print(type(diamond_price))
            # print(diamond_price)
        except Exception as e:
            print('Extraction of predicted value failed. The exception is ', e)
        
        # Create a cursor object using the previously created connection object, execute insert, commit, close cursor object and connection
        # cursor = connection.cursor()
        
        try:   
            connection = pymysql.connect(
                host = host,
                port = port,
                user = user,
                password = password,
                database = database
               )
            cursor = connection.cursor()        
            cursor.execute("insert into diamond_price_app (run_id, carat, cut, color, clarity, depth, tbl, x, y, z, diamond_price) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (run_id, carat, cut, color, clarity, depth, tbl, x, y, z, diamond_price))
            print('Successfully made an entry into DB')
            cursor.close()
            connection.commit()
        finally:
            cursor.close()
            connection.commit()
            connection.close()

        
        final_output = 'The run id is ' +str(run_id) +' and the dimanond price is ' +str(diamond_price)
        return final_output
            
if __name__ == "__main__":
    app.run(host='0.0.0.0')
    
        

        

        

            
    
