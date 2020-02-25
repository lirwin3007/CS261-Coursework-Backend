from datetime import datetime, timedelta
from distutils.dir_util import copy_tree
import os
import csv
import re
import shutil
import glob
import random

# Paths
dummy_path = './res/dummy/'
temp_path = './res/temp/'

def clearTemp():
    for root, dirs, files in os.walk(temp_path, topdown=False):
        for file in files:
            file_path = os.path.join(root, file)
            os.unlink(file_path)
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            shutil.rmtree(dir_path)

# Clear temp
clearTemp()

# Copy dummy data into temp directory
copy_tree(dummy_path, temp_path)

# Do the thing
for dir in os.listdir(temp_path):
    dir_path = os.path.join(temp_path, dir)
    if os.path.isdir(dir_path):
        for root, dirs, files in os.walk(dir_path, topdown=False):
            for name in files:
                try:
                    file_path = os.path.join(root, name)

                    date = datetime.date(datetime.strptime(name[:-4], '%d%m%Y'))
                    date = date.replace(year=date.year + 1)

                    if dir == 'derivativeTrades' and date > date.today():
                        continue

                    name_new = date.isoformat() + '.csv'
                    file_path_new = os.path.join(dir_path, name_new)

                    with open(file_path, 'r') as file, open(file_path_new, 'w') as file_new:
                        reader = csv.DictReader(file)
                        writer = csv.DictWriter(file_new, reader.fieldnames)

                        for i, row in enumerate(reader):
                            if dir == 'derivativeTrades' and i == 100:
                                break

                            for k, v in row.items():
                                if 'date' in k.lower():
                                    year = int(v[6:10])
                                    row[k] = v.replace(str(year), str(year+1))

                            writer.writerow(row)

                except ValueError:
                    continue

            for dir in dirs:
                shutil.rmtree(os.path.join(root, dir))
