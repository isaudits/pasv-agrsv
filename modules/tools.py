#!/usr/bin/env python
'''
@author: Matthew C. Jones, CPA, CISA, OSCP
IS Audits & Consulting, LLC
TJS Deemer Dana LLP

Classes for tool execution

See README.md for licensing information and credits

'''

import re
import os
import core
import db
import output


class Tool:
    def __init__(self):
        '''
        Constructor:
        '''
        self.name = ""
        self.command = ""
        self.url = ""
        self.delay="1000"
        self.run_domain = False
        self.run_ip = False
        self.run_dns = False
        self.email_regex = ""
        self.ip_regex = ""
        self.dns_regex = ""
        self.cleanup_regex = ""
        self.output_subdir = ""
        self.output_format = ""
        self.aggressive = False

class Instance(Tool):
    def __init__(self):
        '''
        Constructor:
        '''
        self.command_result = ""
        self.target = ""
        self.output_dir = ""
        self.suppress_out = False
        self.email_domain_filter = ""
        self.website_output_format = "pdf"
        self.emails = []
        self.ip = []
        self.dns = []
        self.start_time = ""
        self.end_time = ""
        
    def build_instance_from_tool(self, tool):
        '''
        Accepts a tool object, copies attributes to an instance object, and returns
        the instance object for execution
        '''
        self.name = tool.name
        self.command = tool.command
        self.url = tool.url
        self.delay = tool.delay
        self.run_domain = tool.run_domain
        self.run_ip = tool.run_ip
        self.run_dns = tool.run_dns
        self.email_regex = tool.email_regex
        self.ip_regex = tool.ip_regex
        self.dns_regex = tool.dns_regex
        self.cleanup_regex = tool.cleanup_regex
        self.output_subdir = tool.output_subdir
        self.output_format = tool.output_format
        self.aggressive = tool.aggressive
        
        
    def run(self):
        '''
        Run an instance of a tool
        '''
        run_tool = True
        
        if db.check_if_tool_run(self.name, self.target):
            print "Record found in run history for " +self.name + " on " + self.target
            if core.prompt_tool_reruns:
                response = raw_input("Would you like to re-run the tool? [n]")
                if "y" in response or "Y" in response:
                    run_tool = True
                else:
                    run_tool = False
            else:
                run_tool = False
        if not run_tool:
            return
        
        #do not run aggressive tools if aggressive mode is not enabled
        if self.aggressive and not core.aggressive:
            return
        
        if not os.path.exists(os.path.join(self.output_dir, self.output_subdir)):
                os.makedirs(os.path.join(self.output_dir, self.output_subdir))
        
        print "Running "+self.name+" on "+self.target
        
        if self.command:
            output_file_path = os.path.join(self.output_dir, self.output_subdir, self.name + "_" + self.target + "." + self.output_format)
            self.command = self.command.replace("[TARGET]", self.target)
            self.command = self.command.replace("[OUTPUT]", output_file_path)
            
            print self.command
            
            self.start_time = core.getTimestamp(True)
            self.command_result = core.execute(self.command, self.suppress_out)
            self.end_time = core.getTimestamp(True)
            
            if self.cleanup_regex <> "":
                clean_result = re.findall(self.cleanup_regex, self.command_result)
                self.command_result = core.list_to_text(clean_result)
            
            if not self.output_format:
                db.add_run_to_db(self.name, self.target, self.command, self.command_result,'' ,'txt',self.start_time, self.end_time, self.output_subdir)
            else:
                db.add_run_to_db(self.name, self.target, self.command, self.command_result, output_file_path, self.output_format, self.start_time, self.end_time, self.output_subdir)
            print ""
            
            #if no output directory is specified or tool outputs to file itself, then only output to screen...
            if self.output_dir and not self.output_format:
                output.write_outfile(os.path.join(self.output_dir, self.output_subdir), self.name+ "_" + self.target + ".txt", self.command_result)
            
            if self.email_regex:
                self.emails = sorted(list(set(re.findall(self.email_regex, self.command_result))))
                if self.email_domain_filter:
                    self.emails = [s for s in self.emails if self.email_domain_filter in s]
                
                for email in self.emails:
                    email = email.lower()
                    db.add_person_to_db(email)
                    
                print "Emails discovered: " + str(self.emails)
                
            if self.dns_regex:
                self.dns = sorted(list(set(re.findall(self.dns_regex, self.command_result))))
                
                for target in self.dns:
                    target = target.lower()
                    addresses = core.nslookup_fwd(target)
                    for address in addresses:
                        db.add_host_to_db(address,[target])
                
                print "DNS entries discovered: " + str(self.dns)
                
                
            if self.ip_regex:
                self.ip = sorted(list(set(re.findall(self.ip_regex, self.command_result))))
                
                for target in self.ip:
                    hostnames = core.nslookup_rev(target)
                    for hostname in hostnames:
                        hostname = hostname.lower()
                        db.add_host_to_db(target, [hostname])
                
                print "IPs discovered: " + str(self.ip)
            

            
            print "\n" + "-"*80 + "\n"
                
        if self.url:
            self.url = self.url.replace("[TARGET]", self.target)
            output_file_path = os.path.join(self.output_dir, self.output_subdir, self.name + "_" + self.target + "." + self.website_output_format)
            command = "cutycapt --url="+self.url+" --delay="+self.delay+" --out="+output_file_path
            
            #Check for $DISPLAY which returns null if no X server; required for cutycapt (cannot run in SSH / headless)
            if os.environ.get('DISPLAY'):
                core.execute(command, self.suppress_out)
                db.add_run_to_db(self.name, self.target, self.command, self.command_result, output_file_path, self.website_output_format, self.start_time, self.end_time, self.output_subdir)
            else:
                print "[!] No X server detected (maybe inside an SSH session?)"
                print "[!] Cutycapt for screenshot requires X server...skipping...   :("
def run_all():
    
    run_domain_tools()
    run_host_tools()

def run_domain_tools():
    domains=db.get_domains_from_db()
    
    if not domains:
        print "No domains found in DB...Nothing to run..."
        return
    
    for item in domains:
        for tool in core.tools:
            if tool.run_domain == True:
                
                instance = Instance()
                instance.build_instance_from_tool(tool)
                
                instance.target = item.domain
                instance.output_dir = core.output_dir
                instance.suppress_out = core.suppress_out
                instance.website_output_format = core.website_output_format
                
                if core.limit_email_domains:
                    instance.email_domain_filter = item.domain
                
                instance.run()
                core.instances.append(instance)
    
    print "TLD discovery completed"
    
def run_host_tools():
    db_hosts = db.get_hosts_from_db()
    db_hostnames = db.get_hostnames_from_db()
    
    for tool in core.tools:
        if tool.run_ip == True:
            for item in db_hosts:
                instance = Instance()
                instance.build_instance_from_tool(tool)
                
                instance.target = item.ip
                instance.output_dir = core.output_dir
                instance.suppress_out = core.suppress_out
                instance.website_output_format = core.website_output_format
                
                instance.run()
                core.instances.append(instance)
                
        if tool.run_dns == True:
            for item in db_hostnames:
                instance = Instance()
                instance.build_instance_from_tool(tool)
                
                instance.target = item.hostname
                instance.output_dir = core.output_dir
                instance.suppress_out = core.suppress_out
                instance.website_output_format = core.website_output_format
                
                instance.run()
                core.instances.append(instance)
    
    print "\n" + "-"*80 + "\n"
        
if __name__ == '__main__':
    #self test code goes here!!!
    pass
        