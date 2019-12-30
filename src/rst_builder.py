import os
import textwrap

from tabulate import tabulate
from rd_reader import StringCategory, ItemCategory, MethodCategory

class RSTBuilder:
    '''
    RSTBuilder takes an RDReader to build an RST file from an RD file.
    
    
    '''
    MXNET_LINK = "http://github.com/apache/incubator-mxnet/blob/master/"
    def __init__(self, rd_reader):
        self.rd_reader = rd_reader
        self.rst_string = self.get_rst()

    def dedent(func):
        '''
        Normalises all the printed string to fit the docstring indentation
        so textwrap can remove all unnecessary indentations.
        e.g.,
        
        """
        text text 
        {value}
        """
        if value contains \n, the indentation must match "text text"
        
        '''
        def add_indentation_to_new_line(*args, **kwargs):
            return func(*args, **kwargs).replace("\n", "\n        ")
        return add_indentation_to_new_line
            
    @dedent
    def get_default(self, key):
        '''
        The default method to get the string from  "name", "title", and "alias" string
        categories
        '''
        return self.rd_reader.data[key].string

    @dedent
    def get_details(self):
        '''
        The method to get details category.
        Several conditions are applied to the string and they commented.
        If the Rd file does not contain "details", return nothing
        '''
        if "details" in self.rd_reader.data:
            # Check if "defined in ..." is present, if so remove it (this will be used in
            # get_link()).
            details_string = self.rd_reader.data["details"].string
            if "Defined in" in details_string:
                details_string_without_definition = details_string.split("\n")[:-2]
                details_string = "\n".join(details_string.split("\n")[:-2])
            # Create emphasis on Example
            details_string = details_string.replace("Example::", "**Example**::")
            return details_string
            
        return ""

    @dedent
    def get_description(self):
        '''
        Method to get the description.
        '''
        description = self.rd_reader.data["description"].string
        # Somtimes the description is identical to the title.
        # If so, do not print the description
        if description.replace("\n", "") == self.rd_reader.data["title"].string:
            return ""
        else:
            return description

    @dedent
    def get_argument(self):
        '''
        Method to get the arguments. This generates a table that is in a markdown table
        format with tabulate.
        '''
        if "arguments" in self.rd_reader.data:
            headers = ["Argument", "Description"]
            table = []
            argument_items = self.rd_reader.data["arguments"].items

            if len(argument_items) == 0:
                return ""
            
            for argument in argument_items:
                description = argument_items[argument]
                table.append(["``{}``".format(argument), description])
            return tabulate(table, headers, tablefmt="grid")
        else:
            return ""

    @dedent
    def get_usage(self):
        '''
        Method to get the sample usages.
        The usage can be of two types: string or methods.
        '''
        if "usage" in self.rd_reader.data:
            category_class = self.rd_reader.data["usage"]
            if isinstance(category_class, MethodCategory):
                usage_value = category_class.get_value()
            else:
                usage_value = self.rd_reader.data["usage"].string

            usage_value = usage_value.replace("\n", "") # To normalise the indentation
            
            usage_string = '''
            Usage
            ----------
            .. code:: r
            
            \t{usage} 
            '''.format(usage=usage_value)
            return textwrap.dedent(usage_string)
        else:
            return ""

    @dedent
    def get_value(self):
        '''
        To get the value in the mark down file.
        '''
        if "value" in self.rd_reader.data:
            # Put quotations around the first word in the value string
            first_space = self.rd_reader.data["value"].string.find(" ")
            first_word = self.rd_reader.data["value"].string[:first_space].replace("\n", "")
            remaining_words = self.rd_reader.data["value"].string[first_space:]
            value_string = '''
            Value
            ------------------
            ``{first_word}`` {remaining_words}
            '''.format(first_word=first_word, remaining_words=remaining_words)
            return textwrap.dedent(value_string)
        else:
            return ""

    @dedent
    def get_link(self):
        '''
        Parse the last string in the "details" section and make make it into a link to
        the mxnet source code.
        '''
        if "details" in self.rd_reader.data:
            details_string = self.rd_reader.data["details"].string
            defined_in_string = details_string.split("\n")[-2]
            if "Defined in" in defined_in_string:
                path = defined_in_string.split(" ")[-1]
                path, line = path.split(":")
                link_string = '''
                Link to Source Code: {mxnet_link}{path}#{line}
                '''.format(mxnet_link=self.MXNET_LINK, path=path, line=line)
                
                return textwrap.dedent(link_string)
        return ""

    def get_rst(self):
        '''
        The main function of this class.
        Function to build the RST from the Rd file.
        '''
        name = self.get_default("name")
        title = self.get_default("title")
        details = self.get_details()
        description = self.get_description()
        usage = self.get_usage()
        arguments = self.get_argument()
        value = self.get_value()
        link = self.get_link()
        alias = self.get_default("alias")
        
        rst_string = '''\
        .. raw:: html


        ``{name}``
        ============================================
        
        Description
        ----------------------

        {title}
        {description}
        {details}
        
        {usage}

        Arguments
        ------------------

        {arguments}

        {value}

        {link}
        
        .. disqus::
                :disqus_identifier: {alias}

        '''.format(name=name, title=title, description=description, details=details,
                   usage=usage, arguments=arguments, value=value, link=link, alias=alias)

        rst_string_dedent = textwrap.dedent(rst_string)
        return rst_string_dedent

    def write_rst_file(self, directory, filename=None):
        '''
        Function to write the file into storage.
        '''
        if not filename:
            filename = os.path.basename(self.rd_reader.filename).replace(".Rd", ".rst")

        with open(os.path.join(directory, filename), 'w') as f:
            f.write(self.rst_string)
