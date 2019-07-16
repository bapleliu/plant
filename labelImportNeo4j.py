# -*- coding:utf-8 -*- 
import os
import re
from py2neo import Node,Relationship,Graph

class FileToNeo4j():
    #初始化，与neo4j服务器建立连接
    def __init__(self):
        self.graph_plants = Graph()
    
    #提取每行文字标记信息的函数，返回[(tag,text),(tag,text)]的list
    def extract(self,string):
        #提取标记属性和相应的值
        labels=re.findall(r'<([a-z]*?)>(.*?)</[a-z]*?>',string)
        #对属性、值、单位、组合进行修改
        test=list(labels) #后续要对列表labels进行修改，复制成test用for语句进行遍历
        step=0
        for i in range(0,len(test)): #将属性、值、单位组合成属性、值
            if test[i][0]=="danwei":
                labels[i-1-step]=("zhi",labels[i-1-step][1]+labels[i-step][1])
                del labels[i-step]
                step+=1
                
        trait=re.compile(r"^(长|宽|高|([直|胸]?径)|粗|厚)((达|约|近|仅|(不及)|(不足)|(可达))?[0-9-\.]*[厘|毫]?米)")
        
        test=list(labels) #labels已经过修改，将labels再备份一次
        step=0
        for i in range(0,len(test)): #将组合拆成属性、值
            if test[i][0]=="zuhe":
                traits=re.findall(trait,test[i][1])
                labels[i+step]=("sx",traits[0][0])
                labels.insert(i+1+step,("zhi",traits[0][2]))
                step+=1
        
        test=list(labels) 
        step=0
        for i in range(0,len(test)):
            if test[i][0]=="sx" and test[i+1][0]=="sx": #一句话描述多重属性的情况
                labels.insert(i+1+step,("zhi",test[i+2+step][1]))
                step+=1
                
        #增加描述项，修改双重tag
        tag=re.compile(r'<[a-z/]*?>' )
        if labels!=[]:
            if labels[0][0]=="qiguan": #如果是器官的描述行
                #删除所有注释，作为description
                d=tag.sub('',string) 
                #将description加入fields中
                labels.append(('description',d))
            if tag.findall(labels[0][1]): #如果有双重tag,fields[0][1]中会有<tag>text</tag>的形式
                newfield=re.findall(r'<([a-z]*?)>(.*)',labels[0][1])
                labels.append(newfield[0])
                labels[0]=(labels[0][0],tag.sub('',labels[0][1]))       
        return labels
    
    #将文件中提取出的fields按species和subspecies分割
    def cutfiles(self,file):
        f = open(file,"r", encoding='UTF-8') 
        #将所有tag及text提取并存入列表allfields中
        allfields=[]
        for line in f:
            fields=self.extract(line)
            if fields!=[]:
                allfields.append(fields)
        #将allfields按species和subspecies分割
        nums=[] #用来储存subsepecies的序号
        subspecies_fields=[]
        for i in range(0,len(allfields)):
            if allfields[i][0][0]=="subspecies":
                nums.append(i)
        if nums!=[]:
            species_fields=allfields[0:nums[0]]
            subspecies_fields.append(allfields[nums[-1]:len(allfields)])
            if len(nums)>1:
                for i in range(0,len(nums)-1):
                    subspecies_fields.append(allfields[nums[i]:nums[i+1]])
        else:
            species_fields=allfields
        
        
        return species_fields,subspecies_fields
    
    #为物种节点添加属性和子节点 node对应于species_node或者subspecies_node fields对应于species_fields或者subspecies_fields[i]
    def add_species_nodes(self,node,fields):         
        for s in range(0,len(fields)):
            #物种节点添加属性和从属的器官节点
            if fields[s][0][0]=="species": 
                #添加中文名属性
                node["中文名"]=fields[s][0][1]
                #如果有异名tag，添加异名属性
                if len(fields[s])>1 and fields[s][1][0]=="yiming":
                    synonyms=[]
                    for i in range(1,len(fields[s])):
                        synonyms.append(fields[s][i][1])
                        node["异名"]=synonyms
            if fields[s][0][0]=="lifeform": #有生活型tag的行
                #添加生活型属性
                node["生活型"]=fields[s][0][1]
                #如果有性状tag，添加性状属性
                if len(fields[s])>1:
                    for i in range(1,len(fields[s])):
                        if fields[s][i][0]=="sx":
                            node[fields[s][i][1]]=fields[s][i+1][1]
            if fields[s][0][0]=="sj": 
                node["生境"]=fields[s][0][1]
            if fields[s][0][0]=="fenbu": 
                node["国内分布"]=fields[s][0][1]
            if fields[s][0][0]=="guowaifenbu": 
                node["国外分布"]=fields[s][0][1]
            if re.match(r"[hg]u[ao]qi",fields[s][0][0])!=None:#有花期/果期tag的行
                for i in range(0,len(fields[s])): 
                    if fields[s][i][0]=="guoqi": 
                        node["果期"]=fields[s][i][1]
                    if fields[s][i][0]=="huaqi": 
                        node["花期"]=fields[s][i][1]
            if fields[s][0][0]=="qiguan":#有器官tag的行，创建器官节点
                n=len(fields[s])
                organ_node = Node("organ",中文名 = fields[s][0][1],原文 = fields[s][n-1][1])
                r=Relationship(organ_node, "part_of", node)
                for i in range(1,len(fields[s])):
                    if fields[s][i][0]=="sx":
                        organ_node[fields[s][i][1]]=fields[s][i+1][1]
                self.graph_plants.create(organ_node|r|node)
                for i in range(1,len(fields[s])):
                    if fields[s][i][0]=="器官":
                        organ_node2 = Node("organ",中文名 = fields[s][i][1],原文 = fields[s][n-1][1])
                        r2=Relationship(organ_node2, "part_of", node)
                        self.graph_plants.create(organ_node2|r2|node)
        self.graph_plants.push(node) #更新节点
    
    #为亚种节点添加属性和子节点
    def add_subspecies_nodes(self,node,fields):         
        for s in range(0,len(fields)):
            #亚种节点添加属性和从属的器官节点
            if fields[s][0][0]=="subspecies": 
                #创建亚种节点
                subspecies_node=Node("subspecies",中文名 = fields[s][0][1])
                #添加异名和拉丁名属性
                synonyms=[]
                for i in range(1,len(fields[s])):
                    if fields[s][i][0]=="yiming":
                        synonyms.append(fields[s][i][1])
                    if fields[s][i][0]=="latin":
                        latinname=node["拉丁学名"]+" "+fields[s][i][1]
                if synonyms!=[]:
                    subspecies_node["异名"]=synonyms
                subspecies_node["拉丁学名"]=latinname
                
            if fields[s][0][0]=="lifeform": #有生活型tag的行
                #添加生活型属性
                subspecies_node["生活型"]=fields[s][0][1]
                #如果有性状tag，添加性状属性
                if len(fields[s])>1:
                    for i in range(1,len(fields[s])):
                        if fields[s][i][0]=="sx":
                            subspecies_node[fields[s][i][1]]=fields[s][i+1][1]
            if fields[s][0][0]=="sj": 
                subspecies_node["生境"]=fields[s][0][1]
            if fields[s][0][0]=="fenbu": 
                subspecies_node["国内分布"]=fields[s][0][1]
            if fields[s][0][0]=="guowaifenbu": 
                subspecies_node["国外分布"]=fields[s][0][1]
            if re.match(r"[hg]u[ao]qi",fields[s][0][0])!=None:#有花期/果期tag的行
                for i in range(0,len(fields[s])): 
                    if fields[s][i][0]=="guoqi": 
                        subspecies_node["果期"]=fields[s][i][1]
                    if fields[s][i][0]=="huaqi": 
                        subspecies_node["花期"]=fields[s][i][1]
            if fields[s][0][0]=="qiguan":#有器官tag的行，创建器官节点
                n=len(fields[s])
                organ_node = Node("organ",中文名 = fields[s][0][1],原文 = fields[s][n-1][1])
                r=Relationship(organ_node, "part_of", subspecies_node)
                for i in range(1,len(fields[s])):
                    if fields[s][i][0]=="sx":
                        organ_node[fields[s][i][1]]=fields[s][i+1][1]
                self.graph_plants.create(organ_node|r|subspecies_node)
                for i in range(1,len(fields[s])): #一句话描述两种器官的情况
                    if fields[s][i][0]=="器官":
                        organ_node2 = Node("organ",中文名 = fields[s][i][1],原文 = fields[s][n-1][1])
                        r2=Relationship(organ_node2, "part_of", subspecies_node)
                        self.graph_plants.create(organ_node2|r2|subspecies_node)
        self.graph_plants.push(subspecies_node) #更新节点
        r=Relationship(subspecies_node, "belong_to", node) #建立亚种-[从属于]->物种的关系
        self.graph_plants.create(r)
    	
    #将文件信息导入Neo4j，创建物种节点及相关属性、子节点
    def importFile(self,file):
        #从文件路径获取文件名
        filename=os.path.split(file)[1]
        #从文件名获取物种拉丁名
        latinname= os.path.splitext(filename)[0].replace("%20"," ")
        #创建物种节点，添加拉丁名属性
        species_node = Node("species",拉丁学名 = latinname)
        species_fields=self.cutfiles(file)[0]
        subspecies_fields=self.cutfiles(file)[1]
        
        self.add_species_nodes(species_node,species_fields)
        
        if len(subspecies_fields)>0:
            for fields in subspecies_fields:
                self.add_subspecies_nodes(species_node,fields)
    
    #遍历文件夹，将每个文件信息导入Neo4j
    def importDir(self,directory):
        filelists=os.listdir(directory)
        for file in filelists:
            fileFullName=os.path.join(directory,file)
            self.importFile(fileFullName)

