#!/bin/bash

# Start mysql server
systemctl start mysql

# Create the database and a user
mysql -e "
  USE mysql;

  drop user if exists 'derivatex_backend'@'localhost';
  create user 'derivatex_backend'@'localhost' identified by 'qwerty123';
  drop database if exists derivatex;
  create database derivatex;
  grant all privileges on derivatex.* to 'derivatex_backend'@'localhost';
  drop database if exists external;
  create database external;
  grant all privileges on external.* to 'derivatex_backend'@'localhost';
  flush privileges;
"
echo "database initialised"

# Let SQL Alchemy generate schema from models
python3 ./wsgi.py
echo "schema initialised"

# Enable recurse
shopt -s globstar

echo "populating company table"
mysql -e "
   USE external;
   LOAD DATA LOCAL INFILE 'res/dummy/companyCodes.csv'
   INTO TABLE company
   FIELDS TERMINATED BY ',' ENCLOSED BY '\"' LINES TERMINATED BY '\n'
   IGNORE 1 ROWS
   (name, id);"

 echo "populating product_seller table"
 mysql -e "
    USE external;
    LOAD DATA LOCAL INFILE 'res/dummy/productSellers.csv'
    INTO TABLE product_seller
    FIELDS TERMINATED BY ',' ENCLOSED BY '\"' LINES TERMINATED BY '\n'
    IGNORE 1 ROWS
    (product_name, company_id);"

echo "populating currency table"
for p in res/dummy/currencyValues/2019/**/*.csv; do
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
for p in res/dummy/stockPrices/2019/**/*.csv; do
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
for p in res/dummy/productPrices/2019/**/*.csv; do
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
for p in res/dummy/derivativeTrades/2019/April/**/*.csv; do
  mysql -e "
     USE derivatex;
     LOAD DATA LOCAL INFILE '${p}'
     INTO TABLE derivative
     FIELDS TERMINATED BY ',' ENCLOSED BY '\"' LINES TERMINATED BY '\n'
     IGNORE 1 ROWS
     (@date_of_trade, @dummy, asset, buying_party, selling_party, @dummy, currency_code, quantity, @maturity_date, @dummy, @dummy, strike_price)
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
# Restart mysql server
echo "restarting mysql server"
systemctl restart mysql

echo "done"
