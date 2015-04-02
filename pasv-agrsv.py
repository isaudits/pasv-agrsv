#!/usr/bin/env python
'''
@author: Matthew C. Jones, CPA, CISA, OSCP
IS Audits & Consulting, LLC
TJS Deemer Dana LLP

Passive external footprinting

See README.md for licensing information and credits

'''
import ConfigParser
import argparse
import logging
import os

import modules.core
import modules.tools
import modules.db
import modules.menu



#------------------------------------------------------------------------------
# Configure Argparse to handle command line arguments
#------------------------------------------------------------------------------
desc = "Passive footprinting automation script"

parser = argparse.ArgumentParser(description=desc)
parser.add_argument('-c','--config',
                    help='Configuration file. (default: config/default.cfg)',
                    action='store', default='config/default.cfg'
)
parser.add_argument('-a','--aggressive',
                    help='Enable aggressive (non-passive recon) tools',
                    action='store_true'
)
parser.add_argument('-d','--debug',
                    help='Print lots of debugging statements',
                    action="store_const",dest="loglevel",const=logging.DEBUG,
                    default=logging.WARNING
)
parser.add_argument('-v','--verbose',
                    help='Be verbose',
                    action="store_const",dest="loglevel",const=logging.INFO
)
parser.add_argument('domain', help='Single domain to analyze (e.g. example.com)',
                    nargs='?', default = ''
)
args = parser.parse_args()

domain = args.domain
if domain:
    modules.core.projectname = domain
else:
    modules.core.projectname = "default"

config_file = args.config
modules.core.aggressive = args.aggressive

logging.basicConfig(level=args.loglevel)
logging.info('verbose mode enabled')
logging.debug('Debug mode enabled')

#------------------------------------------------------------------------------
# Get config file parameters
#------------------------------------------------------------------------------
modules.core.check_config(config_file)
config = ConfigParser.SafeConfigParser()
config.read(config_file)

try:
    modules.core.output_parent_dir = config.get("main_config", "output_dir")
    modules.core.output_dir = os.path.join(modules.core.output_parent_dir, modules.core.projectname)
    modules.core.website_output_format = config.get("main_config", "website_output_format")
    modules.core.suppress_out = config.getboolean("main_config", "suppress_out")
    modules.core.limit_email_domains = config.getboolean("main_config", "limit_email_domains")
except:
    logging.error("Missing required config file sections. Check running config file against provided example\n")
    modules.core.exit_program()

#------------------------------------------------------------------------------
# Parse tools sections of config file
#------------------------------------------------------------------------------

logging.info("Parsing tools config file...")
for section in config.sections():
    if section == "main_config":
        pass
    else:
        tool = modules.tools.Tool()
        tool.name = section
        if config.has_option(tool.name, "command"):
            tool.command = config.get(tool.name,"command")
        if config.has_option(tool.name, "url"):
            tool.url = config.get(tool.name,"url")
        if config.has_option(tool.name, "run_domain"):
            tool.run_domain = config.getboolean(tool.name,"run_domain")
        if config.has_option(tool.name, "run_ip"):
            tool.run_ip = config.getboolean(tool.name,"run_ip")
        if config.has_option(tool.name, "run_dns"):
            tool.run_dns = config.getboolean(tool.name,"run_dns")
        if config.has_option(tool.name, "email_regex"):
            tool.email_regex = config.get(tool.name,"email_regex")
        if config.has_option(tool.name, "ip_regex"):
            tool.ip_regex = config.get(tool.name,"ip_regex")
        if config.has_option(tool.name, "dns_regex"):
            tool.dns_regex = config.get(tool.name,"dns_regex")
        if config.has_option(tool.name, "cleanup_regex"):
            tool.cleanup_regex = config.get(tool.name,"cleanup_regex")
        if config.has_option(tool.name, "output_subdir"):
            tool.output_subdir = config.get(tool.name,"output_subdir")
        if config.has_option(tool.name, "output_format"):
            tool.output_format = config.get(tool.name,"output_format")
        if config.has_option(tool.name, "aggressive"):
            tool.aggressive = config.get(tool.name,"aggressive")
        modules.core.tools.append(tool)

#------------------------------------------------------------------------------
# Main Program
#------------------------------------------------------------------------------


modules.core.change_project(modules.core.projectname)

if domain:
    
    modules.db.add_domain_to_db(domain)    #add domain parameter to db and fire off
    
    print "\nRunning domain tools..."
    modules.tools.run_domain_tools()
    
    print "\nRunning host tools..."
    modules.tools.run_host_tools()
    
    print "\nDomains tested:"
    modules.db.get_domains_from_db()
    
    print "\nIP addresses identified:"
    modules.db.get_hosts_from_db()
    
    print "\nHostnames identified:"
    modules.db.get_hostnames_from_db()
    
    print "\nEmail addresses identified:"
    modules.db.get_people_from_db()
    
    print "\nScript execution completed!"
    modules.menu.main_menu()
    
else:
    modules.menu.main_menu()