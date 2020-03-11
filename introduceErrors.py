# flake8: noqa

import json
import mysql.connector
import random


# Constants
errorFrequency = {
    1: 0.1,             # 0.1
    2: 0.05,          # 0.05
    3: 0.0
}
idLimit = 25000

# Connect to database
cnx = mysql.connector.connect(user='derivatex_backend', password='qwerty123',
                              host='localhost',
                              database='derivatex')
cursor = cnx.cursor()

##############################################
#                  Error 1                   #
#                                            #
#   Premise: company AMBT33 always trades    #
#   with company GZED20.                     #
#                                            #
#   Error: Company AMBT33 trades with a      #
#   company other than GZED20                #
#                                            #
##############################################

# Introduce some more AMBT33 Trades
cursor.execute(f'SELECT id FROM derivative WHERE id < {idLimit}')
newTrades = [x[0] for x in cursor]
for tradeId in random.sample(newTrades, int(errorFrequency[1] * idLimit)):
    cursor.execute(f'UPDATE derivative SET buying_party = "AMBT33" WHERE id = {tradeId}')

# Set all AMBT33 trades to be with GZED20
cursor.execute('UPDATE derivative SET selling_party = "GZED20" WHERE buying_party = "AMBT33"')

# Select some random AMBT33 trades
cursor.execute(f'SELECT id FROM derivative WHERE buying_party = "AMBT33" AND id < {idLimit}')
errorRecordIds = [x[0] for x in cursor]
errorRecordIds = random.sample(errorRecordIds, int(errorFrequency[1] * len(errorRecordIds)))

# Select some random other selling parties
cursor.execute(f'SELECT selling_party FROM derivative WHERE RAND() <= 0.05 AND selling_party != "GZED20"')
sellingParties = [x[0] for x in cursor]

# Loop through each random AMBT33 trade and insert an update record
# to make it look like an error was made in the past
count = 0
for errorId in errorRecordIds:
    update_log = {
        'attribute': 'selling_party',
        'new_value': 'GZED20',
        'old_value': sellingParties[count]
    }
    count += 1
    if count >= len(sellingParties):
        count = 0
    cursor.execute(f"INSERT INTO action (derivative_id, user_id, type, update_log, timestamp) VALUES ({errorId}, 1, 'UPDATE', '{ json.dumps(update_log) }', NOW())")

print(f"Error 1 - {len(errorRecordIds)}")

##############################################
#                  Error 2                   #
#                                            #
#   Error: A fat finger error has resulted   #
#   in the quantity of trades to be entered  #
#   as significantly bigger (10x - 100x)     #
#   than desired.                            #
#                                            #
##############################################

# Select some random trades
cursor.execute(f'SELECT derivative.id, derivative.quantity FROM derivative WHERE derivative.id < {idLimit}')
result = [x for x in cursor]
errorRecordIds = [x[0] for x in result]
errorRecordIds = random.sample(errorRecordIds, int(errorFrequency[2] * idLimit))
quantities = [x[1] for x in result]

# Loop through each random trade and insert an update record
# to make it look like an error was made in the past
count = 0
for errorId in errorRecordIds:
    update_log = {
        'attribute': 'quantity',
        'new_value': quantities[count],
        'old_value': quantities[count] * random.randint(10, 100)
    }
    count += 1
    cursor.execute(f"INSERT INTO action (derivative_id, user_id, type, update_log, timestamp) VALUES ({errorId}, 1, 'UPDATE', '{ json.dumps(update_log) }', NOW())")

print(f"Error 2 - {len(errorRecordIds)}")

##############################################
#                  Error 3                   #
#                                            #
#   Premise: company AHMZ79 only sells       #
#   Focus Bands to company EPZN28. It        #
#   will not trade Focus Bands to anyone     #
#   else                                     #
#                                            #
#   Error: Company AHMZ79 trades focus       #
#   bands with a company other than EPZN28   #
#                                            #
##############################################

# Create some more trades to work with
cursor.execute(f'SELECT id FROM derivative WHERE id < {idLimit}')
newTrades = [x[0] for x in cursor]
for tradeId in random.sample(newTrades, int(errorFrequency[3] * idLimit * 0.5)):
    cursor.execute(f'UPDATE derivative SET asset = "Focus Bands" WHERE id = {tradeId}')
for tradeId in random.sample(newTrades, int(errorFrequency[3] * idLimit)):
    cursor.execute(f'UPDATE derivative SET selling_party = "AHMZ79" WHERE id = {tradeId}')

# Set all Focus Band trades to be between AHMZ79 and EPZN28
cursor.execute('UPDATE derivative SET selling_party = "AHMZ79", buying_party = "EPZN28" WHERE asset = "Focus Bands"')

# Select some random non Focus Band trades
cursor.execute(f'SELECT id, asset FROM derivative WHERE asset != "Focus Bands" AND selling_party = "AHMZ79" AND id < {idLimit}')
errorRecordIds = [x for x in cursor if "'" not in x[1]]
errorRecordIds = random.sample(errorRecordIds, int(errorFrequency[3] * len(errorRecordIds)))

# Loop through each random non focus band trade and insert an update record
# to make it look like it was a focus band trade in the past
for error in errorRecordIds:
    update_log = {
        'attribute': 'asset',
        'new_value': error[1],
        'old_value': 'Focus Bands'
    }
    cursor.execute(f"INSERT INTO action (derivative_id, user_id, type, update_log, timestamp) VALUES ({error[0]}, 1, 'UPDATE', '{ json.dumps(update_log) }', NOW())")

print(f"Error 3 - {len(errorRecordIds)}")

# Close the connection to the database
cnx.commit()
cursor.close()
cnx.close()
