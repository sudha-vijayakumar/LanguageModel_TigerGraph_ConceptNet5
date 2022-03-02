#!python
#Reference code: 'https://github.com/redsk/neo_wordnet.git'

import os
import operator
import sys
import pickle
import subprocess
import sys
import requests

class WNimporter():
    def __init__(self, wordnetRDFfilename = '../wordnet/wn31.nt'):
        self.replacements = {  'http://wordnet-rdf.princeton.edu/ontology'        : 'wdo', \
                               'http://wordnet-rdf.princeton.edu/wn31'            : 'wn', \
                               'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'  : 'w3#type', \
                               'http://www.w3.org/2000/01/rdf-schema#label'       : 'w3#label', \
                               'http://www.w3.org/1999/02/22-rdf-syntax-ns#first' : 'w3#first', \
                               'http://www.w3.org/1999/02/22-rdf-syntax-ns#rest'  : 'w3#rest', \
                               'http://lemon-model.net/lemon'                     : 'lemon' }

        self.filters = [ 'http://wordnet-rdf.princeton.edu/ontology#translation', \
                         'wn20', \
                         'wn30', \
                         'http://www.w3.org/2002/07/owl#sameAs', \
                         'http://wordnet-rdf.princeton.edu/ontology#old_sense_key', \
                         'http://wordnet-rdf.princeton.edu/ontology#verbnet_class' ]


        self.WNfname = wordnetRDFfilename
        self.path = os.path.dirname(self.WNfname)
        self.nodesFilename = os.path.join(self.path, 'csv_imports/WN-nodes.csv')
        self.edgesFilename = os.path.join(self.path, 'csv_imports/WN-edges.csv')
        self.logFilename = os.path.join(self.path, 'csv_imports/WN-log.log')
        self.WN_unique_fname = self.WNfname[:-3] + '_unique' + self.WNfname[-3:]

    def retrieveWordNet(self):
        if not os.path.isfile(self.WN_unique_fname):
            print('#### Removing duplicated lines in', self.WNfname, ':...',
            sys.stdout.flush())
            args = ['sort', '-us', '-o', self.WN_unique_fname, self.WNfname]
            subprocess.check_call(args)
            print('done.')

        print('#### WordNet 3.1...',
        sys.stdout.flush())
        self.wordnetLines = self.readFile(self.WN_unique_fname)
        print('done.')

        print('#### processing prefixes...',
        sys.stdout.flush())
        self.triples = self.filterAndReplace(self.wordnetLines)
        print('done.')

        print('#### Creating nodes and relationships...',
        sys.stdout.flush())
        self.processTriples(self.triples)
        print('done.')
 


    def readFile(self, fname):
        f = open(fname)
        lines = f.readlines()
        f.close()
        return lines
   
                
    def filterAndReplace(self,lines):
        FRtriples = []
        for l in lines:
            if l != "\n":
                triple = self.getTriple(l)
                if all( [f not in e for f in self.filters for e in triple] ): 
                    for i in range(0, len(triple)):
                        for r in self.replacements:
                            triple[i] = triple[i].replace(r, self.replacements[r])
                    FRtriples.append(triple)
        return FRtriples


    def getTriple(self, l):
        first_space = l.find(' ')
        second_space = l.find(' ', first_space+1)
        triple = [l[0:first_space].strip(), l[first_space+1:second_space].strip(), l[second_space:-3].strip()] 

        for i in range(0, 3):
            if triple[i].startswith('<') and triple[i].endswith('>'):
                triple[i] = triple[i][1:-1]
        
        return triple


    def psd(self, d, returnSorted = False):
        sd = sorted(d.items(), key=operator.itemgetter(1), reverse=True)
        longest = max([len(i) for i in d.keys()])
        for i in sd:
            print(i[0].ljust(longest + 5), str(i[1]).rjust(10))
        
        if returnSorted:
            return sd

    def processTriples(self, triples):
        self.nodes = {}
        self.relationships = []

        self.duplicate_gloss = []
        self.definition = {}
        self.tags = set()
        self.wordKey = {}
        self.antonyms = []
        
        for idx, t in enumerate(triples):

            if t[1]=='wdo#antonym':
                    try:
                      sid = t[0].split('#')
                      sid = sid[1].split('-')
                      sid = sid[-2]+'-'+sid[-1]

                      eid = t[2].split('#')
                      eid = eid[1].split('-')
                      eid = eid[-2]+'-'+eid[-1]

                      self.antonyms.append( {':START_ID': sid, ':END_ID': eid, ':TYPE': t[1]} )
                    except:
                      print()

            if t[1] not in self.tags:
              self.tags.add(t[1])
              t[1] = str(t[1])
            
            if t[1] == str('http://www.w3.org/ns/lemon/ontolex#isLexicalizedSenseOf'):
                process = t[0].split('#')
                word = process[0].rsplit('/', 1)[-1]
                id_ = t[2].rsplit('/', 1)[-1]
                

                if id_ not in self.wordKey:
                  self.wordKey[id_]=word
            try:
                if t[0] in ['', '\n']:
                    continue   
                if t[0].startswith('_'):
                    if t[0] not in self.definition:
                      self.definition[t[0]]=t[2]
            except:
              print('empty definition')

        for idx, t in enumerate(triples):
            try:
                if t[0] in ['', '\n']:
                    continue    
                if t[0].startswith('_'):
                    continue    
                    

                if 'lemma' in str(t[0]):
                  continue

                nodeid = None
                t0Sdash = t[0].split('#')
               
                if len(t0Sdash) > 1:
                    if t0Sdash[1] == 'CanonicalForm' or t0Sdash[1].startswith('Form-'):
                        if t[1] == 'lemon#writtenRep':
                            nodeid = t0Sdash[0]
                            if nodeid not in self.nodes:
                                self.nodes[nodeid] = {}
                            if 'Forms' not in self.nodes[nodeid]:
                                self.nodes[nodeid]['Forms'] = {}
                            self.nodes[nodeid]['Forms'][t0Sdash[1]] = t[2].split('@')[0][1:-1]
                        continue
                    elif t0Sdash[1].startswith('Component-'):
                        continue    
                        
                #id:ID property. implicitly set in the dictionary as key
                nodeid = t[0]   
                # print(t)
                if nodeid not in self.nodes:
                    self.nodes[nodeid] = {}

                n = self.nodes[nodeid] # shortcut
                id_only=nodeid.rsplit('/', 1)[-1]
                

                # LABEL property
                if   t[1] == 'w3#type' and t[2] not in ['lemon#Form', 'lemon#Component']:
                    # count+=1

                    n[':LABEL'] = id_only

                    try:
                      word = self.wordKey[id_only]
                      n['wdo#word'] =  word
                    
                    except:
                      print()


                elif t[1] in ['wdo#partOfSpeech']:
                    pos = str(t[2])
                    pos = pos.split('#')
                    n['wdo#partOfSpeech'] = pos[1] 

                elif str(t[1])==str('http://purl.org/dc/terms/subject'):
                    subject = t[2].replace('"','')
                    n['wdo#subject'] = subject

                elif t[1] in ['wdo#definition']:
                  defnKey = t[2]
                  if t[2] in self.definition:
                    defn = self.definition[t[2]]
                    defn = defn.replace('"','')
                    n['wdo#definition'] = defn

                elif t[1] in self.tags:
                    self.relationships.append( {':START_ID': nodeid, ':END_ID': t[2], ':TYPE': t[1]} )
               
                elif t[1] in ['wdo#synset_member']: 
                    self.relationships.append( {':START_ID': t[2], ':END_ID': nodeid, ':TYPE': t[1]} )


            except Exception as e:
                print('')
                print(e.__repr__())
                print(e.message)
                print('idx =', idx)
                print(t)
                print('Exception, exiting')
                break
        

        print('#### Creating CSV files...',
        sys.stdout.flush())
        self.calculateLowercaseNodesIDs()
        self.writeCSVs()
        
        print('done.')
        print('#### Log file written in ', 
        self.writeLogFile()) 

    def writeCSVs(self):
        self.not_found_nodes = []

        with open(self.nodesFilename, 'w') as f:
            nodeProperties = ['id:ID', ':LABEL', 'wdo#word', 'wdo#partOfSpeech','wdo#definition','wdo#subject']
            headerText = ['uri', 'id','word','pos', 'definition','subject']
            header = '{0}\n'.format(','.join(headerText)) 
            f.write(header)
            
            for nodeID in self.nodes:
                n = self.nodes[nodeID] # faster to type
                
                if n:
                  l = ''
                
                  l += '"{0}","{1}",'.format(nodeID, n[':LABEL'].replace('"',''))

                  if 'wdo#word' in n:
                      l += '"{0}",'.format(n['wdo#word'].replace('"',''))
                  else:
                      l += ','
                  

                  if 'wdo#partOfSpeech' in n:
                      l += '"{0}",'.format(n['wdo#partOfSpeech'].replace('"',''))
                  else:
                      l += ','

                  
                  if 'wdo#definition' in n:
                      l += '"{0}",'.format(n['wdo#definition'])
                  else:
                      l += ','

                  
                  if 'wdo#subject' in n:
                      l += '"{0}"\n'.format(n['wdo#subject'].replace('"',''))
                  else:
                      l += '\n'
                   
                  
                  f.write(l)

        self.rels_with_orphan_nodes = []
        with open(self.edgesFilename, 'w') as f:
            edgeProperties = [':START_ID', ':END_ID', ':TYPE']
            header = '{0}\n'.format(','.join(edgeProperties))
            f.write(header)
            for r in self.relationships:
              
                start_node = self.lookForNode(r[':START_ID'])
                end_node = self.lookForNode(r[':END_ID'])

                if start_node != None and end_node != None:

                    start_node = start_node.rsplit('/', 1)[-1]
                    end_node = end_node.rsplit('/', 1)[-1]
                    typeof=r[':TYPE'].split('#')
                    typeof=typeof[1]
                    rel = '"{0}"\n'.format( '","'.join([start_node.replace('"',''),end_node.replace('"',''),typeof.replace('"','')]))
                    f.write(rel)
                else:
                    self.rels_with_orphan_nodes.append(r)

            for r in self.antonyms:
                print(r)
                start_node = r[':START_ID']
                end_node = r[':END_ID']
                print(start_node)
                if start_node != None and end_node != None:
                    typeof=r[':TYPE'].split('#')
                    typeof=typeof[1]
                    rel = '"{0}"\n'.format( '","'.join([start_node.replace('"',''),end_node.replace('"',''),typeof.replace('"','')]))
                    f.write(rel)
                else:
                    self.rels_with_orphan_nodes.append(r)
    
    def calculateLowercaseNodesIDs(self):
        self.lowercase_nodes = {}
        self.collisions = []
        for n in self.nodes:
            l = n.lower()
            if l in self.lowercase_nodes:
                self.collisions.append( [n, l, self.lowercase_nodes[l]] )
            else:
                self.lowercase_nodes[ n.lower() ] = n
    
    def lookForNode(self, nid):
        if nid in self.nodes:
            return nid
        else:
            altNid = nid[:3] + nid[3].capitalize() + nid[4:]
            if altNid not in self.nodes:
                Shash = nid.split('#') 
                altNid = Shash[0][3:] 
                
                if '+' in nid: 
                    Splus = altNid.split('+')
                    altNid = 'wn/' + '+'.join([ t.capitalize() for t in Splus ])
                
                elif altNid.count('-') > 1: 
                    Sdash = altNid.split('-')
                    altNid = 'wn/' + '-'.join( [ t.capitalize() for t in Sdash[:-1] ] + [Sdash[-1]] ) 
                
                if len(Shash) > 1: 
                    altNid = altNid + '#' + Shash[1]
                    
                if altNid not in self.nodes:
                    l = nid.lower()
                    if l in self.lowercase_nodes:
                        altNid = self.lowercase_nodes[l]
                    else:
                        self.not_found_nodes.append(nid)
                        return None
            return altNid

    def writeLogFile(self):
        log = []
        log.append('#### WordNet import log file.')
        log.append('\n#### Filters: ')
        for f in self.filters:
            log.append(f)
        log.append('\n#### Replacements: ')
        for r in self.replacements:
            log.append( r + ' : ' + self.replacements[r] )
        log.append('\n#### Node referred in relationships but not existing:')
        for n in self.not_found_nodes:
            log.append(n)
        log.append('\n#### The above nodes were referred in the following triples:')
        for r in self.rels_with_orphan_nodes:
            log.append( '<{0}> <{1}> <{2}> .'.format(r[':START_ID'], r[':END_ID'], r[':TYPE']) )
        log.append('\n#### Duplicate gloss properties:')
        for d in self.duplicate_gloss:
            log.append(d)

        self.log = log

        with open(self.logFilename, 'w') as f:
            for l in self.log:
                f.write(l + '\n')

        print(self.logFilename)


def main():
    numargs = len(sys.argv)
    w = None
    if numargs == 2:
        w = WNimporter(sys.argv[1])
    else:
        w = WNimporter()
    
    try:        
        w.retrieveWordNet()
    except Exception as e:
        print('')
        print(e.__repr__())
        print(e.message)
        print("Usage:\npython Fetch-WordNet.py <input file>\n")

if __name__ == "__main__":
    main()
