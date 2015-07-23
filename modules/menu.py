#!/usr/bin/env python
'''
@author: Matthew C. Jones, CPA, CISA, OSCP
IS Audits & Consulting, LLC
TJS Deemer Dana LLP

Core functions

See README.md for licensing information and credits

'''

import sys, os
import core
import db
import tools
import output
 
# Main definition - constants
menu_actions  = {}  
 
# =======================
#     MENUS FUNCTIONS
# =======================

def banner():
    '''returns menu banner text as string'''
    
    db_domains = db.get_domains_from_db('',False,True)
    db_hosts = db.get_hosts_from_db('',False,True)
    
    banner_text = "pasv-agrsv reconnaisance utility - https://github.com/isaudits/pasv-agrsv/\n\n"
    banner_text += "Project name: "
    banner_text += core.projectname
    banner_text += "\n"
    banner_text += "Active DB path: "
    banner_text += core.dbfilename
    banner_text += "\n"
    
    banner_text += "Domain(s): "
    if not db_domains:
        banner_text += "None identified (add some before testing)"
    else:
        for item in db_domains:
            banner_text += item.domain + ","
    banner_text += "\n"
    
    banner_text += "Targets: "
    if not db_hosts:
        banner_text += "None - run a scan!"
    else:
        banner_text += str(len(db_hosts))
    banner_text += "\n"
    
    return banner_text
# Main menu
def main_menu():
    
    while main_menu:
        os.system('clear')
        
        print banner()
        print "Please choose an action:"
        #print "1. Menu 1"
        #print "2. Menu 2"
        print "1. Change active project"
        print "2. Add domain"
        print "3. List domains"
        print "4. Add target"
        print "5. List targets"
        print "6. List people / emails"
        print "7. Run enumeration on identified domains / targets"
        print "8. Run enumeration on domains only"
        print "9. Run enumeration on targets only"
        print "0. Export data to output directory"
        print "\nq. Quit"
    
        # Menu definition
        menu_actions = {
           'main_menu': main_menu,
           '1': change_project,
           '2': add_domain,
           '3': list_domains,
           '4': add_target,
           '5': list_targets,
           '6': list_people,
           '7': run_all,
           '8': run_domain,
           '9': run_host,
           '0': export_data,
           'q': exit
       }
       
        choice = raw_input(" >>  ")
        exec_menu(choice, menu_actions)
 

# Execute menu
def exec_menu(choice, menu_actions):
    os.system('clear')
    ch = choice.lower()
    if ch == '':
        menu_actions['main_menu']()
    else:
        try:
            menu_actions[ch]()
        except KeyError:
            print "Invalid selection, please try again.\n"
            menu_actions['main_menu']()
    return

# Back to main menu
def back():
    menu_actions['main_menu']()
 
# Exit program
def exit():
    sys.exit()

def change_project():
    projectname = raw_input("Enter project name: >> ")
    core.change_project(projectname)

def add_domain():
    db.add_domain_to_db()

def list_domains():
    db.get_domains_from_db("",True)

def add_target():
    db.add_host_to_db()

def list_targets():
    db.get_hosts_from_db("",False)
    db.get_hostnames_from_db("",True)

def list_people():
    db.get_people_from_db("",True)

def run_all():
    tools.run_all()
    db.export_summary_data(core.output_dir)
    output.write_html_index(core.output_dir)

def run_domain():
    tools.run_domain_tools()
    db.export_summary_data(core.output_dir)
    output.write_html_index(core.output_dir)

def run_host():
    tools.run_host_tools()
    db.export_summary_data(core.output_dir)
    output.write_html_index(core.output_dir)

def export_data():
    outpath = os.path.join(core.output_dir, "export")
    db.export_all(outpath)
    print "Data exported to "+outpath

# Test code
if __name__ == "__main__":
    # Launch main menu
    main_menu()