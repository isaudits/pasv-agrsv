#!/usr/bin/env python
'''
@author: Matthew C. Jones, CPA, CISA, OSCP
IS Audits & Consulting, LLC
TJS Deemer Dana LLP

Database functions
Lots of code borrowed from SPARTA (http://sparta.secforce.com)
Credit SECFORCE (Antonio Quina and Leonidas Stavliotis)

See README.md for licensing information and credits
'''
import logging
import os
import core

try:
    # fix SQLAlchemy version issue with Elixir - 0.8 changed location of ScopedSession
    #http://stackoverflow.com/questions/14201210/impossible-to-initialize-elixir
    from sqlalchemy.orm import scoped_session as ScopedSession
except:
    # have correct version - keep on rolling
    pass

try:  
    from elixir import metadata, using_options, Entity, Field
    from elixir import create_all, setup_all, session
    from elixir import Unicode, UnicodeText, Integer, String, BLOB
    from elixir import OneToMany, ManyToMany, ManyToOne, OneToOne
except:
    print "[-] Import failed. Elixir library not found. \nTry installing it with: apt-get install python-elixir"
    exit(0)

class Database:
    # TODO: sanitise dbfilename
    def __init__(self, dbfilename):
        if not os.path.exists(os.path.dirname(dbfilename)):
            os.makedirs(os.path.dirname(dbfilename))
        try:
            self.name = dbfilename
            metadata.bind = 'sqlite:///'+dbfilename
            #metadata.bind.echo = True                                   # uncomment to see detailed database logs
            setup_all()
            create_all()
        except:
            logging.error('[-] Could not create database. Please try again.')

    def openDB(self, dbfilename):
        try:
            self.name = dbfilename
            metadata.bind = 'sqlite:///'+dbfilename
            #metadata.bind.echo = True                                   # uncomment to see detailed database logs
            setup_all()
        except:
            logging.error('[-] Could not open database file. Is the file corrupted?')

    def commit(self):
        session.commit()

class Host(Entity):
    using_options(tablename='hosts')
    ip=Field(String)
    hostnames=ManyToMany('Hostname')

    def __init__(self, ip=None, hostnames=[]):
        self.ip=ip
        self.hostnames=hostnames

class Hostname(Entity):
    using_options(tablename='hostnames')
    hostname=Field(String)
    hosts=ManyToMany('Host')

    def __init__(self,hostname=None, hosts=[]):
        self.hostname=hostname
        self.hosts=hosts

class Domain(Entity):
    using_options(tablename='domains')
    domain=Field(String)
    
    def __init__(self, domain):
        self.domain=domain

class Person(Entity):
    using_options(tablename='people')
    email=Field(String)

    def __init__(self, email=''):
        self.email=email
        
class ToolRun(Entity):
    using_options(tablename='tool_runs')
    tool=Field(String)
    target=Field(String)
    command=Field(String)
    output=Field(String)
    output_file=Field(BLOB)
    output_filetype=Field(String)
    start_time=Field(String)
    end_time=Field(String)
    subdir=Field(String)

    def __init__(self, tool, target, command, output='', output_file='', output_filetype='', start_time='', end_time='', subdir=''):
        self.tool = tool
        self.target = target
        self.command = command
        self.output = output
        self.output_file = output_file
        self.output_filetype = output_filetype
        self.start_time = start_time
        self.end_time = end_time
        self.subdir = subdir
'''
################################################################################
Database functions


TODO: fix CamelCase for db functions or just leave as is?

################################################################################
'''


def is_host_in_db(querytext):
    result = Host.query.filter(Host.ip.contains(querytext)).all()
    if result:
        return True
    return False

def is_hostname_in_db(querytext):
    result = Hostname.query.filter(Hostname.hostname.contains(querytext)).all()
    if result:
        return True
    return False

def get_hosts_from_db(filters='',pause=False,suppress_screen=False):
    result = Host.query.filter(Host.ip.contains(filters)).all()
    
    if not suppress_screen:
        for item in result:
            print item.ip
    if pause:
        raw_input("Press Enter to continue...")
    return result

def get_domains_from_db(filters='',pause=False,suppress_screen=False):
    result = Domain.query.filter(Domain.domain.contains(filters)).all()
    
    if not suppress_screen:
        for item in result:
            print item.domain
    if pause:
        raw_input("Press Enter to continue...")
    return result

def get_hostnames_from_db(filters='',pause=False,suppress_screen=False):
    result = Hostname.query.filter(Hostname.hostname.contains(filters)).all()
    
    if not suppress_screen:
        for item in result:
            print item.hostname
    if pause:
        raw_input("Press Enter to continue...")
    return result

def get_people_from_db(filters='',pause=False,suppress_screen=False):
    result = Person.query.filter(Person.email.contains(filters)).all()
    for item in result:
        print item.email
    if pause:
        raw_input("Press Enter to continue...")
    return result

def get_toolruns_from_db(filters='',pause=False,suppress_screen=False):
    result = ToolRun.query.all()
    if not suppress_screen:
        for item in result:
            print item.tool+" - "+item.target
    if pause:
        raw_input("Press Enter to continue...")
    return result

