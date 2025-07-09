# import
from flask import Flask, render_template, redirect, request   
# Flask 用来创建 Web 应用
# render_template： 用于将 HTML templates 渲染为网页，可以动态插入数据
# redirect：用户重定向到另一个页面
# request：用于获取 HTTP 请求相关的数据

from flask_scss import Scss   #用于自动将 .scss 文件编译为 .css，以方便在网页中使用
from flask_sqlalchemy import SQLAlchemy   #导入 Flask 的数据库扩展 SQLAlchemy，用于和数据库交互
from datetime import datetime

# my app
# 告诉 Flask 当前脚本是主程序。Flask 会根据这个值来定位模板文件、静态文件等路径
app = Flask(__name__)  #是任何 Flask 应用的起点，相当于“创建网站”
Scss(app)  # 将flask_scss 的Scss功能绑定到Flask应用，自动监听.scss 文件并编译为 .css 文件供浏览器使用。

app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False
db = SQLAlchemy(app)  #初始化数据库对象 db，并与当前的 Flask 应用绑定

# data class ~ Row of data
class MyTask(db.Model): #这是一个 SQLAlchemy 的“模型类”， 继承至db.Model
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(100), nullable=False)
    complete = db.Column(db.String(10), default="No")  # 用字符串表示是否完成，如 "0" 或 "1"
    duedate = db.Column(db.Date, nullable=True)

    def __repr__(self) -> str:
        return f"Task {self.id}"
with app.app_context():
    db.create_all()  #把 MyTask 类创建为一张真正的数据库表

#URL 路由 "/"  →  对应函数 index()  →  返回响应内容 
# Routes to webpages
# home page
@app.route("/", methods = ['POST', 'GET'])   #注册一个URL路由（即访问网站的 / 路径）, post=send data, get=receive data
def index():    #是对应的处理函数
    # add a new task
    if request.method == 'POST':
        content = request.form['content']
        complete = request.form['complete']
        duedate_str = request.form['duedate']
        duedate = datetime.strptime(duedate_str, "%Y-%m-%d").date()
        new_task = MyTask(content=content, complete=complete, duedate=duedate)

        try:
            db.session.add(new_task) # 向数据库会话中添加新任务并提交事务，
            db.session.commit()  #保存到数据库
            return redirect('/')  #返回到主页
        except Exception as e:
            print(f"ERROR:{e}")
            return(f"ERROR:{e}")
    #see all current tasks
    else:
        tasks = MyTask.query.order_by(MyTask.id).all()
        # 如果是 GET 请求（用户正常访问页面而非提交表单），就从数据库中读取所有任务
        return render_template('index.html', tasks = tasks)

    return render_template('index.html')   #当浏览器访问 http://localhost:5000/，就会触发这个函数

# delete an item
@app.route("/delete/<int:id>")  #将函数绑定到 /delete/<id> 这个 URL
def delete(id: int):
    delete_task = MyTask.query.get_or_404(id)
    try:
        db.session.delete(delete_task)  #数据库中标记这个对象为“将被删除”
        db.session.commit()  #真正执行SQL删除操作
        return redirect("/")
    except Exception as e:
        return f"ERROR:{e}"
# edit an item
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id:int):
    task = MyTask.query.get_or_404(id)
    if request.method == 'POST':
        task.content = request.form['content']
        task.complete = request.form['complete']
        duedate_str = request.form['duedate']
        task.duedate = datetime.strptime(duedate_str, "%Y-%m-%d").date()
        
        try:
            db.session.commit()
            return redirect("/")
        except Exception as e:
            print(f"ERROR:{e}")
            return "Error"
    else:
        return render_template('edit.html', task=task)

#当这个脚本被直接运行时，启动 Flask 内置开发服务器
if __name__ == "__main__":
    app.run(debug=True)
