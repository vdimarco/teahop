import pandas as pd
import numpy as np
import itertools
import collections
import operator
import networkx as nx
import community

df = pd.read_csv('data/teahop_nodes_clean.csv')
# print df.columns
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

# print len(unique_flavours)#, unique_flavours
# print len(unique_ingredients)#, unique_ingredients
# print collections.Counter(list(itertools.chain(*load_flavours)))
# print collections.Counter(list(itertools.chain(*load_ingredients)))

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


def print_top_nodes(sub_list_nodes, min_betweenness, topX):
    dict_nodes = {}
    for n in sub_list_nodes:
        if bc[n] > min_betweenness:
            dict_nodes[n] = round(bc[n]*1000, 4)
    print sorted(dict_nodes.items(), key=operator.itemgetter(1), reverse=True)[:topX]

# define betweenness centrality
bc = nx.betweenness_centrality(G)
# create partitions
partition = community.best_partition(G)

# define 7 big clusters and subclusters
cluster_labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
current_cluster = -1
for i, partition_id in enumerate(set(partition.values())):
    list_nodes = [nodes for nodes in partition.keys() if partition[nodes] == partition_id]
    # consider only partitions with more than 10 nodes
    if len(list_nodes) > 10:
        current_cluster += 1
        # print cluster
        print 'CLUSTER_'+cluster_labels[current_cluster],
        print [len(list_nodes), 
              len([x for x in list_nodes if x.find('flavour_') >= 0]), 
              len([x for x in list_nodes if x.find('ingredient_') >= 0]), 
              len([x for x in list_nodes if x.find('tea_') >= 0])]

        # select nodes
        flavour_nodes = [x for x in list_nodes if x.find('flavour_') >= 0]
        ingredient_nodes = [x for x in list_nodes if x.find('ingredient_') >= 0]
        tea_nodes = [x for x in list_nodes if x.find('tea_') >= 0]

        # print top 20 flavour nodes with betweenness centrality > 0.0001
        print_top_nodes(flavour_nodes, 0.0001, 20)
        # print top 20 flavour nodes with betweenness centrality > 0.0001
        print_top_nodes(ingredient_nodes, 0.0001, 20)

        # define the subclusters
        H = G.subgraph(list_nodes)
        partition_h = community.best_partition(H)
        for h, partition_id_h in enumerate(set(partition_h.values())):
            list_nodes_h = [nodes for nodes in partition_h.keys() if partition_h[nodes] == partition_id_h]

            # consider only partitions with more than 10 nodes
            if len(list_nodes_h) > 10:

                # print cluster
                print 'CLUSTER_'+str(cluster_labels[current_cluster])+'_'+str(h),
                print [len(list_nodes_h), 
                      len([x for x in list_nodes_h if x.find('flavour_') >= 0]), 
                      len([x for x in list_nodes_h if x.find('ingredient_') >= 0]), 
                      len([x for x in list_nodes_h if x.find('tea_') >= 0])]

                # select nodes
                flavour_nodes_h = [x for x in list_nodes_h if x.find('flavour_') >= 0]
                ingredient_nodes_h = [x for x in list_nodes_h if x.find('ingredient_') >= 0]
                tea_nodes_h = [x for x in list_nodes_h if x.find('tea_') >= 0]

                # print top 20 flavour nodes with betweenness centrality > 0.0001
                print_top_nodes(flavour_nodes, 0.000001, 5)
                # print top 20 flavour nodes with betweenness centrality > 0.0001
                print_top_nodes(ingredient_nodes, 0.000001, 5)

        print ''
