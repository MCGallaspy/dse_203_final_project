## Json2Graph.py
## DSE-203, ETL
# ****************************************************************************************************************************#
# Ver       Developer       Date           Description
# -----------------------------------------------------------------------------------------------------------------------------
# 1.0      Team            11/17/2019      Base version file to process JSON data and convert into graph
# ****************************************************************************************************************************#

import pandas as pd
import json
from py2neo import Graph, Node, Relationship

# Database Credentials
uri = "bolt://localhost:7687"
userName = "neo4j"
password = "h6u4%kr"

# Create graph instance
graph = Graph(uri, auth=(userName, password))


# Read JSON file which is output of scrapping
def read_JSON():
    with open('WikiScraped_LNKD.json', 'r') as myfile:
        data = myfile.read()
    return data


# Create all nodes, skip creation if already present
def createBaseNodes(jsonRootKeys):
    for keyCompany in jsonRootKeys:
        graph.run(queryCreateBaseNodes, companyName=keyCompany)


# Set properties for all base nodes
def updateNodeProperties(jsonRootKeys, json_data):
    for keyCompany in jsonRootKeys:
        val = json_data.get(keyCompany)
        prop_rel_keys = val.keys()
        for key_prop in prop_rel_keys:
            if (key_prop in properties.tolist()):
                # print("Properties found:")
                value = val.get(key_prop)
                # print("key=", key_prop, " Value:", value)
                key_prop = str(key_prop).replace(" ", "").strip()
                key_prop = key_prop.replace("(", "")
                key_prop = key_prop.replace(")", "")
                graph.run(queryUpdateProperty.format(companyName=keyCompany, key=key_prop, value=value))
            # else:
            #     print("Properties NOT found:", key_prop)


# # Check for the edge properties START
def getEdgeProperties(edgePropertiesRaw):
    # print("Getting Edge properties...")
    edgeProperties = ""
    if isinstance(edgePropertiesRaw, dict):
        propKeys = edgePropertiesRaw.keys()
        nProps = len(propKeys)
        x = 0
        edgeProperties = "{"
        for propKey in propKeys:
            edgeProperties = edgeProperties + str(propKey) + ":'" + str(edgePropertiesRaw.get(propKey)) + "'"
            x += 1
            if (x < nProps):
                edgeProperties = edgeProperties + ","
        edgeProperties = edgeProperties + "}"
    # print("edgeProperties::", edgeProperties)

    return edgeProperties


# # Check for the edge properties END

# Set relationships with edge properties among nodes
def updateRelations(jsonRootKeys, json_data):
    relationKeys = relations["RelationKey"]
    for keyCompany in jsonRootKeys:
        val = json_data.get(keyCompany)
        prop_rel_keys = val.keys()
        for key_rel in prop_rel_keys:
            # if(key_rel.lower() in [x.lower() for x in relationKeys.tolist()]):
            if (key_rel in relationKeys.tolist()):
                df_rel = relations[relations["RelationKey"] == key_rel]
                edgeName = df_rel["EdgeName"]
                NodeClass = df_rel["NodeClass"]
                edgeProperties = df_rel["EdgeProperties"]
                edgeType = df_rel["EdgeType"]
                # print("************ REL*********")
                # print("edgeName=", edgeName, "edgeProperties=", edgeProperties, "edgeType=", edgeType)
                value = val.get(key_rel)
                ## TODO: Properly handle
                newNode = value
                edgeName = str(edgeName.values[0]).replace(" ", "").strip()
                NodeClass = str(NodeClass.values[0]).replace(" ", "").strip()

                # print(keyCompany, newNode, NodeClass, newNode, edgeName, edgeProperties)
                if (str(edgeType.values[0]).lower() == "incoming"):
                    if isinstance(value, dict):
                        # print("Set properties for edges")
                        childKeys = value.keys()
                        for childKey in childKeys:
                            newNode = childKey
                            edgeProperties = getEdgeProperties(value.get(childKey))
                            graph.run(
                                queryUpdateEdgePropertyIncoming.format(companyName=keyCompany, newNodeName=newNode,
                                                                       NodeClass=NodeClass,
                                                                       edgeName=edgeName, edgeProperties=edgeProperties,
                                                                       edgeType=edgeType))
                    else:
                        graph.run(
                            queryUpdateRelationIncoming.format(companyName=keyCompany, newNodeName=newNode,
                                                               NodeClass=NodeClass,
                                                               edgeName=edgeName, edgeProperties="", edgeType=edgeType))
                elif (str(edgeType.values[0]).lower() == "outgoing"):
                    if isinstance(value, dict):
                        childKeys = value.keys()
                        for childKey in childKeys:
                            newNode = childKey
                            edgeProperties = getEdgeProperties(value.get(childKey))
                            graph.run(
                                queryUpdateEdgePropertyOutgoing.format(companyName=keyCompany, newNodeName=newNode,
                                                                       NodeClass=NodeClass,
                                                                       edgeName=edgeName, edgeProperties=edgeProperties,
                                                                       edgeType=edgeType))
                    else:
                        # print("Outgoing:", str(edgeType))
                        graph.run(
                            queryUpdateRelationOutgoing.format(companyName=keyCompany, newNodeName=newNode,
                                                               NodeClass=NodeClass,
                                                               edgeName=edgeName, edgeProperties="", edgeType=edgeType))
            #     else:
            #         print("NOT incoming/outgoing:", str(edgeType))
            # else:
            #     print("Relation NOT found:", key_rel)


