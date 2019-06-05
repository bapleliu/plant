# -*- coding: gb2312 -*- 
from flask import Flask,render_template

app=Flask(__name__)

@app.route("/")
def index():
	return render_template("index.html", title="Plant Knowledge Graph")

@app.route("/tree.html")
def tree():
	return render_template("tree.html")

@app.route("/test.html")
def test():
	return render_template("test.html")

if __name__=="__main__":
	app.run(debug = True, host="0.0.0.0", port="8000") #可公开访问
	#app.run(debug = True, port="8000") #仅本机访问