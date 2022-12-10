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
name = 'Fear-less'

fs = gridfs.GridFS(db)

data = db.fs.files.find_one({'filename' : name})
my_id = data['_id']
outputdata = fs.get(my_id).read()
download_location = "E:\Python-Files\ " + name
output = open(download_location, "wb")
output.write(outputdata)
output.close()
print("Download Completed")