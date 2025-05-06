{
    "event": "finished", "running", "waiting_input",
    "task_id": "task_id_1223",
    "data": {
        "question": "wcan you provide me the value for. this feid",
        "form_field": "name"
    }
}


Slack Agent -> get user input -> check if the task_id is "awaiting input", -> call  pi/v1/task-input { "task_id": "", "field" => "value"}

on Cloud Browser:
api/v1/task-input -> check payload -> find the  agent for task_id -> process payload -> reusme agaeent with that payload