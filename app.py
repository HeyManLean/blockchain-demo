# coding=utf-8
import json
import time
from hashlib import sha256
import datetime

import requests
from flask import Flask, request, render_template, redirect

from client import fetch_posts, CONNECTED_NODE_ADDRESS


class Block:
    def __init__(self, index, transactions, timestamp, previous_hash):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.hash = ''

    def compute_hash(self):
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return sha256(block_string.encode()).hexdigest()


class Blockchain:
    def __init__(self):
        self.unconfirmed_transactions = []
        self.chain = []
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis_block = Block(0, [], time.time(), '0')
        genesis_block.hash = genesis_block.compute_hash()
        self.chain.append(genesis_block)
    
    @property
    def last_block(self):
        return self.chain[-1]

    difficulty = 2

    def proof_of_work(self, block):
        block.nonce = 0

        computed_hash = block.compute_hash()
        while not computed_hash.startswith('0' * Blockchain.difficulty):
            block.nonce += 1
            computed_hash = block.compute_hash()
    
        return computed_hash

    def add_block(self, block, proof):
        previous_hash = self.last_block.hash

        if previous_hash != block.previous_hash:
            return False
    
        if not self.is_valid_proof(block, proof):
            return False
    
        block.hash = proof
        self.chain.append(block)
        return True

    def is_valid_proof(self, block, block_hash):
        return (block_hash.startswith('0' * Blockchain.difficulty) and 
                block_hash == block.compute_hash())

    def add_new_transaction(self, transcation):
        self.unconfirmed_transactions.append(transcation)

    def mine(self):
        if not self.unconfirmed_transactions:
            return False

        last_block = self.last_block
        new_block = Block(index=last_block.index + 1,
                          transactions=self.unconfirmed_transactions,
                          timestamp=time.time(),
                          previous_hash=last_block.hash)
        proof = self.proof_of_work(new_block)
        self.add_block(new_block, proof)
        self.unconfirmed_transactions = []

        announce_new_block(new_block)

        return new_block.index

    def check_chain_validity(self, chain):
        if len(self.chain) > len(chain):
            return False

        for inx, block in enumerate(self.chain):
            if block.hash != chain[inx].hash:
                return False

        return True


app = Flask(__name__, template_folder='template')
blockchain = Blockchain()


@app.route('/new_transaction', methods=['POST'])
def new_transaction():
    tx_data = request.get_json()
    require_fields = ['author', 'content']

    for field in require_fields:
        if not tx_data.get(field):
            return 'Invalid transaction data', 404

    tx_data['timestamp'] = time.time()

    blockchain.add_new_transaction(tx_data)

    return 'Success', 201


@app.route('/chain', methods=['GET'])
def get_chain():
    chain_data = []
    for block in blockchain.chain:
        chain_data.append(block.__dict__)
    return json.dumps({'length': len(chain_data),
                       'chain': chain_data})


@app.route('/mine', methods=['GET'])
def mine_unconfirmed_transactions():
    result = blockchain.mine()
    if not result:
        return 'No transactions to mine'
    return 'Block #{} is mined.'.format(result)


@app.route('/pending_tx')
def get_pending_tx():
    return json.dumps(blockchain.unconfirmed_transactions)


peers = set()


@app.route('/add_nodes', methods=['POST'])
def register_new_peers():
    nodes = request.get_json()
    if not nodes:
        return 'Invalid data', 400
    for node in nodes:
        peers.add(node)

    return 'Success', 201


def consensus():
    global blockchain

    longest_chain = None
    current_len = len(blockchain)

    for node in peers:
        response = requests.get('http://{}/chain'.format(node))
        length = response.json()['length']
        chain = response.json()['chain']
        if length > current_len and blockchain.check_chain_validity(chain):
            current_len = length
            longest_chain = chain
    
    if longest_chain:
        blockchain = longest_chain
        return True

    return False


@app.route('/add_block', methods=['POST'])
def validate_and_add_block():
    block_data = request.get_json()
    block = Block(block_data['index'], block_data['transactions'],
                  block_data['timestamp'], block_data['previous_hash'])
    proof = block_data['hash']
    added = blockchain.add_block(block, proof)

    if not added:
        return 'The block was discarded by the node', 400

    return 'Block added to the chain', 201


def announce_new_block(block):
    for peer in peers:
        url = 'http://{}/add_block'.format(peer)
        requests.post(url, json=json.dumps(block.__dict__, sort_keys=True))


@app.route('/')
def index():
    posts = fetch_posts()
    return render_template('index.html',
                            title='YourNet: Decentralized '
                                  'content sharing',
                            posts=posts,
                            node_address=CONNECTED_NODE_ADDRESS,
                            readable_time=timestamp_to_string)


@app.route('/submit', methods=['POST'])
def submit_textarea():
    post_content = request.form["content"]
    author = request.form["author"]

    post_object = {
        'author': author,
        'content': post_content,
    }

    new_tx_address = "{}/new_transaction".format(CONNECTED_NODE_ADDRESS)

    requests.post(new_tx_address,
                  json=post_object,
                  headers={'Content-type': 'application/json'})

    return redirect('/')


def timestamp_to_string(epoch_time):
    return datetime.datetime.fromtimestamp(epoch_time).strftime('%H:%M')


if __name__ == '__main__':
    app.run(debug=True, port=8000)
