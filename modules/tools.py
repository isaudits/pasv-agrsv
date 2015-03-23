#!/usr/bin/env python
import re
import os
import core


class tool:
    def __init__(self):
        '''
        Constructor:
        '''
        self.name = ""
        self.command = ""
        self.url = ""
        self.run_domain = False
        self.run_host = False
        self.email_regex = ""
        self.ip_regex = ""
        self.dns_regex = ""
        self.cleanup_regex = ""
        self.output_subdir = ""

class instance(tool):
    def __init__(self):
        '''
        Constructor:
        '''
        self.command_result = ""
        self.target = ""
        self.output_dir = ""
        self.suppress_out = False
        self.website_output_format = "pdf"
        self.emails = []
        self.ip = []
        self.dns = []
        
    def build_instance_from_tool(self, tool):
        '''
        Accepts a tool object, copies parzmeters to an instance object, and returns
        the instance object for execution
        '''
        self.name = tool.name
        self.command = tool.command
        self.url = tool.url
        self.run_domain = tool.run_domain
        self.run_host = tool.run_host
        self.email_regex = tool.email_regex
        self.ip_regex = tool.ip_regex
        self.dns_regex = tool.dns_regex
        self.cleanup_regex = tool.cleanup_regex
        self.output_subdir = tool.output_subdir
        
        
    def run(self):
        '''
        Run an instance of a tool
        '''
        if self.command:
            self.command = self.command.replace("[TARGET]", self.target)
            self.command_result = core.execute(self.command, self.suppress_out)
            core.write_outfile(os.path.join(self.output_dir, self.output_subdir), self.name+ "_" + self.target + ".txt", self.command_result)
            
            if self.email_regex:
                self.emails = sorted(list(set(re.findall(self.email_regex, self.command_result))))
                print "Emails discovered: " + str(self.emails)
            
            if self.ip_regex:
                self.ip = sorted(list(set(re.findall(self.ip_regex, self.command_result))))
                print "IPs discovered: " + str(self.ip)
            
            if self.dns_regex:
                self.dns = sorted(list(set(re.findall(self.dns_regex, self.command_result))))
                print "DNS entries discovered: " + str(self.dns)
                
        if self.url:
            self.url = self.url.replace("[TARGET]", self.target)
            command = "cutycapt --url="+self.url+" --out="+os.path.join(self.output_dir, self.output_subdir, self.name + "_" + self.target + "." + self.website_output_format)
            core.execute(command, self.suppress_out)
        
if __name__ == '__main__':
    #self test code goes here!!!
    pass