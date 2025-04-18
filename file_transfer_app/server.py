from fastapi import FastAPI, UploadFile, File
import mysql.connector, uuid, sys
from datetime import datetime 
import functools
# from conf.base import DatabasePool
from .conf.base import DatabasePool
from typing import Dict, Any
import json

# Server init
server = FastAPI()

# DB connection
def get_db_conn():
    connection = DatabasePool.get_connnection()
    if not connection:
        print("Mysql connection is not established. Quitting!")
        sys.exit()
    return connection

def close_db_conn(conn):
    DatabasePool.release_connection(conn)

# decorator
def return_response(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        response, statuscode = func(*args, **kwargs)
        return response, statuscode
    return wrapper

# server routes

@server.post("/uploads/requirements/{file_id}")
async def upload_requirements(file_id: str, file: UploadFile = File(...)):
    content = await file.read()   
    if not file_id: return {"error": "Missing file_id"}, 400 
    try:
        db = get_db_conn()
        cursor = db.cursor(dictionary=True)
        query = """
        UPDATE models
        SET requirements_filename = %s,
        requirements_content = %s
        WHERE id = %s;        
        """
        db.start_transaction()
        cursor.execute(query, (file.filename, content, file_id))
        db.commit()
        return {"message": "Requirements inserted succesfully!", "filename": file.filename}, 200
    except Exception as e:
        db.rollback()
        print(e)
        return {"error": "Internal Server Error"}, 500    
    finally:
        cursor.close()
        close_db_conn(db)

@server.post("/uploads/params/{file_id}")
def upload_params(file_id: str, params: Dict[str, Any]):    
    try:
        db = get_db_conn()
        cursor = db.cursor(dictionary=True)
        query = """
        UPDATE models
        SET learning_rate = %s,
        momentum = %s, initial_params = %s
        WHERE id = %s;        
        """
        learning_rate = params["learning_rate"]
        momentum = params["momentum"]
        initial_params = json.dumps(params["initial_params"])
        db.start_transaction()
        cursor.execute(query, (learning_rate, momentum, initial_params, file_id))
        db.commit()
        return {"message": "Params inserted succesfully!", "filename": file_id}, 200
    except Exception as e:
        db.rollback()
        print(e)
        return {"error": "Internal Server Error"}, 500    
    finally:
        cursor.close()
        close_db_conn(db)    


@server.post("/uploads/model")
async def upload_files(file: UploadFile = File(...)):    
    
    content = await file.read()
    file_id = str(uuid.uuid4())
    try:
        db = get_db_conn()
        cursor = db.cursor(dictionary=True)
        query = """
        INSERT INTO models (id, model_filename, model_content, upload_time)
        VALUES (%s, %s, %s, %s);
        """
        db.start_transaction()
        cursor.execute(query, (file_id, file.filename, content, datetime.now()))
        db.commit()
        return {"message": "Model inserted successfully!", "file_id": file_id, "filename": file.filename}, 200        
    except Exception as e:
        db.rollback()
        print(e)
        return {"error": "Model storing failed. Try again!"}, 500
    finally:
        cursor.close()
        close_db_conn(db)
    
@server.get("/files/{file_id}")
def get_file(file_id: str):
    try:
        db = get_db_conn()
        cursor = db.cursor(dictionary=True)
        query = """
        SELECT id, filename, content, upload_time
        FROM models WHERE id = %s;
        """
        cursor.execute(query, (file_id, ))
        data = cursor.fetchone()
        id = data.get("id", file_id)
        filename = data.get("filename", None)
        content = data.get("content", None)
        upload_time = data.get("upload_time", None)
        return {"message": "File fetched successfuly", "file": {
            "file_id": id,
            "filename": filename,
            "content": content,
            "upload_time": upload_time
        }}, 200
    except Exception as e:
        print(e)
        return {"error": "Failed while fetching file. Try Again"}, 500
    finally:
        cursor.close()
        close_db_conn(db)

@server.get("/")
def check_health():
    return {"message": "hello from file server!"}, 200