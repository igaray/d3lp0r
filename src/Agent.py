﻿# -*- coding: utf-8 -*-

import sys
import time
import socket
import argparse
import cProfile
import cPickle
from connection.MASSimConnection import MASSimConnection
from connection.MessageHandling  import *
from perceptServer.PerceptServer import PerceptConnection, VortexPerceptConnection
from pyswip.prolog               import Prolog
from pyswip.easy                 import *

####################################################################################################
class Agent():
    
# The Agent class' point of entry is the mainLoop method.
# This method cycles through simulations and exits when it receives a 'bye'
# message or encounters an anomalous situation. The mainLoop method calls the
# perceiveActLoop, which encapsulates message reception and handling.
# If an action-request message is received, the processActionRequest method is
# called.
# This in turn calls the processPerception method, which uses the various other
# process* methods to update the agent's KB with information from the
# perception.
# Decision making takes place in the processActionRequest method.

    #----------------------------------------------------------------------------------------------#
    def __init__(self, USER, PASS, logToFile, massimHost, perceptServerHost, perceptServerPort, dummy, communication, verbose):
        self.firstTurn = True
        self.username = USER
        self.password = PASS
        
        self.dummy = dummy
        if (dummy):
            print "@Agent: Running in dummy mode."
        self.auxTimeDummy = 10 #10 milisegundos para ejecutar dummy
        
        self.communication = communication
        if (communication):
            print "@Agent: Running with communication protocol activated."
        
        self.verbose = verbose
        if (verbose):
            print "@Agent: Running in verbose mode."
        
        self.logToFile = logToFile
        if (logToFile):
            print "@Agent: Logging to file."
            sys.stdout = open('logs/%s-log.txt' % USER, 'w')
        else:
            pass
        self.log = sys.stdout

        self.massimHost = '127.0.0.1'
        if (massimHost):
            self.massimHost = massimHost
        self.deadline = 0
        print "@Agent: Basic initialization",
        self.massimConnection = MASSimConnection(self.massimHost, 12300, USER, PASS)
        
        self.perceptServerHost = perceptServerHost
        self.perceptServerPort = perceptServerPort  
        if (perceptServerPort and perceptServerHost):
            self.perceptConnection = PerceptConnection(perceptServerHost, int(perceptServerPort), USER)
        else:
            self.perceptConnection = VortexPerceptConnection()
        print "done"



    #----------------------------------------------------------------------------------------------#
    def connect(self):
        # Connect and authenticate to the MASSim server.
        try:
            self.massimConnection.connect()
        except:
            print "@Agent: Error during connection attempt to the MASSim server."
            quit()



    #----------------------------------------------------------------------------------------------#
    def disconnect(self):
        # Let both the MASSim server and the percept server know that we will no
        # longer be connecting.
        self.massimConnection.disconnect()
        self.perceptConnection.disconnect()
        if (self.logToFile):
           self.log.close()
           self.log = sys.__stdout__
           sys.stdout = sys.__stdout__



    #----------------------------------------------------------------------------------------------#
    def prologInitialization(self):
        print "@Agent: Prolog initialization",
        self.prolog = Prolog()
        self.prolog.consult("pl/agent.pl")
        if (self.logToFile):
            self.prolog.query("redirect_output('logs/%s-kb%d.xml')" % (self.username, self.currentLoop)).next()
        if (self.verbose):
            self.prolog.query("assert(verbose)").next()
        print "done"



    #----------------------------------------------------------------------------------------------#
    def prologFinalization(self):
        print "@Agent: Prolog finalization",
        self.prolog.query("retractall(k(_))").next()
        self.prolog.query("retractall(b(_))").next()
        self.prolog.query("retractall(h(_))").next()
        self.prolog.query("retractall(myName(_))").next()
        self.prolog.query("retractall(visibleNode(_))").next()
        self.prolog.query("retractall(notVisible(_))").next()
        self.prolog.query("retractall(explored(_))").next()
        self.prolog.query("retractall(notExplored(_))").next()
        self.prolog.query("retractall(inRange(_))").next()
        self.prolog.query("retractall(buyCount(_,_))").next()
        if self.verbose:
            self.prolog.query("saveKB('-%d')" % self.currentLoop).next()
        self.prolog.query("close_output").next()
        self.prolog = None
        print "done"



    #----------------------------------------------------------------------------------------------#
    def processSimulationStart(self, msg_dict):

        def roleHardCode(username):
            roledict = { '1'  : 'explorer'
                       , '2'  : 'explorer'
                       , '3'  : 'repairer'
                       , '4'  : 'repairer'
                       , '5'  : 'saboteur'
                       , '6'  : 'saboteur'
                       , '7'  : 'sentinel'
                       , '8'  : 'sentinel'
                       , '9'  : 'inspector'
                       , '10' : 'inspector'
                       }
            number = username[-1:]
            if (number == '0'):
                number = '10'
            return roledict[number]
            
        defaultVisionRange = { 'explorer' : 2
                             , 'repairer' : 1
                             , 'saboteur' : 1
                             , 'sentinel' : 3
                             , 'inspector': 1
                             }

        self.role = roleHardCode(self.username)
        self.prolog_role_file = "pl/%s.pl" % (self.role)
        self.prolog.consult(self.prolog_role_file)

        if self.username[-1] == '0':
            team = self.username[:-2]
        else:
            team = self.username[:-1]
        for x in range(1,11):
            self.prolog.query("assertOnce(k(agentRole(%s%d, %s)))" % (team, x, roleHardCode(str(x)))).next()

        self.prolog.query("updateMyName(%s)" % self.username).next()
        if (self.communication):
            self.prolog.query("conectar(%s)" % self.username).next()
            self.prolog.query("registrar([d3lp0r, %s], mapc)" % self.role).next()
        print "@Agent: Saving the visual range of %s: %s" % (self.role, defaultVisionRange[self.role])
        self.prolog.query("assert(myVisionRange(%s))" % defaultVisionRange[self.role]).next()
        self.prolog.query("assert(k(agentVisionRange(0,%s,%s)))" % (self.username, defaultVisionRange[self.role])).next()



    #----------------------------------------------------------------------------------------------#
    def merge_percepts(self, msg_dict_public, msg_dict_difference):
        msg_dict_public['position'].extend(       msg_dict_difference.get('position',       []))
        msg_dict_public['vis_verts'].extend(      msg_dict_difference.get('vis_verts',      []))
        msg_dict_public['vis_edges'].extend(      msg_dict_difference.get('vis_edges',      []))
        msg_dict_public['vis_ents'].extend(       msg_dict_difference.get('vis_ents',       []))
        msg_dict_public['probed_verts'].extend(   msg_dict_difference.get('probed_verts',   []))
        msg_dict_public['surveyed_edges'].extend( msg_dict_difference.get('surveyed_edges', []))
        msg_dict_public['inspected_ents'].extend( msg_dict_difference.get('inspected_ents', []))



    #----------------------------------------------------------------------------------------------#
    def processNodes(self, msg_dict):
        # First, we obtain all the probed vertices.
        # Then, for each visible vertex, we check whether the vertx is among the probed vertices.
        # If it is, it's information is updated with it's value.
        # Otherwise, it's information is updated with the value unknown.
        probed_verts = msg_dict.get('probed_verts', [])
        self.prolog.query("retractall(inRange(_))").next()
        for x in msg_dict.get('vis_verts', []):
            self.prolog.query("asserta(inRange(%s))" % x['name']).next()
            # in_pv == "in probed vertices"
            in_pv = False
            for pv in probed_verts:
                if (pv['name'] == x['name']):
                    in_pv = True
                    break
            if (in_pv):
                self.prolog.query('updateNodeValue(%s,%s)' % (x['name'], pv['value'])).next()
            else:
                self.prolog.query('updateNodeValue(%s,unknown)' % x['name']).next()
            self.prolog.query('updateNodeTeam(%s,%s)' % (x['name'], x['team'])).next()



    #----------------------------------------------------------------------------------------------#
    def processEdges(self, msg_dict):
        # We update the map state with edges.
        for e in msg_dict.get('vis_edges', []):
            self.prolog.query("updateEdge(%s,%s,unknown)" % (e['node1'], e['node2'])).next()
        for e in msg_dict.get('surveyed_edges', []):
            self.prolog.query("updateEdge(%s,%s,%s)" % (e['node1'], e['node2'], e['weight'])).next()



    #----------------------------------------------------------------------------------------------#
    def processEntities(self, msg_dict_private, msg_dict_public):
        # Process the rest of the visible entities.
        for vis_ent in msg_dict_public['vis_ents']:
            self.prolog.query("updateEntityTeamPosition(%s,%s,%s,%s)" % (vis_ent['name'], vis_ent['team'], vis_ent['node'], vis_ent['status'])).next()

        # Proceso las entidades en la percepcion compartida.
        # Si o si son de tu equipo, luego el team se fija a el propio.
        for p in msg_dict_public.get('position', []):
            # Get my own team name from the list of visible entities.
            team = 'd3lp0r'
            for e in msg_dict_public['vis_ents']:
                if (unicode(self.username) == e['name']):
                    team = e['team']
                    break

            # Caso especial: cuando soy yo mismo.
            if (p['name'] == 'self'):
                parameters = ( self.username
                             , team
                             , p['node']
                             , self.role
                             , msg_dict_private['energy']
                             , msg_dict_private['max_energy']
                             , msg_dict_private['health']
                             , msg_dict_private['max_health']
                             , msg_dict_private['strength']
                             , msg_dict_private['vis_range']
                             )
                self.prolog.query("updateEntity(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)" % parameters).next()
            else:
                parameters = ( p['name']
                             , team
                             , p['node']
                             , p['health']
                             , p['max_health']
                             , p['vis_range']
                             )
                self.prolog.query("updateTeammateEntity(%s,%s,%s,%s,%s,%s)" % parameters).next()

        # Proceso las entidades inspeccionadas.
        for e in msg_dict_public['inspected_ents']:
            parameters = ( e['name']
                         , e['team']
                         , e['node']
                         , e['role']
                         , e['energy']
                         , e['max_energy']
                         , e['health']
                         , e['max_health']
                         , e['strength']
                         , e['vis_range']
                         )
            self.prolog.query("updateEntity(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)" % parameters).next()



    #----------------------------------------------------------------------------------------------#
    def processPerception(self, msg_dict_private, msg_dict_public):
        # Actualizamos cada uno de los campos individuales del agente.
        self.prolog.query("updateStep(%s)"              % msg_dict_private['step']).next()
        self.prolog.query("updateMaxEnergyDisabled(%s)" % msg_dict_private['max_energy_disabled']).next()
        self.prolog.query("updateLastAction(%s)"        % msg_dict_private['last_action']).next()
        self.prolog.query("updateLastActionResult(%s)"  % msg_dict_private['last_action_result']).next()
        self.prolog.query("updateMoney(%s)"             % msg_dict_private['money']).next()
        self.prolog.query("updateScore(%s)"             % msg_dict_private['score']).next()
        self.prolog.query("updateZoneScore(%s)"         % msg_dict_private['zone_score']).next()
        self.prolog.query("updateLastStepScore(%s)"     % msg_dict_private['last_step_score']).next()
        self.processNodes(msg_dict_public)
        self.processEdges(msg_dict_public)
        self.processEntities(msg_dict_private, msg_dict_public)
        self.prolog.query("updatePhase").next()



    #----------------------------------------------------------------------------------------------#
    def processActionRequest(self, action_id, msg_dict_private, msg_dict_public):
        print "@Agent: received request-action. id: %s" % action_id

        # Synchronize perceptions with others.
        if (self.firstTurn):
            msg_dict_difference = self.perceptConnection.send_and_recv(msg_dict_public, True)
            print "@Agent: first turn running, requesting history from percept server."
            print_message(msg_dict_difference)
        else:
            msg_dict_difference = self.perceptConnection.send_and_recv(msg_dict_public)
        self.merge_percepts(msg_dict_public, msg_dict_difference)

        # Process perception.
        self.processPerception(msg_dict_private, msg_dict_public)
        
        # Decide action.
        now = time.time()
        if self.dummy or (now > self.deadline):
            query_result = self.prolog.query("execDummy(X)").next()
        else:
            self.remainingTime = self.deadline - now
            query_result = self.prolog.query("run(%s, X)" % self.remainingTime).next()
        actionList   = query_result['X']

        if   (len(actionList) == 1):
            action_xml = action(action_id, actionList[0])
            action_str = actionList[0]
            print "@Agent: action: %s" % actionList[0]
        elif (len(actionList) == 2):
            print "@Agent: action: %s %s" % (actionList[0], actionList[1])
            action_str = '%s(%s)' % (actionList[0], actionList[1])
            action_xml = action(action_id, actionList[0], actionList[1])
        else:
            print "@Agent: error in returned action."
            print "@Agent: return value: %s" % actionList
            action_xml = action(action_id, "skip")
            action_str = 'skip'
        return (action_xml, action_str)



    #----------------------------------------------------------------------------------------------#
    def perceiveActLoop(self):
        # Receive simulation start notification.
        print "@Agent: Waiting for message from MASSim server."

        xml = self.massimConnection.receive()
        msg_type, _, msg_dict, _ = parse(xml)

        quitPerceiveActLoop = False
        while (not quitPerceiveActLoop):
            
            xml = self.massimConnection.receive()
            msg_type, action_id, msg_dict_private, msg_dict_public = parse(xml)

            # Apparently, the sim-start message is not received at the very beginning. 
            self.processSimulationStart(msg_dict)

            if (msg_type == 'sim-start'):
                print "\n\n===== NEW SIMULATION =====\n\n"
                print "@Agent: Received simulation start notification."
                print_message(msg_dict)
                print "@Agent: Processing simulation start...",
                self.processSimulationStart(msg_dict)
                print "done"
                quitPerceiveActLoop = False
            elif (msg_type == 'request-action'):
                print "@Agent: %s receiving perception from server..." % self.username
                self.turnStartTime = time.time()
                self.deadline = self.massimConnection.messageReceived + msg_dict_private['total_time'] / 1000 - 0.2 # VALOR A CAMBIAR
                print "------------------------------------------------------------"
                print "@Agent: Step: %s" % msg_dict_private['step']

                # Primera fase deliberativa: el agente considera por si mismo que accion realizar.
                action_xml, action_str = self.processActionRequest(action_id, msg_dict_private, msg_dict_public)

                # Segunda fase: los agentes se comunican entre si, y se reconsideran las acciones.
                if (self.communication):
                    self.prolog.query("communicateAndResolveConflicts(%s, NewAction)" % action_str).next()

                # Send the action to the MASSim server.
                self.massimConnection.send(action_xml)
                self.firstTurn = False
            elif (msg_type == 'sim-end'):
                print "@Agent: Received sim-end"
                print_message(msg_dict_private)
                quitPerceiveActLoop = True
            elif (msg_type == 'bye'):
                print "@Agent: Received bye"
                print_message(msg_dict_private)
                self.quit = True
                quitPerceiveActLoop = True
            else:
                print "@Agent: In area 51."
                print_message(msg_dict_private)
                quitPerceiveActLoop = True
                self.quit = True



    #----------------------------------------------------------------------------------------------#
    def mainLoop(self):
        self.quit = False
        agent.connect()
        self.currentLoop = 0
        while (not self.quit):
            self.currentLoop += 1
            self.prologInitialization()
            try:
                self.perceiveActLoop()
            except socket.error:
                self.prolog.query("catch(saveKB('-fin-%d'),E,writeln(E))" % self.currentLoop).next()
                sys.exit(0)
            self.prologFinalization()
        if not self.logToFile:
            raw_input("\nFinished. Press ENTER to continue...")
        agent.disconnect()



