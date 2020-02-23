import json
import mysql.connector
import random


# Constants
errorFrequency = {
    1: 0.2,
    2: 0.01
}
idLimit = 50000

# Connect to database
cnx = mysql.connector.connect(user='derivatex_backend', password='qwerty123',
                              host='127.0.0.1',
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

# Set all AMBT33 trades to be with GZED20
cursor.execute('UPDATE derivative SET selling_party = "GZED20" WHERE buying_party = "AMBT33"')

# Select some random AMBT33 trades
cursor.execute(f'SELECT id FROM derivative WHERE buying_party = "AMBT33" AND RAND() < {errorFrequency[1]} AND id < {idLimit}')
errorRecordIds = [x[0] for x in cursor]

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
    #cursor.execute(f"INSERT INTO action (derivative_id, user_id, type, update_log, timestamp) VALUES ({errorId}, 1, 'UPDATE', '{ json.dumps(update_log) }', NOW())")

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
cursor.execute(f'SELECT derivative.id, derivative.quantity FROM derivative WHERE RAND() < {errorFrequency[2]} AND derivative.id < {idLimit}')
result = [x for x in cursor]
errorRecordIds = [x[0] for x in result]
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


# Close the connection to the database
cnx.commit()
cursor.close()
cnx.close()
