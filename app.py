import uuid

from flask import Flask, render_template, redirect, request
import pointfree

import graph

from utils import first

app = Flask(__name__)

@app.route('/')
def index():
	#print graph.flows()
	return render_template('index.html', flows = graph.flows())

@app.route('/flow/<flow_id>')
def flow(flow_id):
	flow = graph.flow(flow_id)
	questions = [rel.end.properties for rel in flow.relationships.outgoing(['Question'])]
	first_question = first([rel.end for rel in flow.relationships.outgoing(['First'])])
	return render_template('flow.html', flow = flow, questions = questions,
		first_question = first_question)

@app.route('/flow/<flow_id>/question/<question_id>')
def question(flow_id, question_id):
	flow = graph.flow(flow_id)
	question = graph.question(flow_id, question_id)

	return render_template('question.html', flow = flow, question=question)

@app.route('/flow/<flow_id>/question/<question_id>/answer/<answer_id>')
def answer(flow_id, question_id, answer_id):
	flow = graph.flow(flow_id)
	question = graph.question(flow_id, question_id)

	answer = first([answer for answer in question.answers if answer['id'] == answer_id])

	rewards = [rel.end for rel in answer.relationships.outgoing(['Reward'])]

	next_question = first([rel.end for rel in answer.relationships.outgoing(['Next'])])

	return render_template('answer.html',
		flow=flow, question=question, answer=answer, rewards=rewards,
		next_question=next_question)

@app.route('/start/flow/<flow_id>')
def begin_flow(flow_id):
	new_journey_id = uuid.uuid4().hex

	journey = graph.new_journey(flow_id, new_journey_id)


	return redirect('/journey/' + new_journey_id)

@app.route('/journey/<journey_id>', methods=['GET', 'POST'])
def journey(journey_id):
	journey = graph.journey(journey_id)

	if not journey.current_question:
		attributes = graph.all_linked_nodes(journey, 'Attribute')
		return render_template('journey/conclusion.html', journey=journey, attributes=attributes)

	if request.method == "POST":
		answer = request.form['answer']
		answer_node = first([a for a in journey.current_question.answers if a['id'] == answer])
		reward_nodes = graph.all_linked_nodes(answer_node, 'Reward')
		next_question_node = graph.first_linked_node(answer_node, 'Next')

		for reward_node in reward_nodes:
			graph.link(journey, reward_node, "Attribute")

		graph.unlink(journey, "Current")

		if next_question_node:
			graph.link(journey, next_question_node, "Current")

		return redirect('/journey/' + journey_id)

	return render_template('journey/question.html', journey = journey)

if __name__ == '__main__':
	app.run(debug = True)

