import json

import mysql.connector

# Constants
errorPercentage = 0.4
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

cursor.execute('UPDATE derivative SET selling_party = "GZED20" WHERE buying_party = "AMBT33"')

cursor.execute(f'SELECT id FROM derivative WHERE buying_party = "AMBT33" AND RAND() <= {errorPercentage} AND id < {idLimit}')
errorRecordIds = [x[0] for x in cursor]

cursor.execute(f'SELECT selling_party FROM derivative WHERE RAND() <= 0.05 AND selling_party != "GZED20"')
sellingParties = [x[0] for x in cursor]

count = 0
for errorId in errorRecordIds:
    update_log = {
        'attribute': 'selling_party',
        'new_value': 'GZED20',
        'old_value': sellingParties[count]
    }
    count += 1
    cursor.execute(f"INSERT INTO action (derivative_id, user_id, type, update_log, timestamp) VALUES ({errorId}, 1, 'UPDATE', '{ json.dumps(update_log) }', NOW())")

# Close the connection to the database
cnx.commit()
cursor.close()
cnx.close()
