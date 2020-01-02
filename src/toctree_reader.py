import json
import textwrap
import os

from tabulate import tabulate

class TocTreeReader:
    '''
    TocTreeReader reads a JSON file describing the toctree to RST files.
    
    Parameters:
    -----------
    filename: str
        Filename of the json file describing tocfile

    rd_readers: [RDReader]
        List of RD reader files reading all the used RD files

    '''
    def __init__(self, filename, rd_readers):
        self.filename = filename
        with open(self.filename) as json_file:
            self.toctree = json.load(json_file)
        self.rd_readers_dict = {}
        for i in rd_readers:
            filename = os.path.basename(i.filename).replace(".Rd", "")
            self.rd_readers_dict[filename] = i

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
    def get_section_title(self, section, underline_type):
        if len(section["title"]) > 0:
            underline = "".join([underline_type]*25) if section[
                "type"] == "General" else ""
            section_title_string = '''
        {title}
        {underline}
            '''.format(title=section["title"].replace("\n", "\n        "),
                       underline=underline)
            return textwrap.dedent(section_title_string)
        else:
            return ""

    @dedent
    def get_section_api(self, section):
        if section["print_api"]:
            apis = []
            for function in section["functions"]:
                rd = self.rd_readers_dict[function]
                value = rd.data["title"].string
                key = ":doc: `{function} <./{function}>`".format(function=function)
                apis.append([key, value])
            return "\n"+tabulate(apis, tablefmt="rst")
        else:
            return ""

    @dedent
    def get_section_toctree(self, section):
        toctree_properties = section["toctree_properties"].replace(
            "\n", "\n           ")
        toctree_string = '''
        .. toctree::
           {toctree_properties}
        '''.format(toctree_properties=toctree_properties)
        
        for function in section["functions"]:
            if section["type"] == "General":
                function_string = '''
           {function}'''.format(function=function)
            else:
                function_string = '''
           {name} <{filename}>'''.format(
                    name=function["name"], filename=function["filename"])
            toctree_string += function_string
        return textwrap.dedent(toctree_string)

    def get_section_string(self, section):
        if section["type"] == "General-sub":
            section_str = ""
            for subsection in section["subsection"]:
                title = self.get_section_title(subsection, "^")
                api = self.get_section_api(subsection)
                toctree = self.get_section_toctree(subsection)
                section = '''
                {title}
                {api}
                
                {toctree}
                '''.format(title=title, api=api, toctree=toctree)
                section_str += section
        else:
            api = self.get_section_api(section)
            toctree = self.get_section_toctree(section)

            section_str = '''
            {api}
            
            {toctree}
            '''.format(api=api, toctree=toctree)
        return section_str
    
    @dedent
    def get_sections(self):
        sections = self.toctree["sections"]
        output_section_strings = ""
        for section in sections:
            title = self.get_section_title(section, "-")
            section_str = self.get_section_string(section)
            
            section_str = '''
            {title}
            {section_str}
            '''.format(title=title, section_str=section_str)
            output_section_strings += section_str
        return textwrap.dedent(output_section_strings)
        
    def write_rst_file(self, directory):
        '''
        Function to write the file into storage.
        '''
        title = self.toctree["title"]
        sections = self.get_sections()
        identifier = self.toctree["identifier"]
        rst_string = '''
        {title}
        ====================================================
        {sections}
                
        .. disqus::
           :disqus_identifier: {identifier}
        '''.format(title=title, sections=sections,
                   identifier=identifier)
        rst_string = textwrap.dedent(rst_string)

        output_basename = os.path.basename(self.filename).replace(".json", ".rst")
        
        with open(os.path.join(directory, output_basename), 'w') as f:
            f.write(rst_string)