####################################################################################################
if (__name__== "__main__"):
    parser = argparse.ArgumentParser(description="Pyeismassim agent initializer")
    parser.add_argument('user',     metavar='USER',                      help="the agent's username")
    parser.add_argument('password', metavar='PASSWORD',                  help="the agent's password")
    parser.add_argument('-ms',      metavar='MASSIM_SERVER_HOST',        help="the massim server host",                                                          dest='massimHost')
    parser.add_argument('-sh',      metavar='SH_PERCEPTION_SERVER_HOST', help="use shared perception server on specified host",                                  dest='perceptServerHost')
    parser.add_argument('-sp',      metavar='SH_PERCEPTION_SERVER_PORT', help="use shared perception server on specified port",                                  dest='perceptServerPort')
    parser.add_argument('-l',                                            help="write-to-log mode",                             action='store_const', const=True, dest='log')
    parser.add_argument('-d',                                            help="dummy mode",                                    action='store_const', const=True, dest='dummy')
    parser.add_argument('-c',                                            help="use communication after decision making",       action='store_const', const=True, dest='communication')
    parser.add_argument('-v',                                            help="verbose mode",                                  action='store_const', const=True, dest='verbose')
    
    args = parser.parse_args()
    
    agent = Agent( args.user
                 , args.password
                 , args.log
                 , args.massimHost
                 , args.perceptServerHost
                 , args.perceptServerPort
                 , args.dummy
                 , args.communication
                 , args.verbose
                 )
    agent.mainLoop()

