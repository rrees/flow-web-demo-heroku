import os

from neo4jrestclient.client import GraphDatabase

from settings import GRAPH_URL

from utils import first

credentials = None

if 'NEO4J_LOGIN' in os.environ and 'NEO4J_PASSWORD' in os.environ:
	credentials = (os.environ['NEO4J_LOGIN'], os.environ['NEO4J_PASSWORD'])

if credentials:
	db = GraphDatabase(GRAPH_URL, username = credentials[0], password = credentials[1])
else:
	db = GraphDatabase(GRAPH_URL)

def flows():
	return db.nodes.indexes.get('flows')['flow']['start']

def flow(flow_id):
	matching_flows =  [flow for flow in db.nodes.indexes.get('flows')['flow']['start'] if flow['id'] == flow_id]

	if len(matching_flows) == 1:
		return matching_flows[0]

	return None

def question(flow_id, question_id):

	the_flow = flow(flow_id)

	matching_questions = [rel.end for rel in the_flow.relationships.outgoing(['Question']) if rel.end['id'] == question_id]

	if len(matching_questions) == 1:
		question = matching_questions[0]
		question.answers = [rel.end for rel in question.relationships.outgoing(['Answer'])]
		return question

	return None

def index(index_name):
	if not index_name in db.nodes.indexes:
		db.nodes.indexes.create(index_name)

	return db.nodes.indexes.get(index_name)

def all_linked_nodes(start_node, relationship_type):
	return [rel.end for rel in start_node.relationships.outgoing([relationship_type])]

def first_linked_node(start_node, relationship_type):
	return first(all_linked_nodes(start_node, relationship_type))

def link(a, b, relationship_name):
	existing_links = [node for node in a.relationships.outgoing([relationship_name]) if node.end == b]
	if not existing_links:
		a.relationships.create(relationship_name, b)
	return a

def unlink(a, relationship_name):
	[rel.delete() for rel in a.relationships.outgoing([relationship_name])]

def new_journey(flow_id, journey_id):
	chosen_flow = flow(flow_id)

	first_node = first([rel.end for rel in chosen_flow.relationships.outgoing(['First'])])

	journey_node = db.nodes.create(id=journey_id, flow_id=flow_id)

	journey_index = index('journeys')

	journey_index.add('id', journey_id, journey_node)

	journey_node.relationships.create("Current", first_node)

	return journey_node

def journey(journey_id):
	journey_index = index('journeys')

	journey_node = first(journey_index['id'][journey_id])

	if journey_node:
		journey_node.current_question = first_linked_node(journey_node, 'Current')
		if journey_node.current_question:
			journey_node.current_question.answers = [rel.end for rel in journey_node.current_question.relationships.outgoing(['Answer'])]

	return journey_node

def create_unique_node(index_name, index_key, index_id, properties = None):
	if not index_name in db.nodes.indexes.keys():
		db.nodes.indexes.create(index_name)

	index = db.nodes.indexes.get(index_name)

	node = first(index[index_key][index_id])

	if not node:
		node = db.nodes.create()

		if properties:
			for key, value in properties.items():
				node[key] = value

		index.add(index_key, index_id, node)

	return node

def node(index_name, index_key, index_id):
	index = db.nodes.indexes.get(index_name)

	if not index: return None

	lookup_results = index[index_key][index_id]

	if lookup_results:
		return first(index[index_key][index_id])

	return None