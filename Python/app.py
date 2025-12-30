import sqlite3 
from argon2 import PasswordHasher

def createPassword():
    ph = PasswordHasher()
    password = input("Enter password: ")
    return ph.hash(password)

def verifyPassword(hashed_pw, password):
    ph = PasswordHasher()
    verify = ph.verify(hash=hashed_pw, password=password)
    if verify is True:
        return True
    else:
        return False

def getAll(cursor) -> None:
    print(cursor.execute("SELECT * FROM user").fetchall())

def createAccount(username, password, cursor) -> bool:
    check_exist = "SELECT * FROM login WHERE (username=:username)" 
    cursor.execute(check_exist, {'username': username})
    result = cursor.fetchall()
    if len(result) == 0:
        command = """
        INSERT INTO login (username, hash)
        VALUES (:username, :password)"""
        cursor.execute(command, {'username': username, 'hash': password})
        return True 
    else:
        return False

def getUserData(username, cursor) -> bool:
    command = """
    SELECT 1 FROM user WHERE 
    (username=:username)
    LIMIT 1""" 
    cursor.execute(command, {'username': username})
    result = cursor.fetchone()
    if result is not None:
        #verify = verifyPassword(hashed_pw=hashed_pw, hash=result[2]) # 2 index should return password
        return result 
    else:
        print("Username not found! ")
        return None
    
def login(username, password, cursor) -> bool:
    
    get = getUserData(username, cursor) # get -> ([user_id, username, hash])
    
    if get is not None:
        hashed_pw = get[2] 
        verify = verifyPassword(hashed_pw, password)
        if verify is True: # if password is correct
            print(f"Welcome! {username}")
            return True
        else:
            print("Password incorrect")
            return False
    else:
        return False

def main() -> None:
    connection = sqlite3.connect('login.db')
    cursor = connection.cursor()
    while (True):
        print("""Choose a method:
              1. Login 
              2. Create an Account""")
        get = int(input("Number: "))
        
        if get == 1:
            username = input("Username: ")
            password = input("Password: ")
            result = login(username, password, cursor)
            if result is True:
                break 
            else:
                continue
            
        if get == 2:
            username = input("Username: ")
            password = input("Password: ")
            result = createAccount(username, password, cursor)
            if result is True:
                connection.commit()
                getAll(cursor)
                print("Account successfully created!")
                print(f"Welcome {username}")
                break 
            else:
                print("Error: Username already exists")
                continue

if __name__ == '__main__':
    main()
