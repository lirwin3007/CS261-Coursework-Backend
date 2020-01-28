import csv, os

dummypath = os.path.dirname(__file__) + '/../dummy/'

def restructureCsv(source, dest, columns):
    with open(dummypath+source, 'r') as infile, open(dummypath+dest, 'w+') as outfile:
        next(infile)
        writer = csv.writer(outfile)
        writer.writerow([name for name,_ in columns])
        for row in csv.reader(infile):
            writer.writerow([row[index] for _,index in columns])

def restructureCsvDir(source, dest, columns):
    with open(dummypath+dest, 'w+') as outfile:
        writer = csv.writer(outfile)
        writer.writerow([name for name,_ in columns])

        for dirpath,_, filenames in os.walk(dummypath+source):
            for filename in filenames:
                if filename.endswith('.csv'):
                    with open(dirpath+'/'+filename, 'r') as infile:
                        next(infile)
                        for row in csv.reader(infile):
                            writer.writerow([row[index] for _,index in columns])

restructureCsvDir('currencyValues/', 'currency.csv', [('code',1),('valuation_date',0),('usd_exchange_rate',2)])
restructureCsvDir('derivativeTrades/', 'derivative.csv', [('id',1),('buying_party',3),('selling_party',4),('asset',2),('quantity',7),('strike_price',11),('currency_code',6),('maturity_date',8)])
restructureCsvDir('productPrices/', 'product.csv', [('name',1),('valuation_date',0),('market_price_usd',2)])
restructureCsvDir('stockPrices/', 'company_share.csv', [('company_id',1),('valuation_date',0),('share_price_usd',2)])
restructureCsv('companyCodes.csv', 'company.csv', [('code',1),('name',0)])
restructureCsv('productSellers.csv', 'product_seller.csv', [('company_id',1),('product_name',0)])
