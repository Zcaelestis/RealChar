from sqlalchemy import create_engine 
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv #
import os 

load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL") # 从环境变量中获取数据库的URL

connect_args = {"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith(
    "sqlite") else {} # 如果数据库的URL以sqlite开头,则设置connect_args为{"check_same_thread": False},否则为空字典

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args=connect_args
) # 创建数据库引擎使用SQLALCHEMY_DATABASE_URL和connect_args

SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine) # 创建SessionLocal类,用于创建数据库会话


def get_db(): # 定义get_db函数,用于获取数据库会话
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 如果直接运行这个文件,则执行下面的代码,用于测试数据库连接;
if __name__ == "__main__":
    print(SQLALCHEMY_DATABASE_URL) 
    from realtime_ai_character.models.user import User            # 从models.user中导入User类
    with SessionLocal() as session:                               # 创建数据库会话,并print数据库中的所有User
        print(session.query(User).all())                          # 通过session.query(User)获取User的查询对象,通过all()获取所有User   
        session.delete(User(name="Test", email="text@gmail.com")) # 通过session.delete()删除User
        session.commit()                                          # 提交会话

        print(session.query(User).all())                          # 再次print数据库中的所有User             
        session.query(User).filter(User.name == "Test").delete()  # 删除增加的user,commit
        session.commit()

        print(session.query(User).all())                          # 最后再次print数据库中的所有User  
