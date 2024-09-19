import typing
import strawberry
import sqlite3
import bcrypt
import jwt
import datetime
import random

from typing import Optional, List
from pydantic import BaseModel, EmailStr, constr, ValidationError
from fastapi import Request, HTTPException


secret_key = '8f7e70f91a23b4f0b935e9d7c4fbd65f89e9b9d2537188b3f4e4df48e92b38ed'

class RegisterUserModel(BaseModel):
    email: EmailStr
    name: constr(min_length=1)
    password: constr(min_length=8)
    adminflg: Optional[bool]

class RegisterMessageModel(BaseModel):
    title: constr(min_length=1, max_length=16)
    message: constr(min_length=1, max_length=128)


def verify_jwt(request: Request) -> dict:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization header missing or malformed")
    token = auth_header[len("Bearer "):]
    
    try:
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        if payload["tmp"]:
            raise HTTPException(status_code=401, detail="Invalid tmp token") 
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


def verify_tmp_jwt(request: Request) -> dict:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization header missing or malformed")
    token = auth_header[len("Bearer "):]
    
    try:
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        if not payload["tmp"]:
            raise HTTPException(status_code=401, detail="Invalid tmp token") 
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def check_password(stored_password: str, provided_password: str) -> bool:
    return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password.encode('utf-8'))
    
def jwt_create(user_id, username, tmpflg):
    payload = {
    'user_id': user_id,
    'username': username,
    'iat': datetime.datetime.utcnow(),
    'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1),
    'tmp': tmpflg
    }

    token = jwt.encode(payload, secret_key, algorithm='HS256')
    return token

