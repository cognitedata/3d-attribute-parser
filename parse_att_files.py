from cognite3d import get_nodes
from parser import ATTParser
import argparse, os, requests, pickle, json

arg_parser = argparse.ArgumentParser(description='Parse .att files and convert to .json.')
arg_parser.add_argument('--input', '-i', type=str, help='Input folder containing .att files, or path to specific .att file')
arg_parser.add_argument('--outputfile', '-o', type=str, help='Output .json file with map between Cognite 3D node id and PDMS id', default='parsed.json')
arg_parser.add_argument('--reload_3d_nodes', '-t', help='Force reloading of Cognite 3D node ids', action='store_true')
arg_parser.add_argument('--reload_att_files', '-a', help='Force reloading of PDMS ids', action='store_true')
args = arg_parser.parse_args()

def get_node_id_map(model_id, revision_id):
  # Load using pickle unless forced reload or pickle file is missing
  if args.reload_3d_nodes or not os.path.exists('node_id_map.bin'):
    print('Downloading 3D nodes from Cognite API ...')
    node_id_map = get_nodes(model_id, revision_id)
    with open('node_id_map.bin', 'wb') as handle:
      pickle.dump(node_id_map, handle, protocol=pickle.HIGHEST_PROTOCOL)
      print('Dumped 3d node id map to node_id_map.bin')
    return node_id_map
  else:
    with open('node_id_map.bin', 'rb') as handle:
      node_id_map = pickle.load(handle)
      print('Loaded 3d node id map from node_id_map.bin')
      return node_id_map

def get_pdms_id_map():
  # Load using pickle unless forced reload or pickle file is missing
  if args.reload_att_files or not os.path.exists('pdms_id_map.bin'):
    print('Parsing .att files ...')
    parser = ATTParser()
    pdms_id_map = parser.parse(args.input)
    with open('pdms_id_map.bin', 'wb') as handle:
      pickle.dump(pdms_id_map, handle, protocol=pickle.HIGHEST_PROTOCOL)
      print('Dumped pdms id map to pdms_id_map.bin')
    return pdms_id_map
  else:
    with open('pdms_id_map.bin', 'rb') as handle:
      pdms_id_map = pickle.load(handle)
      print('Loaded pdms id map from pdms_id_map.bin')
      return pdms_id_map

# 3ddemo
model_id = 3894221335236914
revision_id = 7395219163381819

node_id_map = get_node_id_map(model_id, revision_id)
pdms_id_map = get_pdms_id_map()

# for name in node_id_map.keys():
#   value = node_id_map[name]
#   del node_id_map[name]
#   node_id_map[name.upper()] = value

# for name in pdms_id_map.keys():
#   value = pdms_id_map[name]
#   del pdms_id_map[name]
#   pdms_id_map[name.upper()] = value

# Loop through and find matches where name is identical in the two maps
node_id_pdms_id_map = {}
pdms_id_node_id_map = {}
print('Building map between node_id and pdms_id')
missing_pdms_ids = {}
for name, pdms_id in pdms_id_map.items():
  if name in node_id_map:
    node_id = node_id_map[name]
    node_id_pdms_id_map[node_id] = pdms_id
    pdms_id_node_id_map[pdms_id] = node_id
  else:
    missing_pdms_ids[name] = pdms_id

# Create dictionary with the two maps to be dumped to json
output = {
  'node_id_pdms_id_map': node_id_pdms_id_map,
  'pdms_id_node_id_map': pdms_id_node_id_map,
  'missing_pdms_ids': missing_pdms_ids,
}



print('Found ', len(node_id_pdms_id_map.keys()), ' matches and ', len(missing_pdms_ids), ' missing pdms ids.')
print('Dumping matches to ', args.outputfile)
# Dump to json
with open(args.outputfile, 'w') as o:
  json.dump(output, o)

# Dump node_id_map to json
print('Dumping node_id_map to node_id_map.json')
with open('node_id_map.json', 'w') as o:
  json.dump(node_id_map, o)

# Dump pdms_id_map to json
print('Dumping pdms_id_map to pdms_id_map.json')
with open('pdms_id_map.json', 'w') as o:
  json.dump(pdms_id_map, o)