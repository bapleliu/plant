## Plant Knowledge Graph ##
---
This project aims to create a plant Knowledge Graph with Neo4j.

I'm a begginner of programming, hope to learn more coding skills while working with the project.


* 2019-4-23
Try to build a web app based on flask.
Follow the [Flask tutorial](http://www.pythondoc.com/flask-mega-tutorial/helloworld.html#id2), now I have built a "Hello world" page.
Then try to use [cytoscape.js with Neo4j](https://blog.csdn.net/zhongzhu2002/article/details/45843283) to show the graph on browser.

* 2019-4-24
Found that cytoscape.js is not a good choice.
Most of the Data Visualization projects with Neo4j were based on d3.js.
This is an [example](https://blog.csdn.net/weixin_30342639/article/details/86756977), but it's in Java.
[Neo4jd3](https://github.com/eisman/neo4jd3) is also an excellent example,  but it's in Ruby.
Maybe I need to learn d3.js from scratch, and then try to connect it with flask.
Let's follow this [tutorial](http://benalexkeen.com/creating-graphs-using-flask-and-d3/) first.

* 2019-4-25
ModuleNotFoundError: No module named "flask.ext"
Solution: "flask.ext.wtf"-->"flask_wtf"

Fllowing the [Flask tutorial](http://www.pythondoc.com/flask-mega-tutorial/helloworld.html#id2), I've built a Login page.
Next tutorial is the book "Data Visualization with Python and Javascript"

* 2019-5-31
Learned d3.js and built the index.html file.
Organized folders and files as below:
plant
��  config.py
��  server.py
����static
��  ����css
��  ����data
��  ����js
����templates
(use DOS command "tree /f>1.txt" to get the tree structure)