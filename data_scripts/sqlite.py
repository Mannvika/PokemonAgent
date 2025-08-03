import sqlite3
import json

connection = sqlite3.connect('./pokemon.db')

cursor = connection.cursor()

# sql = 'create table if not exists towns (name text primary key, lore text)'
sql = 'drop table if exists trainers'
cursor.execute(sql)
sql = 'create table if not exists trainers (name text primary key, lore text)'
cursor.execute(sql)

with open('trainers.json', 'r') as file:
    lore_data = json.load(file)

for entry in lore_data:
    name = entry['title']
    lore = entry['lore']
    sql = 'insert or ignore into trainers (name, lore) values (?, ?)'
    cursor.execute(sql, (name, lore))

#cursor.execute(sql)
connection.commit()
connection.close()