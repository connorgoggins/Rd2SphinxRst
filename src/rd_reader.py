import re

# Helper classes to sort the different types categories.

class StringCategory:
    # The general class where the contents of the category only contains a string
    def __init__(self, string):
        self.string = string

class ItemCategory:
    # The category contains a list of \items{}
    def __init__(self, items):
        self.items = items

class MethodCategory:
    # The category contains a list of \methods{}
    def __init__(self, methods):
        key = next(iter(methods))
        value = methods[key]
        self.methods = (key, value)

    def get_value(self):
        key, value = self.methods
        value1, value2 = value
        output_value = '''.. code:: r
        \t{key}.{value1}{value2}
        '''.format(key=key, value1=value1, value2=value2)
        return output_value
        
class RDReader:
    '''
    RDReader reads an R Markdown file and saves the information into memory.
    The files are automatically generated from Roxygen2 and are in the form of:
    \name{...}
    \title{...}
    \arguments{
    \item{...}
    }
    etc...

    The files are organised in categories (e.g., name, title, argument, example),
    and subcategories (e.g., item, method, etc)

    Parameter:
    ----------
    filename: (str)
        Filename of the R Markdown file
    '''
    def __init__(self, filename):
        self.filename = filename
        file_content = self._read_file(filename)
        self.data = self.parse_file(file_content)

    def parse_file(self, file_content):
        '''
        Iterates through content of the file and parses each category.
        '''
        output = {}
        # Single line category
        singleline_categories = ["name", "alias", "title", "format",
                                "keyword", "doctype"]
        singleline_category_search_string = r"\\(.*?){(.*?)}$"        
        categories = re.findall(singleline_category_search_string,
                          file_content, re.DOTALL|re.MULTILINE)

        for category_string in categories:
            key, value = self._parse_category(category_string)
            if key in singleline_categories:
                output[key] = value
            
        # Multiline categories
        # Note that multiline categories end with "^}$"
        multiline_categories = ["usage", "arguments", "value",
                                "description", "details", "examples"]
        
        multiline_category_search_string = r"^\\([a-z]*?){$(.*?)^}"
        categories = re.findall(multiline_category_search_string,
                          file_content, re.DOTALL|re.MULTILINE)
        for category_string in categories:
            key, value = self._parse_category(category_string)
            if key in multiline_categories:
                output[key] = value

        return output

    def _read_file(self, filename):
        '''
        Helper function to read the contents of the file
        '''
        with open(filename, 'r') as rd_file:
            file_content = rd_file.read()
        return file_content

    def _parse_category(self, category_string):
        '''
        Each category can be in 1 of 2 forms: 1) string, 2) A list of 
        categories i.e., [\(.*){...}] * N.
        
        Parameter:
        ----------
        category: (str)
            The parsed category
        '''
        category_name, content = category_string

        output_class = StringCategory(content)

        # Check if the category contains methods
        method_search_string = r"\\method{(.*?)}{(.*)}(.*)$"
        methods = re.findall(method_search_string, content,
                             re.DOTALL|re.MULTILINE)
        if len(methods) > 0:
            output = {}
            for method in methods:
                name, model, usage = method
                output[name] = (model, usage)
            output_class = MethodCategory(output)
                
        # Check if the category contains items
        # (which are the argument within the "argument" section)
        items_search_string = r"\\item{([a-zA-Z0-9_\\.]*?)}"
        items = re.findall(items_search_string, content,
                                     re.DOTALL)
            
        if len(items) > 0:
            output = {}
            for item in items:
                # Find the description of the argument.
                # i.e., the ones within {}
                start_index = content.find(item) + len(item)
                start, end = self.find_closed_parenthesis(content, start_index)
                if end:
                    description = content[start:end]
                else:
                    description = content[start:]
                output[item] = description
            
            output_class = ItemCategory(output)
                
        return category_name, output_class 
        

    def find_closed_parenthesis(self, content, start_index):
        '''
        Helper function to find the first closed parenthesis.
        '''
        start_index = content.find('{', start_index)
        end_index = None
        counter = 0
        for index, letter in enumerate(content[start_index:]):
            if letter == '{':
                counter += 1
            if letter == '}':
                counter -= 1
            if counter == 0:
                end_index = index
                break
        if end_index:
            return start_index + 1, start_index + end_index
        else:
            return start_index + 1, None
