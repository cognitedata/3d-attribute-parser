import requests, pickle, os, json

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
  name_id_map = {}
  done = False
  cursor = None

  duplicate_node_names = {}

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
        name = node['name']
        nodes.append(node)
        if name in name_id_map:
          # Report duplicates and count
          if not name in duplicate_node_names:
            duplicate_node_names[name] = {'ids': [name_id_map[name]], 'count': 0}
          duplicate_node_names[name]['count'] += 1
          duplicate_node_names[name]['ids'].append(node['id'])
        name_id_map[name] = node['id']
    done = cursor==None
    
    print(' Downloading nodes: ', len(nodes))
    if node_count_cap and len(nodes) > node_count_cap:
      break
  print('Found ', len(duplicate_node_names.keys()), ' duplicate node names in 3D model.')
  with open('duplicate_node_names.json', 'w') as o:
    json.dump(duplicate_node_names, o)
  return name_id_map
