## CreateGraph.py
## DSE-203, ETL
# ****************************************************************************************************************************#
# Ver       Developer       Date           Description
# -----------------------------------------------------------------------------------------------------------------------------
# 1.0      Team            11/22/2019      Base version file to process scrapped data and convert into graph
# ****************************************************************************************************************************#

import pandas as pd
import csv
from py2neo import Graph, Node, Relationship
import re

# Database Credentials
uri = "bolt://localhost:7687"
userName = "neo4j"
password = "h6u4%kr"

# Create graph instance
graph = Graph(uri, auth=(userName, password))



# Query string to create base nodes
queryCreateNodes = """MERGE (nodeLbl:{nodeLabel} {{name: "{node}"}})"""

# Create all nodes, skip creation if already present
NODE_LABELS=['ORG','PERSON','PRODUCT', 'NAICS']
def createNodes():
        with open('./Input/NodeLabels.tsv',encoding="utf8") as tsvfile:
            reader = csv.reader(tsvfile, delimiter='\t')
            next(reader, None)  # skip the headers
            for row in reader:
                row[0] = str(row[0]).replace("\"", "").strip()
                row[0] = row[0].replace("\\", "").strip().upper()
                # if(row[1] == ""):
                #     row[1] = 'NoLabel'
                if row[1] in NODE_LABELS:
                    print("Creating node:", row[0], row[1])
                    graph.run(queryCreateNodes.format(node=row[0], nodeLabel=row[1]))
                    print("Nodes created successfully!")



# Query string to update properties for base nodes
queryUpdateProperty = """MATCH (n) WHERE n.name =~ "(?i){nodeName}"
                        WITH n
                        set n.{propKey} = "{propValue}"
                        """

# Set properties for all nodes
def updateNodeProperties():
    with open('./Input/NodeProperty.tsv',encoding="utf8") as tsvfile:
        reader = csv.reader(tsvfile, delimiter='\t')
        next(reader, None)  # skip the headers
        for row in reader:
            nodeName = str(row[0]).upper()
            propKey = str(row[1]).replace(" ", "").strip()
            propValue = str(row[2])

            if (nodeName is not None and len(nodeName.strip()) > 0 and propKey is not None and len(
                    propKey.strip()) > 0):
                if(propKey.upper() == "FOUNDED" or propKey.upper() == "LAUNCHED"):
                    x = re.findall("[1-2][0-9][0-9][0-9]", str(propValue))
                    if(len(x) > 0):
                        propKeyYYYY = propKey + "Year"
                        propValueYYYY = x[0]
                        graph.run(queryUpdateProperty.format(nodeName=nodeName, propKey=propKeyYYYY, propValue=propValueYYYY))
                print("Updating node property:", nodeName, propKey, propValue)
                graph.run(queryUpdateProperty.format( nodeName=nodeName, propKey=propKey, propValue=propValue))

    print("Node property update Done!")


# Update relationships Query
queryUpdateRelation = """MATCH (a),(b) WHERE a.name =~ "(?i){startNode}" AND b.name =~ "(?i){endNode}"
                        MERGE (a)-[r:{edgeLabel}]->(b)
                        set r.EdgeID={edgeID}
                        """
# Set relationships with edge IDS
EDGEID_ACQUIRED=[]

def convert_monetary(edgePropKey,edgePropValue):
    if 'Value' in edgePropKey:
        sam = re.sub(r"\s+", "", edgePropValue)
        sam = re.sub(r"US","",sam)
        sam = re.sub(r"\$","",sam)
        number = re.findall('\d*\.?\d+',sam)
        if len(number)>0:
            if "m" in sam.lower() or 'million' in sam.lower():
                number_ = float(number[0])*10**6
            elif "b" in sam.lower() or 'billion' in sam.lower():
                number_ = float(number[0])*10**9
            elif "k" in sam.lower():
                number_ = float(number[0])*10**3
            else:
                number_ = float(number[0])
        else:
            number_ = ""
        return number_
    else:
        return edgePropValue

def updateRelations():
    with open('./Input/Connectivity.tsv',encoding="utf8") as tsvfile:
        reader = csv.reader(tsvfile, delimiter='\t')
        next(reader, None)  # skip the headers
        for row in reader:
            if(len(row) > 0):
                edgeID =  str(int(float(row[0])))
                startNode = str(row[1]).strip().upper()
                endNode = str(row[2]).strip().upper()
                edgeLabel = str(row[3]).replace(" ", "").strip()

                #Handle empty lines
                if((edgeID is not  None and len(edgeID.strip()) > 0) and (startNode is not  None and len(startNode.strip()) > 0)
                    and (endNode is not  None and len(endNode.strip())) and (edgeLabel is not  None and len(edgeLabel.strip()) > 0 )):
                    if (edgeLabel == 'acquired'):
                        EDGEID_ACQUIRED.append(edgeID)
                    print("Processing Relation:", edgeID, startNode, endNode, edgeLabel)
                    graph.run(queryUpdateRelation.format(startNode=startNode, endNode=endNode, edgeLabel=edgeLabel, edgeID=edgeID))

    print("Relation update Done!")


# Update edge property Query
queryUpdateEdgeProperty = """MATCH (a)-[r]-(b) where r.EdgeID={edgeID}
                            set r.{edgePropKey} = "{edgePropValue}"
                            """
# Update Edge Properties
def updateEdges():
    with open('./Input/EdgeProperty.tsv',encoding="utf8") as tsvfile:
        reader = csv.reader(tsvfile, delimiter='\t')
        next(reader, None)  # skip the headers
        for row in reader:
            edgeID =  str(int(float(row[0])))
            edgePropKey = str(row[1]).replace(" ", "").strip()
            edgePropValue = str(row[2])
            edgePropValue = convert_monetary(edgePropKey,edgePropValue)

            #Handle empty lines
            if (edgeID is not None and len(edgeID.strip()) > 0 and edgePropKey is not None and len(edgePropKey.strip()) > 0 ):
                # Get the year only
                if(edgeID in EDGEID_ACQUIRED and  edgePropKey=='Date'):
                    edgePropValue = edgePropValue[-4:]
                    print("Acquire date:", edgePropValue)

                print("Processing Edges:", edgeID, edgePropKey, edgePropValue)
                graph.run(queryUpdateEdgeProperty.format(edgeID=edgeID, edgePropKey=edgePropKey, edgePropValue=edgePropValue))

    print("Edge property update Done!")


# Delete Orphan Nodes
def deleteOrphanNodes():
    graph.run("MATCH (n) WHERE NOT (n)--() DELETE n")
    print("Deleting orphan nodes Done!")

# GENERATE THE GRAPH
print("*********** Call create node ***********")
createNodes()

print("*********** Call update node properties ***********")
updateNodeProperties()

print("*********** Call update relations ***********")
updateRelations()

print("*********** Call update edge properties ***********")
updateEdges()

print("*********** Call delete orphan nodes ***********")
deleteOrphanNodes()

print("Graph Execution Done!")