def add_domain_to_db(domain=''):
    #nothing passed to function - must be a user prompt
    if not domain:
        print "Enter domain to add (e.g. google.com)"
        domain = raw_input(" >>  ")
        
    db_domain = Domain.query.filter_by(domain=domain).first()
    if not db_domain:
        db_domain = Domain(domain)
    
    session.commit()

def add_host_to_db(ip=None, hostnames=[]):
    #nothing passed to function - must be a user prompt
    if not ip and not hostnames:
        print "Enter ip of target to add (leave blank if only a hostname)"
        ip = raw_input(" >>  ")
        print "Enter hostname(s) of target to add, separated by spaces (leave blank if only an ip)"
        hostnames = raw_input(" >>  ").split()
    
    db_host = Host.query.filter_by(ip=ip).first()
    if not db_host:
        db_host = Host(ip)
    
    for name in hostnames:
        db_hostname = Hostname.query.filter_by(hostname=name).filter(Hostname.hosts.any(Host.ip==ip)).first()
        if not db_hostname:
            db_hostname = Hostname(name, [db_host])
            
        session.commit()
    
def add_person_to_db(email):
    db_person = Person.query.filter_by(email=email).first()
    if not db_person:
        db_person = Person(email)
    
    session.commit()

def add_run_to_db(tool, target, command, output='', output_file_path='', output_filetype='', start_time='', end_time='', subdir=''):
    
    if output_file_path:
        try:
            with open(output_file_path, "rb") as import_file:
                output_file = import_file.read()
            #print "Length = %s" %len(output_file)
        except:
            print "Could not read tool output file"
            output_file = ''
    else:
        output_file = ''
    
    ToolRun(tool, target, command, output, output_file, output_filetype, start_time, end_time, subdir)
    
    session.commit()

def check_if_tool_run(tool, target):
    '''
    accepts a tool name and target (name, ip, or domain) as strings and returns
    true if a corresponding tool run record is found in the database
    '''
    db_tool_run = ToolRun.query.filter_by(tool=tool).filter_by(target=target).first()
    if db_tool_run:
        return True
    else:
        return False
    
def export_all(path):
    '''
    Exports all data in database into a specified path
    '''
    export_summary_data(path)
    export_tool_output(path)

def export_summary_data(path):
    path = os.path.join(path,"summary")
    db_domains = get_domains_from_db('',False,True)
    db_hosts = get_hosts_from_db('',False,True)
    db_hostnames = get_hostnames_from_db('',False,True)
    db_people = get_people_from_db('',False,True)
    
    list_domains=''
    list_hosts=''
    list_hostnames=''
    list_people=''
    
    for item in db_domains:
        list_domains += item.domain + '\n'
        
    for item in db_hosts:
        list_hosts += item.ip + '\n'
        
    for item in db_hostnames:
        list_hostnames += item.hostname + '\n'
        
    for item in db_people:
        list_people += item.email + '\n'

    core.write_outfile(path, "domains.txt", list_domains, True)
    core.write_outfile(path, "hosts.txt", list_hosts, True)
    core.write_outfile(path, "hostnames.txt", list_hostnames, True)
    core.write_outfile(path, "people.txt", list_people, True)
    
def export_tool_output(path):
    '''
    Exports all data in database into a specified path
    '''

    db_toolruns = get_toolruns_from_db('',False,True)
    

    
    for item in db_toolruns:
        filename = item.tool+ "_" + item.target
        outpath = os.path.join(path, item.subdir)
        if not os.path.exists(outpath):
            os.makedirs(outpath)
            
        if not item.output_file:
            filename+=".txt"
            core.write_outfile(outpath, filename, item.output)
        else:
            filename+="."+item.output_filetype
            with open(os.path.join(outpath,filename), "wb") as output_file:
                output_file.write(item.output_file)
            
    
    
def export_run_outfile(db_tool, outfile_path):
    '''
    Accepts a record from the tool_run table and exports the outfile blob to the
    specified path
    
    Example record query to pass to db_tool:
    db_tool = tool_run.query.filter_by(tool=tool).filter_by(target=target).first()
    '''
    
    with open(outfile_path, "wb") as output_file:
        output_file.write(db_tool.output_file)

def test_queries(ip, name):
    #do some test queries

    print ip + ' in database? ' + str(is_host_in_db(ip))
    print "records in DB containing " + ip
    get_hosts_from_db(ip)
    
    print name + ' in database? ' + str(is_hostname_in_db(name))
    print "records in DB containing " + name
    get_hostnames_from_db(name)
    
    print
    get_domains_from_db()
    print

if __name__ == "__main__":

    db = Database('../tmp/myDatabase')
    
    print "Running initial queries..."
    test_queries('111.222.333.444', 'host1')
    test_queries('123.456.789.123', 'host11')
    
    print "\nAdding some test data..."
    add_domain_to_db('test.com')
    add_host_to_db('111.222.333.444', ['host1.domain.com', 'host2.domain.com'])
    add_host_to_db('111.222.333.444', ['host3.domain.com'])
    add_host_to_db('555.666.777.888', ['host4.domain.com'])
    add_run_to_db('nslookup', 'host1.domain.com', 'this is the command', 'this is the output')
    add_run_to_db('nslookup', '555.666.777.888', 'this is another command', 'this is some more output')
    
    print "\nRunning test queries again..."
    test_queries('111.222.333.444', 'host1')
    test_queries('123.456.789.123', 'host11')
    
    export("../tmp/testexport")
    
    