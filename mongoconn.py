from pymongo import MongoClient
import gridfs

def mongo_conn():
    try:
        conn = MongoClient(host='127.0.0.1', port = 27017)
        print('Mongo Connected',conn)
        return conn.grid_file
    except Exception as e:
        print("Error in MongoConnection",conn)

db = mongo_conn()
name = 'arcade'
file_location = "D:\Songs\Arcade.mp3"
file_data = open(file_location, "rb")
data = file_data.read()

fs = gridfs.GridFS(db)

fs.put(data, filename = name)
print('Upload Complete')
