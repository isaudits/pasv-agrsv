#!/usr/bin/env python
'''
@author: Matthew C. Jones, CPA, CISA, OSCP
IS Audits & Consulting, LLC
TJS Deemer Dana LLP

Core functions

See README.md for licensing information and credits

'''
import sys
import os
import shutil
import subprocess
import tools

# exit routine
def exit_program():
    print "\n\nQuitting...\n"
    sys.exit()
    
# cleanup old or stale files
def cleanup_routine(output_dir):
    '''Returns 'False' if the output directory is dirty and users select not to clean'''
    
    try:
        if not os.listdir(output_dir) == []:
            response = raw_input("\nOutput directory is not empty - delete existing contents? (enter no if you want to append data to existing output files)? [no] ")
            if "y" in response or "Y" in response:
                print("Deleting old output files...\n")
                shutil.rmtree(output_dir, True)
            else:             
                return False
    except:
        pass

def check_config(config_file):
    if os.path.exists(config_file):
        pass
    else:
        print "Specified config file not found. Copying example config file..."
        shutil.copyfile("config/default.example", config_file)

def execute(command, suppress_stdout=False):
    '''
    Execute a shell command and return output as a string
    
    By default, shell command output is also displayed in standard out, which can be suppressed
    with the boolean suppress_stdout
    '''
    
    output = ""
    try:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    
        # Poll process for new output until finished
        while True:
            nextline = process.stdout.readline()
            output += nextline
            if nextline == '' and process.poll() != None:
                break
            if not suppress_stdout:
                sys.stdout.write(nextline)
            sys.stdout.flush()
        
        return output
    except KeyboardInterrupt:
        print "\n[!] Keyboard Interrupt - command '%s' killed..." % command
        print "[!] Continuing script execution..."
        return ""

    except Exception as exception:
        print "\n[!] Error running command '%s'" % command
        print "[!] Exception: %s" % exception
        return ""

def write_outfile(path, filename, output_text):
    if output_text:
        if not os.path.exists(path):
            os.makedirs(path)
            
        outfile = os.path.join(path, filename)
        
        file = open(outfile, 'a+')
        file.write(output_text)
        file.close

def list_to_text(itemlist):
    ''' iterate through list and return a string of the list items separated by newlines'''
    
    output_text = ""
    for item in itemlist:
        output_text += item + "\n"
    return output_text

def nslookup(target, output_dir="", output_subdir=""):
    #if no output directory is specified, command will not save output to a file
    instance = tools.instance()
    instance.name = "nslookup"
    instance.target = target
    instance.command = "nslookup [TARGET]"
    instance.url = ""
    instance.run_domain = False
    instance.run_ip = True
    instance.run_dns = True
    instance.email_regex = ""
    instance.ip_regex = "Address:\s(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
    instance.dns_regex = "name = (.*)"
    instance.cleanup_regex = ""
    instance.output_dir = output_dir
    instance.output_subdir = output_subdir
    instance.suppress_out = False
    instance.run()
    return instance

def sanitise(string):
    '''this function makes a string safe for use in sql query (not necessarily to prevent SQLi)'''
    s = string.replace('\'', '\'\'')
    return s

if __name__ == '__main__':
    #self test code goes here!!!
    nslookup("www.google.com")
    pass