from neo4jrestclient.client import GraphDatabase

import graph
import production

from utils import first

db = GraphDatabase("http://localhost:7474/db/data")

def create_flow_start(index_name, index_key, index_id, id, properties = None):
	if not index_name in db.nodes.indexes.keys():
		db.nodes.indexes.create(index_name)
		print 'Created index %s' % index_name

	index = db.nodes.indexes.get(index_name)

	node = first([node for node in index[index_key][index_id] if node.get("id","") == id])

	if not node:
		node = db.nodes.create(id = id)

		if properties:
			for key, value in properties.items():
				node[key] = value

		index.add(index_key, index_id, node)
		print "New node created"

	return node

flow_id = "papoc"

flow_node = create_flow_start('flows', 'flow', 'start', flow_id, {
	"title" : "After the Apocalypse",
	"description" : "Post-apocalypse character generation in a Fallout vein",})

questions =[
	("q1", "When the bombs started falling where were your parents?"),
	("s1", "Which section did your parents work in?"),
	("w1", "Were they affected by the radiation from the fallout?"),
]

for q_id, question in questions:

	graph.create_unique_node('questions', flow_id, q_id,
		{"id" : q_id, "text" : question})
	graph.link(flow_node, graph.node('questions', flow_id, q_id), "Question")

answers = [
	("q1a1", "They had a place in the shelters"),
	("q1a2", "They had nowhere to run"),

	("s1a1", "Administration"),
	("s1a2", "Security"),
	("s1a3", "Science"),

	("w1a1", "I don't know whether they were tough or lucky but no"),
	("w1a2", "Why do you think I look this way?"),
]

for a_id, answer in answers:
	graph.create_unique_node('answers', flow_id, a_id,
		{"id" : a_id, "text" : answer})

rewards = [
	("q1a1r1", "Shelter-born"),
	("q1a2r1", "Born free"),

	("s1a1r1", "Leadership"),
	("s1a2r1", "Shooter"),
	("s1a2r2", "Brawler"),
	("s1a3r1", "Person of Science"),
	("s1a3r2", "Monkey wrench"),

	("w1a1r1", "Wastelander"), ("w1a2r1", "Mutant"),
]

for reward_id, reward in rewards:
	graph.create_unique_node('rewards', flow_id, reward_id,
		{"type" : "Trait", "value" : reward})

answer_pairs = [
	("q1", "q1a1"), ("q1", "q1a2"),

	("s1", "s1a1"), ("s1", "s1a2"), ("s1", "s1a3"),

	("w1", "w1a1"), ("w1", "w1a2"),
]

graph.link(flow_node, graph.node('questions', flow_id, 'q1'), 'First')

for question_id, answer_id in answer_pairs:
	graph.link(
		graph.node('questions', flow_id, question_id),
		graph.node('answers', flow_id, answer_id),
		"Answer")

reward_pairs = [
	("q1a1", "q1a1r1"),
	("q1a2", "q1a2r1"),

	("s1a1", "s1a1r1"),
	("s1a2", "s1a2r1"),
	("s1a2", "s1a2r2"),
	("s1a3", "s1a3r1"),
	("s1a3", "s1a3r2"),

	("w1a1", "w1a1r1"),
	("w1a2", "w1a2r1"),
]

for answer_id, reward_id in reward_pairs:
	graph.link(
		graph.node('answers', flow_id, answer_id),
		graph.node('rewards', flow_id, reward_id),
		"Reward"
		)

next_pairs = [
	("q1a1", "s1"),
	("q1a2", "w1"),
]

for answer_id, question_id in next_pairs:
	graph.link(
		graph.node('answers', flow_id, answer_id),
		graph.node('questions', flow_id, question_id),
		"Next")




