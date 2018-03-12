import hashlib
import json
from textwrap import dedent
from time import time
from uuid import uuid4

from flask import Flask, jsonify, request

class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transcations = []

        self.new_block(proof=100, previous_hash=1)

    def new_block(self, proof, previous_hash=None):
        # create a new block and add it to the chain
        """
        生成新块
        :param proof: the proof given by the proof of work algorithm
        :param previous_hash: hash of the block
        :return: new block
        """

        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transaction': self.current_transcations,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1])
        }

        self.current_transcations = []
        self.chain .append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        # add a new Transcation to the transcations
        """
        生成新的交易信息，将信息加入到下一个待挖的区块中
        :param sender: address of the sender
        :param recipient: address of the recipient
        :param amount: amount
        :return: the index of the block that will hold this transcation
        """
        self.current_transcations.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount
        })
        return self.last_block['index'] + 1

    @staticmethod
    def hash(block):
        # hashes a block
        """
        生成块中的hash256值
        :param self: block
        :return:
        """
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def proof_of_work(self, last_proof):
        """
        简单工作证明
        :return:
        """
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1

        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        """
        验证证明：证明是否hash(last_proof, proof)是否以4个0开头？
        :param last_proof: previous proof
        :param proof: current proof
        :return: true if current , false if not
        """
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    @property
    def last_block(self):
        # return the last blocks
        return self.chain[-1]


# Instantiate our Node
app = Flask(__name__)

# generate a gloablly unquie address for this node
node_identifier = str(uuid4()).replace('_', '')

# instantiate the blockchain
blockchain = Blockchain()

@app.route('/mine', methods=['GET'])
def mine():
    # we run the proof of work algorithm to get the next proof
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    # 为工作量证明的节点提供奖励， 发送者为“0”表示新挖出来的币
    blockchain.new_transaction(sender="0", recipient=node_identifier, amount=1)

    # forge the new block by adding it to the chain
    block = blockchain.new_block(proof)

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transaction': block['transaction'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash']
    }

    return jsonify(response), 200

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing value', 400

    index = blockchain.new_transaction(values['render'], values['recipient'], values['amount'])

    response = {
        'message': f'Transaction will be added to block {index}'
    }

    return jsonify(response), 201

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)