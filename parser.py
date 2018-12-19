import os

class ATTParser():
  def __init__(self):
    self.map = {}
    self.supported_versions = ['CADC_Attributes_File v1.0']
    self.valid_tokens = ['start', 'end', 'name_end', 'sep']
    self.reset()

  def reset(self):
    self.tokens = {}
    self.stack = []
    
  def parse_tokens(self, first_line):
    # First line with tokens are on the form
    # CADC_Attributes_File v1.0 , start: NEW , end: END , name_end: := , sep: &end&
    # with tokens start=NEW, end=END etc.
    tokens = {}

    words = first_line.split(',')
    for word in words:
      colon_idx = word.find(':')
      if colon_idx != -1:
        key = word[0:colon_idx].strip()
        value = word[colon_idx+1:].strip()
        tokens[key] = value
    
    return tokens

  def validate_tokens(self, tokens):
    if not set(tokens) == set(self.valid_tokens):
      raise ValueError('Error parsing file. Found unexpected tokens.')

  def validate_file(self, first_line):
    # Check first line for correct version
    if not any(version in first_line for version in self.supported_versions):
      raise ValueError('Unsupported .ATT file version.')

  def parse_string(self, string):
    self.reset()
    lines = string.splitlines()
    for index, line in enumerate(lines):
      line_number = index+1
      if line_number == 1:
        self.validate_file(line)
        self.tokens = self.parse_tokens(line)
        self.validate_tokens(self.tokens)
        continue
      
      line = line.strip()
      
      if line.startswith(self.tokens['start']):
        # Remove start token to extract node name
        self.current_node_name = line.replace(self.tokens['start'], '').strip()
        self.stack.append(self.current_node_name)
        
      if line.startswith(self.tokens['end']):
        if len(self.stack) > 0:
          self.stack.pop()
        continue

      # Next lines are key value pairs,
      # possibly multiple on one line separated by the 'sep' token
      parts = line.split(self.tokens['sep'])
      for part in parts:
        part = part.strip()
        split_pos = part.find(self.tokens['name_end'])
        if split_pos != -1:
          key = part[0:split_pos].strip()
          value = part[split_pos+len(self.tokens['name_end']):].strip()
          if key == ':MIMIRID':
            # Found PDMS-id
            if self.stack[-1] in self.map:
              print('Error, key ', self.stack[-1], ' with PDMS id already exists...')
              print('Old id:', self.map[self.stack[-1]], '. New id: ', value)
            self.map[self.stack[-1]] = value
  
  def parse_file(self, file_path):
    with open(file_path, encoding='latin-1') as f:
      content = f.read()
      self.parse_string(content)
  
  def parse_folder(self, path):
    file_names = [f for f in os.listdir(path) if f.lower().endswith('.att')]
    for count, file_name in enumerate(file_names):
      print('Parsing ', file_name, '(%d of %d)' % (count+1, len(file_names)))
      with open(os.path.join(path, file_name), encoding='latin-1') as f:
        content = f.read()
        self.parse_string(content)

  def parse(self, path):
    # Parse path. Check if it is a single file or a directory containing .att files
    if os.path.isfile(path):
      self.parse_file(path)
    elif os.path.isdir(path):
      self.parse_folder(path)
    
    return self.map
    