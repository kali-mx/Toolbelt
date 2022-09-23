#!/usr/bin/env python3

from flask import Flask, render_template_string, request, Response

app = Flask(__name__)

init_config = {key:app.config[key] for key in app.config}

@app.route('/')
def index():
    return Response(open(__file__).read(), mimetype='text/plain')

@app.route('/docker')
def docker():
    return Response(open("Dockerfile").read(), mimetype='text/plain')

@app.route('/ssti')
def ssti():
    query = request.args['query'] if 'query' in request.args else '...'

    # no persistence!
    to_del = []
    for key in app.config:
        if key not in init_config:
            to_del.append(key)
        else:
            app.config[key] = init_config[key]
    for key in to_del:
        del app.config[key]

    for attr in dir(request):
        if any(attr.startswith(i) for i in ["__"]):
            continue
        try:
            setattr(request, attr, None)
        except Exception as e:
            pass
            # print("Failed to set attr", attr)

    # turns out flask doesn't like it when you nuke their data
    request.environ = {"flask._preserve_context": False}

    if len(set(query)) > 16:
        return f"<div>Too many ({len(set(query))}) unique characters!</div>" + \
               f"<div>Unique characters used: {''.join(set(query))}</div>"

    return f"<div>Number of unique characters: {len(set(query))}</div>" + \
           f"<div>Unique characters used: {''.join(set(query))}</div>" + \
           render_template_string(query)

app.run('0.0.0.0', 5004)
