#!/bin/bash

# Start mysql server
systemctl start mysql
echo "started mysql server"

# Setup MySQL objects
sudo mysql < setup_sql.sql
echo "setup sql objects"

# Let SQL Alchemy generate schema from models
python3 ./wsgi.py
echo "schemas initialised"

# Run mod_dummy_data
echo "modifying dummy data"
python3 ./mod_dummy_data.py

# Enable recurse
shopt -s globstar

echo "populating company table"
mysql -e "
   USE external;
   LOAD DATA LOCAL INFILE 'res/temp/companyCodes.csv'
   INTO TABLE company
   FIELDS TERMINATED BY ',' ENCLOSED BY '\"' LINES TERMINATED BY '\n'
   IGNORE 1 ROWS
   (name, id);"

 echo "populating product_seller table"
 mysql -e "
    USE external;
    LOAD DATA LOCAL INFILE 'res/temp/productSellers.csv'
    INTO TABLE product_seller
    FIELDS TERMINATED BY ',' ENCLOSED BY '\"' LINES TERMINATED BY '\n'
    IGNORE 1 ROWS
    (product_name, company_id);"

echo "populating currency table"
for p in res/temp/currencyValues/*.csv; do
  mysql -e "
     USE external;
     LOAD DATA LOCAL INFILE '${p}'
     INTO TABLE currency
     FIELDS TERMINATED BY ',' ENCLOSED BY '\"' LINES TERMINATED BY '\n'
     IGNORE 1 ROWS
     (@valuation_date, code, usd_exchange_rate)
     SET valuation_date = STR_TO_DATE(@valuation_date, '%d/%m/%Y');"
done

echo "populating company_stock table"
for p in res/temp/stockPrices/*.csv; do
  mysql -e "
     USE external;
     LOAD DATA LOCAL INFILE '${p}'
     INTO TABLE company_stock
     FIELDS TERMINATED BY ',' ENCLOSED BY '\"' LINES TERMINATED BY '\n'
     IGNORE 1 ROWS
     (@valuation_date, company_id, stock_price)
     SET valuation_date = STR_TO_DATE(@valuation_date, '%d/%m/%Y'), currency_code = 'USD';"
done

echo "populating product table"
for p in res/temp/productPrices/*.csv; do
  mysql -e "
     USE external;
     LOAD DATA LOCAL INFILE '${p}'
     INTO TABLE product
     FIELDS TERMINATED BY ',' ENCLOSED BY '\"' LINES TERMINATED BY '\n'
     IGNORE 1 ROWS
     (@valuation_date, name, market_price)
     SET valuation_date = STR_TO_DATE(@valuation_date, '%d/%m/%Y'), currency_code = 'USD';"
done

echo "populating derivative table"
for p in res/temp/derivativeTrades/*.csv; do
  mysql -e "
     USE derivatex;
     LOAD DATA LOCAL INFILE '${p}'
     INTO TABLE derivative
     FIELDS TERMINATED BY ',' ENCLOSED BY '\"' LINES TERMINATED BY '\n'
     IGNORE 1 ROWS
     (@date_of_trade, code, asset, buying_party, selling_party, @dummy, notional_curr_code, quantity, @maturity_date, @dummy, @dummy, strike_price)
     SET date_of_trade = STR_TO_DATE(@date_of_trade, '%d/%m/%Y'), maturity_date = STR_TO_DATE(@maturity_date, '%d/%m/%Y');"
done

echo "creating users"
mysql -e "
  USE derivatex;
  INSERT INTO user (f_name, l_name, email, password)
  VALUES
    ('Joe', 'Bloggs', 'joe.bloggs@gmail.com', 'password123'),
    ('John', 'Doe', 'john.doe@gmail.com', 'qwerty123'),
    ('Jane', 'Doe', 'jane.doe@gmail.com', '321ytrewq');
"
echo "creating historical actions"
mysql -e "
  USE derivatex;
  INSERT INTO action
  (derivative_id, user_id, type, timestamp)
  SELECT id,
    (SELECT id FROM user ORDER BY RAND () LIMIT 1),
  'ADD', date_of_trade FROM derivative;
"

# Clear temp directory
echo "clearing temp"
rm -rf res/temp/*

# Restart mysql server
echo "restarting mysql server"
systemctl restart mysql

echo "done"
