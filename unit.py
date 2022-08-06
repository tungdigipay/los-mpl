import json
payload = {
    "tung": "khanh"
}
url = "http://kalapa.vn/"
response = "no"
query = """
mutation m_log_kalapa { 
    insert_LOG_kalapa(
        objects: {
            url: "%s", 
            payload: "%s", 
            response: "%s"
        }
    ) { 
        returning { ID } 
    } 
}
    """ % (url, json.dumps(payload), response)

print(query)