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
from elixir import metadata, using_options, Entity, Field
from elixir import create_all, setup_all, session
from elixir import Unicode, UnicodeText, Integer, String
from elixir import OneToMany, ManyToMany, ManyToOne, OneToOne

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

class host(Entity):
    using_options(tablename='hosts')
    ip=Field(String)
    hostnames=ManyToMany('hostname')

    def __init__(self, ip='', hostnames=[]):
        self.ip=ip
        self.hostnames=hostnames

class hostname(Entity):
    using_options(tablename='hostnames')
    hostname=Field(String)
    hosts=ManyToMany('host')

    def __init__(self,hostname='', hosts=[]):
        self.hostname=hostname
        self.hosts=hosts

class person(Entity):
    using_options(tablename='people')
    email=Field(String)

    def __init__(self, email=''):
        self.email=email

def isHostInDB(querytext):
    result = host.query.filter(host.ip.contains(querytext)).all()
    if result:
        return True
    return False

def isHostnameInDB(querytext):
    result = hostname.query.filter(hostname.hostname.contains(querytext)).all()
    if result:
        return True
    return False

def getHostsFromDB(filters=''):
    result = host.query.filter(host.ip.contains(filters)).all()
    for item in result:
        print item.ip
    return result

def getHostnamesFromDB(filters=''):
    result = hostname.query.filter(hostname.hostname.contains(filters)).all()
    for item in result:
        print item.hostname
    return result

def addHostToDB(ip='', hostnames=[]):
    db_host = host.query.filter_by(ip=ip).first()
    if not db_host:
        db_host = host(ip)
    
    for name in hostnames:
        db_hostname = hostname.query.filter_by(hostname=name).filter(hostname.hosts.any(host.ip==ip)).first()
        if not db_hostname:
            db_hostname = hostname(name, [db_host])
    
    session.commit()
    
def addPersonToDB(email):
    db_person = person.query.filter_by(email=email).first()
    if not db_person:
        db_person = person(email)

def testQueries(ip, name):
    #do some test queries

    print ip + ' in database? ' + str(isHostInDB(ip))
    print "records in DB containing " + ip
    getHostsFromDB(ip)
    
    print name + ' in database? ' + str(isHostnameInDB(name))
    print "records in DB containing " + name
    getHostnamesFromDB(name)

if __name__ == "__main__":

    db = Database('../tmp/myDatabase')
    
    print "Running initial queries..."
    testQueries('111.222.333.444', 'host1')
    testQueries('123.456.789.123', 'host11')
    
    print "\nAdding some test data..."
    addHostToDB('111.222.333.444', ['host1.domain.com', 'host2.domain.com'])
    addHostToDB('111.222.333.444', ['host3.domain.com'])
    addHostToDB('555.666.777.888', ['host4.domain.com'])
    
    print "\nRunning test queries again..."
    testQueries('111.222.333.444', 'host1')
    testQueries('123.456.789.123', 'host11')
    
    