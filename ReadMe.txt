# "CreateGraph.py" is the main file to load all nodes, property, relation, edge.

# This file has following 4 functions:-

Please modify file path/name before run the code..

#A PROCESSING STRUCTURED & UN-STRUCTURED DATA
1. createNodes()
It reads file NodeLabels.tsv and create all nodes with right label.

2. updateNodeProperties()
It reads NodeProperty.tsv and update all nodes with their properties.

3. updateRelations()
It reads Connectivity_Merged.tsv and establish relationship with relationship labels.

4. updateEdges()
It reads EdgeProperty_Merged.tsv and update all edges with their properties.


#B Clean uo ORPHAN nodes
this would reduce nodes from 40K to ~660
MATCH (n) WHERE NOT (n)--() DELETE n

