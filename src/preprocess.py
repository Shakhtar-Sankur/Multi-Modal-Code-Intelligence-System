import tree_sitter
from tree_sitter import Language, Parser
import re
import logging

def load_parser(language='python'):
    PY_LANGUAGE = Language('build/my-languages.so', 'python')
    parser = Parser()
    parser.set_language(PY_LANGUAGE)
    return parser

def preprocess_code(code):
    """
    Preprocess code for CodeBERT: tokenize, clean comments, extract metadata.
    """
    logger = logging.getLogger(__name__)
    
    code = re.sub(r'#.*?\n', '\n', code)
    code = re.sub(r'""".*?"""', '', code, flags=re.DOTALL)
    
    parser = load_parser()
    tree = parser.parse(bytes(code, 'utf8')) 
  
    metadata = {'functions': [], 'classes': []}
    for node in tree.root_node.children:
        if node.type == 'function_definition':
            metadata['functions'].append(node.text.decode('utf8'))
        elif node.type == 'class_definition':
            metadata['classes'].append(node.text.decode('utf8'))
    
    logger.info(f"Preprocessed code: {len(code)} chars, {len(metadata['functions'])} functions")
    return {'code': code, 'metadata': metadata}