###############
# Web Service #
###############

# Task 2 of the Developer Programming Task.
#
# A simple web service that accepts a POST method to take in fragments, and
# then reconstruct them using the logic from Task 1.


from flask import Flask, request
import main

app = Flask(__name__)

tasks = []

@app.route('/')
def display_tasks():
    return str(tasks)

# This POST method accepts a json file with a field 'data', which contains a
# file with all the fragments.
@app.route('/', methods=['POST'])
def post_call():
    if not request or not 'data' in request.json:
        abort(400)
    task = {request.json['data']: main.reconstruct(request.json['data'])}
    tasks.append(task)
    return tasks[-1][request.json['data']]

if __name__ == '__main__':
    app.run()
