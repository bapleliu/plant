# -*- coding: gb2312 -*- 
from flask import Flask,render_template

app=Flask(__name__)

@app.route("/")
def index():
	return render_template("index.html", title="Plant Knowledge Graph")

if __name__=="__main__":
	app.run(debug = True, host="0.0.0.0", port="8000") #�ɹ�������
	#app.run(debug = True, port="8000") #����������