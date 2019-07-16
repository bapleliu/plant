# -*- coding:utf-8 -*- 
from flask import Flask,render_template,request,redirect
from cypher import Neo4jToJson


from flask_wtf import FlaskForm                        #引入FlaskForm类，作为自定义Form类的基类
from wtforms import StringField,SubmitField           #StringField对应HTML中type="text"的<input>元素，SubmitField对应type='submit'的<input>元素
from wtforms.validators import Required                #引入验证函数

app = Flask(__name__)
app.config['SECRET_KEY'] = 'plant_knowledge_graphV1.0'  

class NameForm(FlaskForm):
	name = StringField('输入查询物种名称：',validators=[Required()])
	submit = SubmitField('查询')

@app.route("/")
def index():
	return render_template("index.html", title="Plant Knowledge Graph")

@app.route("/tree.html")
def tree():
	return render_template("tree.html", title="Vegetation Classification")

@app.route("/search.html", methods = ['GET', 'POST'])
def search():
	name=None
	form = NameForm()
	data_neo4j = Neo4jToJson()
	if form.validate_on_submit():        
		name = form.name.data
		data_neo4j.post(name)
		return render_template("search.html",name=name,form=form)
	return render_template("search.html",name=name,form=form)



if __name__=="__main__":
	app.run(debug = True, host="0.0.0.0", port="8000") #可外部访问
	#app.run(debug = True, port="8000") #仅本机访问


