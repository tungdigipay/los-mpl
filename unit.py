import json
from libraries import Hasura

payload = {
    "tung": "khanh"
}
url = "http://kalapa.vn/"
response = "no"
query = """
query LOS_customers {
  LOS_customers {
    ID
    fullName,
    LOS_master_gender{
      label score
    }
  }
}
    """

print(Hasura.process("LOS_customers", query))