# -*- coding: utf-8 -*-

from py2neo import Graph
import json
import re
import random


class Neo4jToJson(object):
    #接受表单查询，返回Json格式查询结果#

    def __init__(self):
        #初始化数据#
        # 与neo4j服务器建立连接
        self.graph = Graph()
        self.links = []
        self.nodes = []

    def post(self,select_name):
        
        # select_name是前端传过来的查询名称

        # 取出所有节点数据
        nodes_data_all = self.graph.run("MATCH (n:species) RETURN n").data()
        # node名存储
        nodes_list = []
        for node in nodes_data_all:
            nodes_list.append(node['n']['中文名'])
        
        # 根据前端的数据，判断搜索的关键字是否在nodes_list中存在，如果存在返回相应数据，否则返回随机数据
        if select_name in nodes_list:
            # 获取Neo4j中相关节点数据
            nodes_data = self.graph.run("MATCH (n)--(b) where n.中文名 ='" + select_name + "' return n,b").data()
            links_data = self.graph.run("MATCH (n)-[r]-(b) where n.中文名 ='" + select_name + "' return r").data()

        else:
            # 获取Neo4j中随机某个节点数据
            random_index=random.randint(0, len(nodes_list)-1)
            select_name=nodes_list[random_index]
            print(select_name)
            links_data = self.graph.run("MATCH (n)-[r]-(b) where n.中文名 ='" + select_name + "' return r").data()
            nodes_data = self.graph.run("MATCH (n)--(b) where n.中文名 ='" + select_name + "' return n,b").data()
        
        #整理节点数据
        self.get_select_nodes(nodes_data)

        #整理关系数据
        self.get_links(links_data)

        #关系数据中source、target的值转换为nodes中对应序号index
        self.convert_index(self.links,self.nodes)

        # 数据格式转换
        neo4j_data = {'links': self.links, 'nodes': self.nodes}
        neo4j_data_json = json.dumps(neo4j_data, ensure_ascii=False).replace(u'\xa0', u'')
        
        # 数据存入json文件        
        with open("static/data/result.json","w") as f:
            json.dump(neo4j_data,f)

    def get_links(self, links_data):
        #关系数据整理#
        links_data_str = str(links_data)
        links = []
        i = 1
        dict = {}
        # 正则匹配
        links_str = re.sub("[\!\%\[\]\,\。\{\}\-\:\'\(\)\>]", " ", links_data_str).split(' ')
        for link in links_str:
            if len(link) > 1:
                if i == 1:
                    dict['source'] = link 
                elif i == 2:
                    dict['rel'] = link
                elif i == 3:
                    dict['target'] = link
                    self.links.append(dict)
                    dict = {}
                    i = 0
                i += 1
        return self.links

    def get_select_nodes(self, nodes_data):
        #节点数据整理#
        dict_node = {}
        for node in nodes_data:
            name = node['n']['中文名']   #cypher查询语句中的n节点
            index = "_"+str(node['n'].identity)   #node['n']是py2neo的Node对象，用node.identity可返回其id值,并在前面加上下划线
            label = list(node['n'].labels)[0] #node.labels返回Node对象的所有标签，list()[0]返回其中第一个标签
            properties = dict(node['n']) #dict(node)返回Node对象的所有属性
            dict_node["id"] = index
            dict_node["name"]=name
            dict_node["label"]=label
            dict_node["properties"]=properties
            self.nodes.append(dict_node)
            dict_node = {}
            break
        for node in nodes_data:
            name = node['b']['中文名']   #cypher查询语句中的b节点
            index = "_"+str(node['b'].identity)   
            label = list(node['b'].labels)[0] 
            properties = dict(node['b']) 
            dict_node["id"] = index
            dict_node["name"]=name
            dict_node["label"]=label
            dict_node["properties"]=properties
            self.nodes.append(dict_node)
            dict_node = {}

    def convert_index(self,links,nodes):
        #将self.links中source和target的值（即node的id值）转换为nodes中对应node的index，使数据能用于d3.js力导向图#
        id_to_index={}  #存储键值对，键为id(n["id"])，值为index(i)
        i=0
        for n in nodes:
            id_to_index[n["id"]]=i
            i+=1
        for link in links:
            link["source"]=id_to_index[link["source"]]
            link["target"]=id_to_index[link["target"]]
        self.links=links
        return self.links


