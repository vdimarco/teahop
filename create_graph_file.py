import pandas as pd
import numpy as np
import itertools
import collections
import operator
import networkx as nx

df = pd.read_csv('data/teahop_nodes_clean.csv')
print df.columns
print len(df)
df = df[df['flavours'] != 'Not available'].copy()
print len(df)
df = df[df['rating'] > 0].copy()
print len(df)

load_flavours = []
unique_flavours = []

load_ingredients = []
unique_ingredients = []

for k, v in df.iterrows():

    if v['flavours'] != 'Not available': 
        load_flavours.append([x.strip() for x in str(v['flavours']).lower().split(',')])

    if v['ingredients'] != 'Not available':
        load_ingredients.append([x.strip() for x in str(v['ingredients']).lower().split(',')])

unique_flavours = list(set(list(itertools.chain(*load_flavours))))
unique_ingredients = list(set(list(itertools.chain(*load_ingredients))))

print len(unique_flavours)#, unique_flavours
print len(unique_ingredients)#, unique_ingredients
print collections.Counter(list(itertools.chain(*load_flavours)))
print collections.Counter(list(itertools.chain(*load_ingredients)))

counter_flavours = dict(collections.Counter(list(itertools.chain(*load_flavours))))
counter_ingredients = dict(collections.Counter(list(itertools.chain(*load_ingredients))))

import networkx as nx
G=nx.Graph()
for item in unique_flavours:
    G.add_node('flavour_'+str(item))
    G.node['flavour_'+str(item)]['viz'] = {'color': {'r': 255, 'g': 0, 'b': 0, 'a': 0}}
for item in unique_ingredients:
    G.add_node('ingredient_'+str(item))
    G.node['ingredient_'+str(item)]['viz'] = {'color': {'r': 0, 'g': 255, 'b': 0, 'a': 0}}
for item in df['name'].unique():
    G.add_node(str(item))
    G.node[item]['viz'] = {'color': {'r': 0, 'g': 0, 'b': 255, 'a': 0}}

# set the initial weight for the name_ as a calculation considering the mean(flavours) + mean(ingredients)
for k, v in df.iterrows():
    name = 'tea_'+str(v['name'].lower().replace(' ','-'))
    fla = ['flavour_'+x.strip().replace(' ','-') for x in str(v['flavours']).lower().split(',') if x != 'not available']
    ing = ['ingredient_'+x.strip().replace(' ','-') for x in str(v['ingredients']).lower().split(',') if x != 'not available']

    for item in fla:
        G.add_edge(name,item,weight=10)
    for item in ing:
        G.add_edge(name,item,weight=10)
    for f in fla:
        for i in ing:
            if f not in G.neighbors(i):
                G.add_edge(f,i,weight=0)
            G[f][i]['weight'] += 1

nx.write_gpickle(G, 'graph.p')