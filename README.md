This application use the example of http://flask.pocoo.org/ .
	1. 创建应用的结构目录
	例：
	/flaskr
		/flaskr
			/static
			/templates
	这个应用将会作为python的package安装
	static文件夹中用来存储渲染胶本如CSS、javascript脚本
	temlates文件夹用来存储html格式的模板
	2. 创建数据库模式
	这一步用来创建数据库模式，在flaskr/flaskr文件夹下创建名为schema.sql的文件，并写入以下内容：
	  drop table if exists entries;
	  create table entries(
	           id integer primary key autoincrement,
	           title string not null,
	           text string not null
	   );
	这个模式包含一个单独的名为entries的表。包含整型（integer）自增长的主键id，和两个不能为null的字符串。
	3. 应用设置代码
	创建好数据模式schema后，可以创建应用模块了。在flaskr/flaskr文件夹下创建flaskr.py
	   import os
	   import sqlite3
	   from flask import Flask,request,session,g,redirect,url_for,abort,\
	           render_template,flash
	   app=Flask(__name__)
	   app.config.from_object(__name__)
	   app.config.update(dict(
	       DATABASE=os.path.join(app.root_path,'flaskr.db'),
	       SECRET_KEY='development key',
	      USERNAME='admin',
	      PASSWORD='defualt'
	  ))
	  app.config.from_envvar('FLASKR_SETTINGS',silent=True)
	  
	  def connect_db():
	      """Connects to the specific database."""
	      rv=sqlite3.connect(app.config['DATABASE'])
	      rv.row_factory=sqlite3.Row
	      return rv
	4. 作为软件包安装flaskr
	在flaskr/flaskr文件夹下创建__init__.py使flaskr/flaskr成为一个目录包，在flaskr/文件夹下创建setup.py和MANIFEST.in
	
	setup.py包含以下内容：
	setup(
	    name='flaskr',
	    packages=['flaskr'],
	    include_package_data=True,
	    install_requires=[
	        'flask',
	    ],
	)
	
	在MANIFEST.in中指定模板、静态文件以及数据模式的路径，写入以下内容：
	graft flaskr/templates
	graft flaskr/static
	include flaskr/schema.sql
	
	__init__.py为了定位应用在__init__.py中写入以下内容：
	from .flaskr import app
	
	之后便要安装应用了，在根目录flaskr/下执行
	pip install --editable .
	请确保在virtualenv环境下安装
	
	做完了这些，便可以启动应用了
	导入环境变量
	export FLASK_APP=flaskr
	export FLASK_DEBUG=true
	flask run#(启动应用)
	5. 连接数据库
	在flaskr.py中加入以下函数以连接数据库
	def get_db():
	    '''open a new database connection if there is none yet for the 
	    current application context.
	    '''
	    if not hasattr(g,'sqlite_db'):
	        g.sqlite_db=connect_db()
	    return g.sqlite_db
	
	@app.teardown_appcontext
	def close_db(error):
	    """closes the database again at the end of the request."""
	    if hasattr(g,'sqlite_db'):
	        g.sqlite_db.close()
	6. 创建数据库
	将创建好的数据模式schema.sql写入sqlite3命令行
	sqlite3 /tmp/flaskr.db < schema.sql
	
	在flaskr.py中加入初始化数据库函数：
	
	def init_db():
	    db=get_db()
	    with app.open_resource('schema.sql',mode='r') as f:
	        db.cursor().executescript(f.read())
	    db.commit()
	
	@app.cli.command('initdb')
	def initdb_command():
	    """Initializes the database."""
	    init_db()
	    print ('Initialized the database.')
	
	现在可以使用flask脚本创建数据库了
	flask initdb
	Initialized the database.
	7. 创建视图函数
	将视图函数写入应用flaskr.py中
	@app.route('/')
	def show_entries():
	    db=get_db()
	    cur=db.execute('select title,text from entries order by id desc')
	    entries=cur.fetchall()
	    return render_template('show_entries.html',entries=entries)
	
	
	
	@app.route('/add',methods=['POST'])
	def add_entry():
	    if not session.get('logged_in'):
	        abort(401)
	    db=get_db()
	    db.execute('insert into entries (title,text) values (?,?)',
	               [request.form['title'],request.form['text']])
	    db.commit()
	    flash('New entry was successfully posted')
	    return redirect(url_for('show_entries'))
	
	
	@app.route('/login',methods=['GET','POST'])
	def login():
	    error=None
	    if request.method=='POST':
	        if request.form['username']!=app.config['USERNAME']:
	            error='Invalid username'
	        elif request.form['password']!=app.config['PASSWORD']:
	            error='Invalid password'
	        else:
	            session['logged_in']=True
	            flash('You were logged in ')
	            return redirect(url_for('show_entries'))
	    return render_template('login.html',error=error)
	
	@app.route('/logout')
	def logout():
	    session.pop('logged_in',None)
	    flash('You were logged out')
	    return redirect(url_for('show_entries'))
	8. 创建模板
	在templates文件夹下建立模板文件
	layout.html 
	<!doctype html>
	<title>Flaskr</title>
	<link rel=stylesheet type=text/css href="{{ url_for('static',filename='style.css')}}">
	<div class=page>
	    <h1>Flaskr</h1>
	    <div class=metanav>
	    {% if not session.logged_in %}
	        <a href="{{ url_for('login') }}">log in </a>
	    {% else %}
	        <a href="{{ url_for('logout')}}">log out</a>
	    {% endif %}
	    </div>
	    {% for message in get_flashed_messages()%}
	        <div class=flash>{{message}}</div>
	    {% endfor %}
	    {% block body %}{% endblock %}
	</div>
	
	login.html 
	{% extends "layout.html" %}
	{% block body %}
	    <h2>Login</h2>
	    {% if error %}<p class=error><strong>Error:</strong>{{ error }}{% endif %}
	    <form action="{{ url_for('login') }}" method=post>
	            <dl>
	                    <dt>Username:
	                    <dd><input type=text name=username>
	                    <dt>Password:
	                    <dd><input type=password name=password>
	                    <dd><input type=submit value=Login>
	            </dl>
	    </form>
	{% endblock %}
	
	show_entries.html 
	{% extends "layout.html" %}
	{% block body %}
	    {% if session.logged_in %}
	        <form action="{{ url_for('add_entry') }}" method=post class=add-entry>
	                <dl>
	                        <dt>Title:
	                        <dd><input type=text size=30 name=title>
	                        <dt>text:
	                        <dd><textarea name=text rows=5 cols=40></textarea>
	                        <dd><input type=submit value=Share>
	                </dl>
	        </form>
	    {% endif %}
	    <ul class=entries>
	    {% for entry in entries %}
	        <li><h2>{{ entry.title }}</h2>{{ entry.text|safe}}
	    {% else %}
	        <li><em>Unbelievable. No entries here so far</em>
	    {% endfor %}
	    </ul>
	{% endblock %}
	9. 添加渲染风格
	在static/文件夹下创建style.css,写入以下内容
	style.css 
	body    {font-family: sans-serif;background:#eee;}
	a,h1,h2 {color:#377ba8;}
	h1,h2   {font-family:'Georgia',serif;margin:0;}
	h1      {border-bottom:2px solid #eee;}
	h2      {font-size: 1.2em;}
	
	.page   {margin: 2em auto;width:35em;border:5px solid #ccc;
	        padding: 0.8em;background:white;}
	.entries {list-style:none;margin:0;padding:0;}
	.entries li {margin:0.8em 1.2em;}
	.entries li h2 {margin-left:-1em;}
	.add-entry {font-size:0.9em;border-bottom:1px solid #ccc;}
	.add-entry dl {font-weight:bold;}
	.metanav {text-align:right;font-zise:0.8em;padding:0.3em;
	        margin-bottom:1em;background:#fafafa;}
	.flash  {background:#cee5F5;padding:0.5em;
	        border:1px solid #aacbe2;}
	.error {background:#f0d6d6;padding:0.5em;}
	
	10. 测试应用
	在flaskr/文件夹下创建测试文件夹tests并在tests中创建文件夹test_flaskr.py
	 
	运行测试 请确保安装了pytest
	pip install -e .
	pip install pytest
	命令运行在flaskr/文件夹下
	py.test
	
	结合setup进行测试（testing+setuptools）：
	修改setup.py
	setup.py 
	from setuptools import setup
	setup(
	    name='flaskr',
	    packages=['flaskr'],
	    include_package_data=True,
	    install_requires=[
	        'flask',
	    ],
	    setup_requires=[
	        'pytest-runner',
	    ],
	    tests_require=[
	        'pytest',
	    ],
	
	)
	
	创建setu.cfg，写入：
	[aliases]
	test=pytest
	现在你可以运行 python setup.py test进行测试了。
	

	
	
	
	
	
	