# Read the xlsx file which holds metadata info for input JSON file
# Sample data in the file is as below
# Columns: PropertiesKey	    RelationKey	    NodeClass	EdgeName	    EdgeProperties	EdgeType
# Value:  Founded	        NAICS	    NAICS	    NAICS Code		                incoming

df = pd.read_excel('JSONMetaData.xlsx')
properties = df["PropertiesKey"]
properties = properties.dropna(how='all')
relations = df.loc[:, df.columns != 'PropertiesKey']
relations = relations.dropna(how='all')

# companies = json_data.keys()
# print("Companies:", companies)

# Query string to create base nodes (for companies as JSON key)
queryCreateBaseNodes = """MERGE (company:Company {name: {companyName}})"""

# Query string to update properties for base nodes
queryUpdateProperty = """MATCH (company:Company {{name: "{companyName}"}})
    WITH company
    SET company.{key} = "{value}"
"""

# Incoming: Query string to update incoming relation to base nodes, create new nodes and establish new relations
queryUpdateRelationIncoming = """MATCH (company:Company {{name: "{companyName}"}})
    WITH company
    MERGE(node:{NodeClass}{{name: "{newNodeName}"}}) MERGE(company) <- [:{edgeName}]-(node)
"""

# Outgoing: Update edge properties with relationships
queryUpdateRelationOutgoing = """MATCH (company:Company {{name: "{companyName}"}})
    WITH company
    MERGE(node:{NodeClass}{{name: "{newNodeName}"}}) MERGE(company) - [:{edgeName}]->(node)
"""

# Incoming: Update edge properties with relationships
queryUpdateEdgePropertyOutgoing = """MATCH (company:Company {{name: "{companyName}"}})
    WITH company
    MERGE(node:{NodeClass}{{name: "{newNodeName}"}}) MERGE(company) <- [:{edgeName} {edgeProperties}]-(node)
"""

# Outgoing: Update edge properties with relationships
queryUpdateEdgePropertyIncoming = """MATCH (company:Company {{name: "{companyName}"}})
    WITH company
    MERGE(node:{NodeClass}{{name: "{newNodeName}"}}) MERGE(company) - [:{edgeName} {edgeProperties}]->(node)
"""


# Read and process data
data = read_JSON()
json_data = json.loads(data)
jsonRootKeys = json_data.keys()

# ********************************* CREATE THE GRAPH *********************************
# Create base nodes
createBaseNodes(jsonRootKeys)
# Update node properties
updateNodeProperties(jsonRootKeys, json_data)
# Update relationships and edge properties
updateRelations(jsonRootKeys, json_data)

print("Graph creation successful!")