def get_author(root: "Thread") -> "User":
    with sqlite3.connect('demo.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT authorid FROM threds WHERE id = ?", (root.id,))
        author_id_row = cursor.fetchone()
    
        if author_id_row:
            author_id = author_id_row[0]
            cursor.execute("SELECT id, name, email, adminflg FROM users WHERE id = ?", (author_id,))
            user_row = cursor.fetchone()
        
    if user_row:
        return User(id=user_row[0], name=user_row[1], email=user_row[2], admin=bool(user_row[3]))
    
    return None

def get_user_threads(root: "User") -> List["Thread"]:
    with sqlite3.connect('demo.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, detail, memo FROM threds WHERE authorid = ?", (root.id,))
    rows = cursor.fetchall()
    columns = [description[0] for description in cursor.description]
            
    id_index = columns.index('id')
    title_index = columns.index('title')
    detail_index = columns.index('detail')
    memo_index = columns.index('memo')
            
    return [
        Thread(id=row[id_index], title=row[title_index], detail=row[detail_index], secretmemo=row[memo_index] )
        for row in rows
    ]
    

@strawberry.type
class User:
    id: int
    name: str
    email: str
    admin: bool
    threads: Optional[List["Thread"]] = strawberry.field(resolver=get_user_threads)
    
@strawberry.type
class Thread:
    id: int
    title: str
    detail: str
    secretmemo: Optional[str]
    author: "User" = strawberry.field(resolver=get_author)
    
@strawberry.type
class Flag:
    message: str    

@strawberry.type
class Login:
    status: str
    tmpToken: Optional[str]
    accessToken: Optional[str]
    
@strawberry.type
class LoginOTP:
    status: str
    accessToken: Optional[str]
    
@strawberry.type
class RegisterUser:
    status: str
    message: Optional[str]

@strawberry.type
class PostMessage:
    status: str
    message: Optional[str]
     

#Query型
@strawberry.type
class Query:
    @strawberry.field
    def thread(self) -> typing.List[Thread]:
        with sqlite3.connect('demo.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM threds')
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
            
        id_index = columns.index('id')
        title_index = columns.index('title')
        detail_index = columns.index('detail')
        memo_index = columns.index('memo')
            
        return [
            Thread(id=row[id_index], title=row[title_index], detail=row[detail_index], secretmemo=row[memo_index])
            for row in rows
        ]

    @strawberry.field
    def flag(self, info: strawberry.types.Info) -> Flag:
        payload = verify_jwt(info.context["request"])
        user_id = payload["user_id"]
        
        with sqlite3.connect('demo.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        row = cursor.fetchone()
        
        columns = [description[0] for description in cursor.description]
        adminflg_index = columns.index('adminflg')
        
        if row[adminflg_index]:
            message = "flag{VGhhbmsgeW91IGZvciBwYXJ0aWNpcGF0aW5nIGluIHRoZSBldmVudC4=}"
        else:
            message = "管理者権限でのアクセスが必要です"
           
        return Flag(message=message)


@strawberry.type    
class Mutation:
    @strawberry.field
    def login(self, email: str, password: str) -> Login:
        
        with sqlite3.connect('demo.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        row = cursor.fetchone()
        
        columns = [description[0] for description in cursor.description]
        password_index = columns.index('password')
        
        if row:
            stored_password = row[password_index]
            
            if check_password(stored_password, password):
                id_index = columns.index('id')
                name_index = columns.index('name')
                adminflg_index = columns.index('adminflg')
                
                if row[adminflg_index] == True:
                    random_number = random.randint(0, 9999)
                    code = f"{random_number:04d}"
                    with sqlite3.connect('demo.db') as conn:
                        cursor = conn.cursor()
                        cursor.execute('''
                        UPDATE users
                        SET code = ?, codeexp = CURRENT_TIMESTAMP
                        WHERE id = ?
                        ''', (code, row[id_index]))

                    status = "success"
                    tmp_token = jwt_create(row[id_index], row[name_index], True)
                    access_token = None
                else:
                    status = "success"
                    tmp_token = None
                    access_token = jwt_create(row[id_index], row[name_index], False)
                    
                return Login(status=status, tmpToken=tmp_token, accessToken=access_token)
        
        status = "error"
        tmp_token = None
        access_token = None
        return Login(status=status, tmpToken=tmp_token, accessToken=access_token)
        
        
    @strawberry.field
    def loginotp(self, info: strawberry.types.Info, code: str) -> LoginOTP:
        payload = verify_tmp_jwt(info.context["request"])
        user_id = payload["user_id"]
        
        with sqlite3.connect('demo.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
            SELECT * FROM users 
            WHERE id = ? 
            and code = ? 
            and codeexp >= datetime('now', '-3 minutes')''', (user_id, code))
        row = cursor.fetchone()
        
        if row:
            columns = [description[0] for description in cursor.description]
            id_index = columns.index('id')
            name_index = columns.index('name')
            
            with sqlite3.connect('demo.db') as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE users
                    SET code = ?
                    WHERE id = ?
                    ''', (None, row[id_index]))
            
            status = "success"
            tmp_token = None
            access_token = jwt_create(row[id_index], row[name_index], False)
            
            return LoginOTP(status=status, accessToken=access_token)
        
        status = "error"
        tmp_token = None
        access_token = None
        return LoginOTP(status=status, accessToken=access_token)
    
    
    @strawberry.field
    def register_user(self, email: str, name: str, password: str, adminflg: Optional[bool] = False) -> RegisterUser:   
        try:
            RegisterUserModel(email=email, name=name, password=password, adminflg=adminflg)
            hashed_password = hash_password(password)
            
            with sqlite3.connect('demo.db') as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO users (name, email, password, adminflg) 
                    VALUES (?, ?, ?, ?)'''
                    , (name, email, hashed_password, adminflg))
                conn.commit()
                
            status = "success"
            message = None
            
        except ValidationError as e:
            status = "error"
            message = f"Validation error: {e}"
        
        return RegisterUser(status=status, message=message)

        
    @strawberry.field
    def post_message(self, info: strawberry.types.Info, title: str, message: str) -> PostMessage:
        payload = verify_jwt(info.context["request"])
        user_id = payload["user_id"]
        
        try:
            RegisterMessageModel(title=title, message=message)            
            with sqlite3.connect('demo.db') as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO threds (title, detail, authorid)
                    VALUES (?, ?, ?)
                    '''
                    , (title, message, user_id))
                conn.commit()
                
            status = "success"
            message = None
            
        except ValidationError as e:
            status = "error"
            message = f"Validation error: {e}"
        
        return RegisterUser(status=status, message=message)
