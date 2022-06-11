#!/usr/bin/env python
# coding: utf-8

# In[1]:


from igraph import *
import cairo
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
from networkx import closeness_centrality, reciprocity, overall_reciprocity,transitivity, diameter, average_clustering, betweenness_centrality


# In[23]:


heroes = pd.read_csv('hero-network.csv',names=['from','to '])
edges = pd.read_csv('edges_heroes.csv')


# In[24]:


heroes.head()


# ## 2. Creating Weights

# In[25]:


df_w = heroes.groupby(['from',"to "]).size().reset_index(name='weight')
heroes_w = df_w.sort_values(by = "weight", ascending = False).reset_index().drop(['index'],axis=1)
heroes_w


# ## 2. Eliminating Duplicates

# In[26]:


Df = df_w.loc[df_w["from"] != df_w["to "], ]
Df.sort_values(by='weight', ascending= False)


# In[91]:


hero_network_df=heroes
hero_network_df["from"] = hero_network_df["from"].apply(lambda x: x.strip())
hero_network_df["to "] = hero_network_df["to "].apply(lambda x: x.strip())

hero_network_df.head()

all_heroes = set()

for row in hero_network_df.index:
    all_heroes.add(hero_network_df["from"][row])
    all_heroes.add(hero_network_df["to "][row])
    
print(len(all_heroes))


# In[95]:


undir_hero_map = defaultdict(set)

for row in hero_network_df.index:
    hero1 = hero_network_df["from"][row]
    hero2 = hero_network_df["to "][row]
    
    undir_hero_map[hero1].add(hero2)
    undir_hero_map[hero2].add(hero1)
    
print("There are {} Marvel characters in the dataset".format(len(undir_hero_map.keys())))


# In[96]:


# get the number of edges/links (not weighted)
# from undirected graph
total_num_edges = 0

for hero in undir_hero_map.keys():
    edge_length = len(undir_hero_map[hero])
    total_num_edges += edge_length
    
total_num_edges /= 2

total_num_edges
ordered_heroes = list(all_heroes)



first_deg_df = first_deg_df.sort_values(by='count', ascending=False)

#top 60 heroes by first-degree connections - most of these have appeared in movies already!
first_deg_df.head(60)


# In[99]:


# basic BFS for getting hero degree of separation
from collections import deque

def basicBFS(hero, graph_map):
    queue = deque([hero])
    seen = set([hero])
    
    while(len(queue) > 0):
        curr_hero = queue.popleft()
        
        # add all first-degree heroes not in seen
        for adjacent_hero in graph_map[curr_hero]:
            if(adjacent_hero not in seen):
                queue.append(adjacent_hero)
                seen.add(adjacent_hero)
            
    
    return seen

def connectivity(hero_set, graph_map):
    all_groups = []
    all_seen = set()
    count = 0
    
    for hero in graph_map.keys():
        count += 1
        if(hero not in all_seen):
            hero_group = basicBFS(hero, graph_map)
            all_groups.append(len(hero_group))
            for connected_hero in hero_group:
                all_seen.add(connected_hero)
                
    print("Number of Groupings and Hero Count:", all_groups)
    print("Total Number of Heroes Seen (should match total hero count):", count)
                
    return all_groups

print(connectivity(all_heroes, undir_hero_map))
def hero_BFS(hero1, hero2, graph_map):    
    queue = deque()
    queue.append((hero1, [hero1]))
    seen = set([hero1])
    
    while(len(queue) > 0):
        curr_hero, hero_chain = queue.popleft()
        
        if(curr_hero == hero2):
            return hero_chain
        
        # otherwise, add all unseen heroes to queue, with chain
        for new_hero in graph_map[curr_hero]:
            if(new_hero not in seen):
                new_hero_chain = hero_chain.copy()
                new_hero_chain.append(new_hero)
                
                queue.append((new_hero, new_hero_chain))
                
                seen.add(new_hero)
#     print(seen)
    return ["Not connected!"]
            
# test
hero_BFS('IRON MAN/TONY STARK', "EMPRESS S'BYLL [SKRU", undir_hero_map)


# In[27]:


edges.head()


# ## 3. Eliminating heroes with few appearances

# In[28]:


common = edges['hero'].value_counts()
common_heroes = common[common > 20].index


# In[29]:


common_heroes.value_counts()


# In[30]:


len(common)


# In[31]:


M = Df[Df['from'].isin(common_heroes)]
M_df = M[M['to '].isin(common_heroes)]
M_df = M_df.reset_index().drop(['index'],axis=1)
M_df.sort_values(by='weight', ascending= False)


# In[32]:


len(M_df)


# In[33]:


M_df['to '].nunique()


# In[34]:


g1 = nx.from_pandas_edgelist(M_df,source = 'from', target = 'to ')


# ### a) Degrees

# In[35]:


nxdeg = pd.DataFrame(g1.degree())
nxdeg.sort_values(by = 1,ascending = False)


# In[36]:


sns.histplot(nxdeg, x= nxdeg[1],y = nxdeg.index)


# ### b) Closeness Centrality

# In[37]:


closeness_vec = closeness_centrality(g1)
closeness_df = pd.DataFrame([closeness_vec]).transpose()


# In[38]:


closeness_df


# In[39]:


sns.histplot(closeness_df, x= closeness_df[0],y = nxdeg.index)


# ### c) Betweenness Centrality

# In[40]:


between_vec = betweenness_centrality(g1)
between_df = pd.DataFrame([between_vec]).transpose()


# In[41]:


between_df


# In[42]:


sns.histplot(between_df, x= between_df[0],y = nxdeg.index)


# In[65]:


from networkx.algorithms import community


# In[66]:


from networkx.algorithms.community import greedy_modularity_communities
c = greedy_modularity_communities(g1)


# In[67]:


dfc = pd.DataFrame(c)


# In[68]:


group_0 = dfc.iloc[0]


# In[69]:


group_1 = dfc.iloc[1]


# In[70]:


group_2 = dfc.iloc[2]


# In[71]:


nodes0 = pd.DataFrame(group_0)


# In[72]:


nodes1 = pd.DataFrame(group_1)
nodes1 = nodes1.dropna()


# In[73]:


nodes2 = pd.DataFrame(group_2)
nodes2 = nodes2.dropna()


# In[74]:


data = {'community0':group_0,'community1':group_1,'community2':group_2}


# In[75]:


community_df = pd.DataFrame(data)


# In[76]:


community_df

