import os
import json

def getItem(item):
    items = json.load(open('items.json', 'r'))
    return items[f'{item}']

def updateItem(item, value):
    items = json.load(open('items.json', 'r'))
    items[f'{item}'] = value
    json.dump(items, open('items.json', 'w'))

def basicSetup(config):
    num_users = len(config['treatments']) * config['replication']
    platforms = config['platforms']
    replication = config['replication']

    treatments = config['treatments']
    names = ['google']
    for platform in platforms:
        for treatment in treatments:
            for i in range(replication):
                name = f"{platform}_{treatment['action']}_{treatment['topic']}_{i}"
                names.append(name)
                for action in ['pre-observation', 'treatment', 'post-observation']:
                    name = f"{action}_{platform}_{treatment['action']}_{treatment['topic']}_{i}"
                    names.append(name)
    if not os.path.exists('items.json'):
        items = {item: 0 for item in names}
        json.dump(items, open('items.json', 'w'))


if __name__ == '__main__':
    config = json.load(open('config.json', 'r'))
    basicSetup(config)