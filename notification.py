from flask import Flask
from flask import request
from json import dumps
from httplib2 import Http
import json
from gitlab import Gitlab
import requests
application = Flask(__name__)
def get_pipeline(project_id, branch):
    gl = Gitlab('YOUR_GITLAB_URL', 'YOUR_GITLAB_PERSONAL_ACCESS_TOKEN')
    gl.auth()
    project = gl.projects.get(project_id)
    pipelines = project.pipelines.list(ref=branch,all=True)
    return pipelines[0].web_url
def send(data):
   """Teams Chat incoming webhook"""
   url = 'TEAMS_INCOMING_APP_WEBHOOK'
   message_headers = {'Content-Type': 'application/json; charset=UTF-8'}

   http_obj = Http()
   status = data['object_attributes']['detailed_status']
   event = data['object_kind']
   isPipeline = event == 'pipeline'
   if status != 'running' and isPipeline:
    project = data['project']['name']
    project_id = data['project']['id']
    branch = data['object_attributes']['ref']
    user = data['user']['name']
    commit = data['commit']['message']

    print('Calling API')
    pipeline = get_pipeline(project_id, branch)

    response = requests.post(
        url,
        headers=message_headers,
        json= {
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "themeColor": "0076D7",
            "summary": "Deployment on" + branch,
            "sections": [{
                "activityTitle": "Deployment on " + branch,
                "activitySubtitle": "On Project " + project,
                "facts": [{
                    "name": "Triggered by",
                    "value": user
                }, {
                    "name": "Status",
                    "value": status
                }, {
                    "name": "Commit message",
                    "value": commit
                }, {
                    "name": "Pipeline link",
                    "value": pipeline
                }
                ],
                "markdown": True
    }]
        }
    )
@application.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        content = request.get_json(silent=True)
        send(content)
        return 'OK\n'
    else:
        return 'WORKING!!!!!!!!'
if __name__ == "__main__":
    application.run(host='0.0.0.0', debug=True)
