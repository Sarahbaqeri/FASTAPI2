from fastapi import FastAPI,HTTPException,status,Response,Depends
from pydantic import BaseModel
from fastapi.params import Body
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time
import models
from database import engine,get_db
from sqlalchemy.orm import session
import schemas
from typing import List
models.Base.metadata.create_all(bind=engine)

app=FastAPI()


posts_list=[{"title":"sara","content":"sara is a student","published":True,"rating":10,"id":1},{"title":"saba","content":"saba is a teacher","rating":4,"id":2},{"title":"shiva","content":"shiva is a manager","published":False,"rating":8,"id":3}]


while True:
    try:
        conn=psycopg2.connect(host='localhost',database='fastapi',user='postgres',password='haras777')
        cursor=conn.cursor()
        print('database connection was sucessfull')
        break
    except Exception as error:
        print('connection to database failed')
        print('error:',error)
        time.sleep(2)


def find_post_id(id:int):    
    for post in posts_list:
        if post['id']==id :
            return post

def find_post_index(id:int):
    for index,post in enumerate(posts_list):
        if post['id']==id:
            return index


@app.get('/')
def root():
    return {'massage':'welcome!!!!!'}

@app.get("/posts",response_model=List[schemas.Post])
def get_all_posts(db:session = Depends(get_db)):
    #cursor.execute("""SELECT * FROM posts""")
    #posts=cursor.fetchall()
    posts=db.query(models.Post).all()
    return posts

@app.post("/posts",status_code=status.HTTP_201_CREATED,response_model=schemas.Post)
def create_post(post:schemas.PostCreate,db:session = Depends(get_db)):
    #cursor.execute("""INSERT INTO posts (title,content,published) VALUES(%s,%s,%s)RETURNING *""",(post.title,post.content,post.published))
    #new_post=cursor.fetchone()
    #conn.commit()
    post.dict()
    new_post=models.Post(**post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@app.get("/posts/{id}",response_model=schemas.Post)
def find_by_id(id:int,db:session = Depends(get_db)):
    #cursor.execute("""SELECT * FROM posts WHERE id=(%s)""",(str(id)))
    #post=cursor.fetchone()
    post=db.query(models.Post).filter(models.Post.id==id).first()
    if not post :
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"this post was not found")
    return post            

@app.delete("/posts/{id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id:int,db:session = Depends(get_db)):
    #cursor.execute("""DELETE FROM posts WHERE id=%s RETURNING *""",(str(id)))
    #deleted_post=cursor.fetchone()
    #conn.commit()
    post=db.query(models.Post).filter(models.Post.id==id)
    if post.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"post with id:{id} does not exist")
    post.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put("/posts/{id}",response_model=schemas.Post)
def update_post(id:int,updated_post:schemas.PostBase,db:session = Depends(get_db)):
    #cursor.execute("""UPDATE posts SET title=%s, content=%s, published=%s WHERE id=%s RETURNING * """,(post.title,post.content,post.published,(str(id))))
    #updated_post=cursor.fetchone()
    #conn.commit()
    post_query=db.query(models.Post).filter(models.Post.id==id)
    post1=post_query.first()
    if post1 == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"post with id:{id} does not exist")
    post_query.update(updated_post.dict(),synchronize_session=False)   
    db.commit()
    return post_query.first()