# import
from flask import Flask, render_template, redirect, request   #用来创建 Web 应用
from flask_scss import Scss   #用于自动将 .scss 文件编译为 .css，以方便在网页中使用
from flask_sqlalchemy import SQLAlchemy   #导入 Flask 的数据库扩展 SQLAlchemy，用于和数据库交互
from datetime import datetime

# my app
# 告诉 Flask 当前脚本是主程序。Flask 会根据这个值来定位模板文件、静态文件等路径
app = Flask(__name__)
Scss(app)

app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False
db = SQLAlchemy(app)

#data class ~ Row of data
class MyTask(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    content = db.Column(db.String(100), nullable = False)
    complete = db.Column(db.Integer, default = 0)
    created = db.Column(db.DateTime, default = datetime.utcnow)

    def __repr__(self) -> str:
        return f"Task {self.id}"
with app.app_context():
    db.create_all()

#URL 路由 "/"  →  对应函数 index()  →  返回响应内容 
# Routes to webpages
# home page
@app.route("/", methods = ['POST', 'GET'])   #注册一个URL路由（即访问网站的 / 路径）, post=send data, get=receive data
def index():    #是对应的处理函数
    # add a new task
    if request.method == 'POST':
        current_task = request.form['content']
        new_task = MyTask(content=current_task)
        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')  #返回到主页
        except Exception as e:
            print(f"ERROR:{e}")
            return(f"ERROR:{e}")
    #see all current tasks
    else:
        tasks = MyTask.query.order_by(MyTask.created).all()
        return render_template('index.html', tasks = tasks)

    return render_template('index.html')   #当浏览器访问 http://localhost:5000/，就会触发这个函数

# delete an item
@app.route("/delete/<int:id>")
def delete(id: int):
    delete_task = MyTask.query.get_or_404(id)
    try:
        db.session.delete(delete_task)
        db.session.commit()
        return redirect("/")
    except Exception as e:
        return f"ERROR:{e}"
# edit an item
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id:int):
    task = MyTask.query.get_or_404(id)
    if request.method == 'POST':
        task.content = request.form['content']
        try:
            db.session.commit()
            return redirect("/")
        except Exception as e:
            return f"ERROR:{e}"
    else:
        return render_template('edit.html', task=task)





# check current tasks










#当这个脚本被直接运行时，启动 Flask 内置开发服务器
if __name__ == "__main__":
    app.run(debug=True)
