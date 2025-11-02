import sqlite3

conn = sqlite3.connect('memes.db')
cursor = conn.cursor()

#cursor.execute('''
#CREATE TABLE IF NOT EXISTS memes (
#               name TEXT NOT NULL,
#               url TEXT NOT NULL
#               )
#               ''')

#for meme in memes:
    #cursor.execute('INSERT INTO memes (name, url) VALUES (?, ?)', (f'{meme['answer']}',f'{meme['url']}'))

conn.commit()
