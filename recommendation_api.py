from flask import Flask, jsonify, render_template, request
import json
import pandas as pd
import numpy as np
import itertools
import collections
import operator
import networkx as nx
import os

app = Flask(__name__)

G = nx.read_gpickle('data/graph_empty.p')

df = pd.read_csv('data/teahop_nodes_clean.csv')
print (df.columns)
print (len(df))
df = df[df['flavours'] != 'Not available'].copy()
print (len(df))
df = df[df['rating'] > 0].copy()
print (len(df))

@app.route('/list', methods=['GET'])
def get_items():
    load_flavours = []
    unique_flavours = []

    load_ingredients = []
    unique_ingredients = []

    load_teas = []

    # df['flavours'] = df['flavours'].apply(lambda x: [y.strip() for y in str(x).split(',') if str(y).find('last update') == -1] if x != 'Not available' else [])
    # df['ingredients'] = df['ingredients'].apply(lambda x: [y.strip() for y in str(x).split(',') if str(y).find('last update') == -1] if x != 'Not available' else [])
    # flavours = list(set(list(itertools.chain(*df['flavours']))))
    # ingredients = list(set(list(itertools.chain(*df['ingredients']))))
    # teas = df[df['name'] != 'Not available']['name'].tolist()
    # flavours = [{'label':f, 'id':'flavour_'+str(f).lower().replace(' ','-')} for f in flavours]
    # ingredients = [{'label':i, 'id':'ingredient_'+str(i).lower().replace(' ','-')} for i in ingredients]
    # teas = [{'label':t, 'id':'tea_'+str(t).lower().replace(' ','-')} for t in teas]
    
    for k, v in df.iterrows():

        if v['flavours'] != 'Not available':
            load_flavours.append([x.strip() for x in str(v['flavours']).split(',') if str(x).find('last update') == -1])

        if v['ingredients'] != 'Not available' and str(v['ingredients']).find('last update') == -1:
            load_ingredients.append([x.strip() for x in str(v['ingredients']).split(',') if str(x).find('last update') == -1])

        if v['name'] != 'Not available':
            load_teas.append(v['name'])
            
    flavours = [{'label':f, 'id':'flavour_'+str(f).lower().replace(' ','-')} for f in flavours]
    ingredients = [{'label':i, 'id':'ingredient_'+str(i).lower().replace(' ','-')} for i in ingredients]
    teas = [{'label':t, 'id':'tea_'+str(t).lower().replace(' ','-')} for t in teas]

    return jsonify({'teas': teas, 'flavours': flavours, 'ingredients': ingredients})

@app.route(
    '/',
    methods=['GET']
    )


def index():
    return render_template("form.html")

@app.route('/recommendation', methods=['POST'])


def get_recommendations():
    candidates = {}

    # rec_teas = []
    # rec_flavours = []
    # rec_ingredients = []
    # dic_teas = []
    # dic_flavours = []
    # dic_ingredients = []


    print (dict(request.json))
    selection = dict(request.json)['items']
    selected_nodes = [x for x in dict(request.json)['items']]
    #selection = {'items':[{'label':'flavour_chocolate', 'type':'flavour'}, {'label':'ingredient_black tea', 'type':'ingredient'}]}
    #selected_nodes = [x['label'] for x in selection['items']]
    print (selected_nodes)

    for k, v in df.iterrows():
        name = 'tea_' + str(v['name'].lower().replace(' ', '-'))
        candidates[name] = 0
        fla = ['flavour_' + x.strip().replace(' ','-') for x in str(v['flavours']).lower().split(',') if x != 'not available']
        ing = ['ingredient_' + x.strip().replace(' ','-') for x in str(v['ingredients']).lower().split(',') if x != 'not available']
        for item in fla:
            if item not in candidates:
                candidates[item] = 0
        for item in ing:
            if item not in candidates:
                candidates[item] = 0

    #selected_nodes = ['flavour_chocolate', 'ingredient_black tea', 'name_chocolate chai', 'flavour_sweet']
    #selected_nodes = ['flavour_chocolate', 'ingredient_black tea']

    for sn in selected_nodes:
        candidates[sn] = 1.0

    max_weight = 37.0
    min_threshold = 0.5
    decay = 0.01

    # Spreading activation
    for sn in selected_nodes:
        for n1 in G.neighbors(sn):
            candidates[n1] += candidates[sn]*(G[sn][n1]['weight']/max_weight)*decay
            for n2 in G.neighbors(n1):
                if n2 not in selected_nodes and candidates[n1] > (min_threshold*len(selected_nodes)):
                    candidates[n2] += candidates[n1]*((G[n1][n2]['weight']/max_weight)/len(G.neighbors(n1)))*decay
                for n3 in G.neighbors(n2):
                    if n3 not in selected_nodes and candidates[n2] > (min_threshold*len(selected_nodes)):
                        candidates[n3] += candidates[n2]*((G[n2][n3]['weight']/max_weight)/len(G.neighbors(n2)))*decay
    for sn in selected_nodes:
        del candidates[sn]

    top_candidates = sorted(candidates.items(), key=operator.itemgetter(1), reverse=True)[:100]
    return jsonify({'suggestions':
        [{'label':k,
        'name':'Butter Sencha',
        'tea_type':'Green',
        'caffeine_level':'Low',
        'url':'https://www.davidstea.com/ca_en/our-teas/tea-type/green/butter-sencha-34',
        'ranking':round(v,6)}
        for k, v in top_candidates]})

    print (top_candidates)

# TODO: add  to `/recommendations`

    # for item in top_candidates:
    #     if item[0].find('tea_') == 0:
    #         rec_teas.append(item)
    #     elif item[0].find('flavour') == 0:
    #         rec_flavours.append(item)
    #     elif item[0].find('ingredient') == 0:
    #         rec_ingredients.append(item)
    # return jsonify({'rec_teas': rec_teas, 'rec_flavours': rec_flavours, 'rec_ingredients': rec_ingredients})


if __name__ == '__main__':
    app.run(debug=True)


 # data = {'items':[{'label':'tea1', 'type':'tea'},{'label':'tea2', 'type':'tea'}, {'label':'ingredient1', 'type':'ingredient'}]}
 # $.ajax({
 #   url: 'http://localhost:5000/recommendation',
 #   type: 'POST',
 #   contentType:'application/json',
 #   data: JSON.stringify(data),
 #   dataType:'json'
 # });
