#!python
#Reference: 'https://github.com/redsk/neo_wordnet.git'
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
        self.nodesFilename = os.path.join(self.path, 'WNnodes.csv')
        self.edgesFilename = os.path.join(self.path, 'WNedges.csv')
        self.logFilename = os.path.join(self.path, 'WNimporter.log')
        self.WN_unique_fname = self.WNfname[:-3] + '_unique' + self.WNfname[-3:]

    def convertWordNet(self):
        # Wordnet 3.1 RDF has duplicate lines. So first of all we filter them
        # we use the standard UNIX command 'sort' or open the file if it already exists
        if not os.path.isfile(self.WN_unique_fname):
            print('#### Filtering duplicated lines in', self.WNfname, ': it will take a while...',
            sys.stdout.flush())
            args = ['sort', '-us', '-o', self.WN_unique_fname, self.WNfname]
            subprocess.check_call(args)
            print('done.')

        print('#### Opening WordNet 3.1 with unique lines...',
        sys.stdout.flush())
        self.wordnetLines = self.readFile(self.WN_unique_fname)
        print('done.')

        print('#### Filtering and replacing prefixes in WordNet...',
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
                if all( [f not in e for f in self.filters for e in triple] ): # if none of the self.filters applies
                    for i in range(0, len(triple)):
                        for r in self.replacements:
                            triple[i] = triple[i].replace(r, self.replacements[r])
                    FRtriples.append(triple)
        return FRtriples


    def getTriple(self, l):
        first_space = l.find(' ')
        second_space = l.find(' ', first_space+1)
        triple = [l[0:first_space].strip(), l[first_space+1:second_space].strip(), l[second_space:-3].strip()] # removing ' .\n' at the end

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

        count = 0 
        for idx, t in enumerate(triples):
            try:
                if t[0] in ['', '\n']:
                    continue    # empty line
                if t[0].startswith('_'):
                    continue    # we ignore lists

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

                        # #CanonicalForm and #Form- nodes have only 'lemon#writtenRep' and 'w3#type' relationships
                        # As we don't create nodes for Forms, we ignore the 'w3#type' relationship that would
                        # overwrite the base node one.
                        continue
                    elif t0Sdash[1].startswith('Component-'):
                        continue    # we ignore 'Component-' nodes
                    # else:
                    #     We consider it as a normal node, e.g. 'wn/nationality-n#1-n'


                # this is the id:ID property. We don't need to set it as it's already implicitly in the dictionary as key
                nodeid = t[0]   

                if nodeid not in self.nodes:
                    self.nodes[nodeid] = {}

                n = self.nodes[nodeid] # shortcut
                id_only=nodeid.rsplit('/', 1)[-1]
                if count==100:
                  break
                
                # LABEL property
                if   t[1] == 'w3#type' and t[2] not in ['lemon#Form', 'lemon#Component']: # nodeid is set to the base component
                    count+=1

                    n[':LABEL'] = id_only
                    response = requests.get("http://wordnet-rdf.princeton.edu/json/id/"+id_only)
                    data = response.json()
                    dic = data[0]

                    defn = dic['definition']
                    lemmas = dic['lemmas']
                    word = (lemmas[0])['lemma']
                       
                    pos = (id_only.split('-'))[-1]
                    

                    n['wdo#definition'] = defn
                    n['wdo#word'] = word

                # Relationships
                elif t[1] in ['lemon#sense', 'lemon#reference', 'wdo#derivation', 'wdo#hyponym', 'wdo#hypernym', 'wdo#similar', 'wdo#antonym', \
                              'wdo#member_meronym', 'wdo#member_holonym', 'wdo#pertainym', 'wdo#also', \
                              'wdo#part_meronym','wdo#mero_part','wdo#part_holonym', 'wdo#instance_hyponym', 'wdo#instance_hypernym' \
                              'wdo#domain_member_category', 'wdo#domain_category', 'wdo#verb_group', 'wdo#domain_region', 'wdo#domain_member_region' \
                              'wdo#attribute', 'wdo#has_domain_topic','wdo#domain_usage', 'wdo#domain_member_usage', 'wdo#substance_holonym', 'wdo#substance_meronym', \
                              'wdo#entail', 'wdo#action', 'wdo#cause', 'wdo#theme', 'wdo#result', 'wdo#participle', 'wdo#agent', 'wdo#patient', \
                              'wdo#beneficiary', 'wdo#location', 'wdo#instrument', 'wdo#goal', 'wdo#creator', 'wdo#product', 'wdo#experiencer']:
                    
                    self.relationships.append( {':START_ID': nodeid, ':END_ID': t[2], ':TYPE': t[1]} )
                    

                # Reverse relationships
                elif t[1] in ['wdo#synset_member']: 
                    self.relationships.append( {':START_ID': t[2], ':END_ID': nodeid, ':TYPE': t[1]} )

                # Integer properties
                elif t[1] in ['wdo#sense_number', 'wdo#tag_count', 'wdo#lex_id']:
                    if t[1] in n:
                        print(t[1], 'already in n!', t[0], t[1], t[2])
                        break
                    if t[2] != '"None"':
                        n[ t[1] ] = int( t[2].split('^^')[0][1:-1] )  # "0"^^<http://www.w3.org/2001/XMLSchema#integer>  -> 0
                    #else:
                    #    print '\nNumeric property is None, ignoring.', t[0], t[1], t[2]

                # String properties
                elif t[1] in ['wdo#partOfSpeech']:
                    # if t[1] in n:
                    #     print(t[1], 'already in n!', t[0], t[1], t[2])
                    #     break
                    
                    pos = str(t[2])
                    pos = pos.split('#')
                    n['wdo#partOfSpeech'] = pos[1] 

                
                # IGNORED:
                #     lemon#canonicalForm : this is handled differently because we don't create a node for canonicalForm, we have an attribute in the base node
                #     lemon#writtenRep : these relationships are for CanonicalForm and Form nodes only
                #     lemon#otherForm : link to other Forms. But here Forms are properties, not nodes.
                #     wdo#sense_tag : not sure what to do with these...
                #     w3#first : used in lists for sense sentences, which we ignore.
                #     w3#rest : same
                #     lemon#decomposition : sentence decomposition, we ignore parts of sentences

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
            nodeProperties = ['id:ID', ':LABEL', 'wdo#word','wdo#definition','wdo#synset_member', 'wdo#partOfSpeech']
            headerText = ['uri', 'id', 'word','definition','synset', 'pos']
            header = '{0}\n'.format('\t'.join(headerText)) 
            f.write(header)
            
            for nodeID in self.nodes:
                n = self.nodes[nodeID] # faster to type
                print(n)
                if n:
                  l = ''
                  l += '"{0}"\t"{1}"\t'.format(nodeID, n[':LABEL'])
                  
                  if 'wdo#word' in n:
                      l += '"{0}"\t'.format(n['wdo#word'])
                  else:
                      l += '\t'
                  
                  if 'wdo#definition' in n:
                      l += '"{0}"\t'.format(n['wdo#definition'])
                  else:
                      l += '\t'

                  if 'wdo#synset_member' in n:
                      l += '"{0}"\t'.format(n['wdo#synset_member'])
                  else:
                      l += '\t'

                  if 'wdo#partOfSpeech' in n:
                      l += '"{0}"\n'.format(n['wdo#partOfSpeech'])
                  else:
                      l += '\n'
                  
                  f.write(l)

        self.rels_with_orphan_nodes = []
        with open(self.edgesFilename, 'w') as f:
            edgeProperties = [':START_ID', ':END_ID', ':TYPE']
            header = '{0}\n'.format('\t'.join(edgeProperties))
            f.write(header)
            for r in self.relationships:
              
                start_node = self.lookForNode(r[':START_ID'])
                end_node = self.lookForNode(r[':END_ID'])

                if start_node != None and end_node != None:

                    start_node = start_node.rsplit('/', 1)[-1]
                    end_node = end_node.rsplit('/', 1)[-1]
                    typeof=r[':TYPE'].split('#')
                    typeof=typeof[1]
                    rel = '"{0}"\n'.format( '"\t"'.join([start_node, end_node, typeof]) )
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
            # capitalize first letter
            # 'wn/djiboutian-a#1-a' -> 'wn/Djiboutian-a#1-a'
            altNid = nid[:3] + nid[3].capitalize() + nid[4:]
            if altNid not in self.nodes:
                Shash = nid.split('#')  # if there is a '#' suffix
                altNid = Shash[0][3:]   #'orthodox+church-n'
                
                if '+' in nid:  # 'wn/orthodox+church-n#1-n' 
                    Splus = altNid.split('+')
                    altNid = 'wn/' + '+'.join([ t.capitalize() for t in Splus ]) # 'wn/Orthodox+Church-n' 
                
                elif altNid.count('-') > 1:  # 'anglo-saxon-n'
                    Sdash = altNid.split('-')
                    altNid = 'wn/' + '-'.join( [ t.capitalize() for t in Sdash[:-1] ] + [Sdash[-1]] ) # 'wn/Anglo-Saxon-n', we don't capitalize the last 'n'
                
                if len(Shash) > 1: 
                    altNid = altNid + '#' + Shash[1] # 'wn/Orthodox+Church-n#1-n' 
                    
                if altNid not in self.nodes:
                    # let's try with a lowercase version
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
        w.convertWordNet()
    except Exception as e:
        print('')
        print(e.__repr__())
        print(e.message)
        print("Usage:\npython convertwn.py <input file>\n")

if __name__ == "__main__":
    main()
