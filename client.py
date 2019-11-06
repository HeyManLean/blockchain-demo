# coding=utf-8

"""
客户端
"""
import json

import requests


CONNECTED_NODE_ADDRESS = 'http://127.0.0.1:8000'


def fetch_posts():
    posts = []

    get_chain_address = '{}/chain'.format(CONNECTED_NODE_ADDRESS)
    response = requests.get(get_chain_address)
    if response.status_code == 200:
        content = []
        chain = response.json()
        print(chain)
        for block in chain['chain']:
            for tx in block['transactions']:
                tx['index'] = block['index']
                tx['hash'] = block['previous_hash']
                content.append(tx)
    
        posts = sorted(content, key=lambda k: k['timestamp'],
                       reverse=True)

    return posts
