import requests, pickle, os

def get(url):
  baseUrl = "https://api.cognitedata.com/api/0.6/projects/%s" % os.getenv('COGNITE_PROJECT')
  url = baseUrl+url
  
  headers = {'Api-key': os.getenv('COGNITE_API_KEY'),
         'Content-Type': 'application/json'}
  params = {}
  cookies = {}

  max_tries = 20

  for attempt in range(max_tries):
    try:
      res = requests.get(url, params=params, headers=headers, cookies=cookies)
      if res.status_code == 200:
        data = res.json()
        return data
      else:
        print('Got error: ', res)
        print('url: ', url)
        exit()
    except Exception as e:
      if attempt == max_tries:
        print('Error, tried requesting nodes 20 times: ', str(e))
        exit()

def get_nodes(model_id, revision_id, node_count_cap = None):
  print('Getting nodes from 3D api')
  nodes = []
  nameIdMap = {}
  done = False
  cursor = None

  while not done:
    url = '/3d/models/%s/revisions/%s/nodes?limit=1000' % (model_id, revision_id)
    if cursor:
      url += '&cursor=%s' % cursor
    cursor = None

    response = get(url)
    if response:
      data = response['data']
      cursor = data['nextCursor'] if 'nextCursor' in data.keys() else None
      for node in data['items']:
        nodes.append(node)
        nameIdMap[node['name']] = node['id']
    done = cursor==None
    
    print(' Downloading nodes: ', len(nodes))
    if node_count_cap and len(nodes) > node_count_cap:
      break
  return nameIdMap
