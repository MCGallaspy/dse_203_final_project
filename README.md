# Layout of project

The work of the project is roughly divided into three directories:

* scraping: Contains code for scraping data from WikiPedia and other sources.
* processing: Code for processing the scraped data into node lists, edge lists, and properties.
* graph: Code for loading the processed data into the neo4j graph database.

# Scraping

A few notes on the files under the scraping directory:

* Under the scraping/mike directory we have two scrapy spider classes for scraping info from wikipedia pages and
  NAICS codes from the siccode.com. The "raw" results are written to json files in that same directory, in particular
  the compressed output2.json.gz for WikiPedia results and naics.json for NAICS codes.
* The notebook 'Exploring scraped data.ipynb' demonstrates the structure of the scraped wikipedia data in output2.json.
* 'Extracting nodes, edges, and properties.ipynb' demonstrates reformatting the extracted data into node and edge lists.
* Under scraping/kevin_scrape is an alternate scraping code using Selenium which attempted to process the data instead
  of storing the html. Results are stored in result_kk.json.

# Processing

This directory contains many scripts that process the scraped data. The end goal is to produce five tab-separated value
files in the processing/5tables directory that would correspond to the nodes, edges, and properties in the neo4j database.
The schema of the tables is the one described in slides in class for a property graph.

A few notes on the several notebooks contained in this directory:

* 'NLP with spacy.ipynb' and 'NLP with spacy - 2.ipynb' explore the scraped wikipedia data and attempts to apply
  named entity recognition (NER). The results are "messy" and require entity resolution, so a simple attempt is made. (It's
  not very effective.)
* 'Extracting high-quality entities from entity list.ipynb' again applies NER and extracts entities using the very simple
  heuristic that more commonly identified entities are higher quality. The results are qualitatively "somewhat ok".
* The files under processing/NLP_Processing apply some more NLP techniques to extract entities, and extracts
  edges and properties using part-of-speech tagging to match sentence structures.
* 'Creating 5-table data.ipynb' combines all processed data so far in to the 5-table format described in the class slides,
   enabling the data to be easily loaded into neo4j.
* 'Adding NAICS codes.ipynb' specifically augments the node and edge lists with NAICS codes and the connections between
   them.
* 'Setting NAICS codes for ORGs.ipynb' creates connections between organizations in the database and their scraped
   NAICS codes.
* 'Create node and edge type histograms.ipynb' exhibits the types and quantities of entities in the graph.

# Graph

All code for loading into the graph is contained here. Additionally, there is some normalization of dates and numerical
values, e.g. various data formats have the year extracted, and quantities like $12M and 12,000,000 become identified.

# Instructions for pushing

On your local machine, check out a new branch when adding code or data:

    git checkout -b my_new_branch

Once you have made your commits, push your code to a new branch on the remote repo, and open a pull request:

    git push origin my_new_branch

Contact me if you have any technical questions related to git.
