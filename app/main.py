from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body 
from pydantic import BaseModel
from typing import Optional
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time
app = FastAPI()

class Post(BaseModel):
    title: str
    content: str
    published: bool = True

my_posts = [{"title": "Title of post1", "content": "content of post1","id": 1},{
    "title": "title of post2", "content":"content of post 2","id": 2}]

# Connect to database
while True:
    try:
        conn = psycopg2.connect(host = "localhost", database ='fastapi', user = 'postgres',
        password = 'Kshs030714',cursor_factory=RealDictCursor )
        cursor = conn.cursor()
        print("Database connection successful")
        break
    except Exception as error:
        print("Connection to database failed")
        print("Error:", error)
        time.sleep(2)


# API functions
@app.get("/")
def root():
    return {"BOBO": "Strays House Keeper"}

@app.get("/posts")
def get_posts():
    cursor.execute("""SELECT * FROM posts """)
    posts = cursor.fetchall()
    return {"data":posts}

@app.post("/posts", status_code = status.HTTP_201_CREATED)
def create_post(post: Post):
    insert_query = """
    INSERT INTO posts (title, content, published)
    VALUES (%s, %s, %s)
    RETURNING *
    """
    cursor.execute(insert_query,(post.title, post.content, post.published))
    conn.commit()
    new_post = cursor.fetchone()
    return {"data":new_post}
# title str, content str

@app.get("/posts/{id}") # {id} is called path parameter: always a string
def get_post(id: int): # id: int automatically convert the path parameter into an integer, and if retrun message if unconvertable.
    quer = """
    SELECT * FROM posts WHERE id = %s
    """
    cursor.execute(quer, (str(id)))
    post = cursor.fetchall()    
    print(post)
    if not post:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,
                            detail= f"post with id {id} not found")
    return{"post detail": post}

@app.delete("/posts/{id}", status_code = status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    quer = """
    DELETE FROM posts WHERE id = %s
    RETURNING *
    """
    cursor.execute(quer, (str(id,)))
    conn.commit()
    delete_post = cursor.fetchone()
    if not delete_post:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,
                            detail = f"post with id {id} not found")
    return Response(status_code = status.HTTP_204_NO_CONTENT)

@app.put("/posts/{id}")
def update_post(id:int,post: Post):
    quer = """
    UPDATE posts SET title = %s , content = %s, published = %s WHERE id = %s
    RETURNING *
    """
    cursor.execute(quer, (post.title, post.content,post.published,str(id),))
    updated_post = cursor.fetchone()
    conn.commit()
    if not updated_post:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,
                            detail= "post with id :{id} doesn't exist")
    return{"Post":updated_post}
    