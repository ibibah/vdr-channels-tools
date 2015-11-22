
#!/usr/bin/python

import argparse
from collections import defaultdict
import os

class Channels:
  def __init__(self, channelString):
    self.m_ok = False;
    self.name = ""
    self.bouquet = ""
    self.name_bouquet = ""
    self.frequency = ""
    self.parameter = ""
    self.source = ""
    self.SRate = ""
    self.VPID = ""
    self.APID = ""
    self.TPID = ""
    self.CA = ""
    self.SID = ""
    self.NID = ""
    self.TID = ""
    self.RID = ""
    self.parse(channelString)

  def parse(self, channelString):
    # on split la string avec comme separateur ':'
    donnees = channelString.rstrip('\n\r').split(":")
    # test du nombre de champs trouve
    if len(donnees) == 13:
      self.name_bouquet = donnees[0]

      nameItems = self.name_bouquet.split(";")
      self.name = nameItems[0]
      if len(nameItems) == 2:
        self.bouquet = nameItems[1]

      self.frequency = donnees[1]
      self.parameter = donnees[2]

      if self.parameter[-1:] == "1":
        self.DVBS = "DVBS2"
      else:
        self.DVBS = "DVBS"

      self.source = donnees[3]
      self.SRate = donnees[4]
      self.VPID = donnees[5]
      self.APID = donnees[6]
      self.TPID = donnees[7]
      self.CA = donnees[8]
      self.SID = donnees[9]
      self.NID = donnees[10]
      self.TID = donnees[11]
      self.RID = donnees[12]
      self.m_ok = True

  def IsSameChannelWithNameAndDVBS(self, other):
   if isinstance(other, Channels):
        return ( (self.name == other.name) or
                 (self.name == other.name + " HD" ) or
                 (self.name + " HD" == other.name )  and
                 ( self.DVBS == other.DVBS) )

  def IsSameChannelWithFreqAndSID(self, other):
   if isinstance(other, Channels):
        return ( ( self.frequency == other.frequency) and
                 ( self.SID == other.SID ) )

  def isOk(self):
    return self.m_ok


  def __eq__(self, other):
    if isinstance(other, Channels):
        #operateur de comparaison
        return ( ( self.IsSameChannelWithNameAndDVBS(other) == True ) and
                 ( self.frequency == other.frequency ) and
                 ( self.SID == other.SID) )
    else:
        return NotImplemented

  def  __str__(self):
    return  self.name_bouquet + ':' + self.frequency + ':' + self.parameter + ':' + self.source + ':' + self.SRate + ':' + self.VPID + ':' + self.APID + ':' + self.TPID + ':' + self.CA + ':' + self.SID + ':' + self.NID + ':' + self.TID + ':' + self.RID + '('+ self.DVBS + ')'


def process(srcref, srcScan): #, dst):

  ChannelsScanList = list()
  ChannelsRefList = list()
  ChannelsCSatKingOfSatList = list()

  # lecture du fichier scan
  for scanLigne in srcScan:
    Chan = Channels(scanLigne)
    if Chan.isOk():
        ChannelsScanList.append(Chan)
    #else:
    #    print "rejet de la ligne " + scanLigne

  # lecture du fichier ref
  for refLigne in srcref:
    Chan = Channels(refLigne)
    if Chan.isOk():
        ChannelsRefList.append(Chan)
    #else:
    #    print "rejet de la ligne " + refLigne

  # lecture de la sortie KingOfSat
  outputKos = os.popen("python get-canalsat-channels-king-of-sat.py --list 19.2E --bouquet CanalSat", "r").read()
  donnees = outputKos.split('\n')
  for kofLigne in donnees:
    Chan = Channels(kofLigne)
    if Chan.isOk():
        ChannelsCSatKingOfSatList.append(Chan)
    #else:
    #    print "rejet de la ligne " + kofLigne
  
  print '------- channels with no problems are not listed ------------'
  print '------- channels with suspicion of problems :' 
  #pour chaque ligne du fichier source
  for chaRef in ChannelsRefList:

    # si le fichier scan a au moins une ref de la chaine
    results_scan = [ x for x in ChannelsScanList if x.IsSameChannelWithNameAndDVBS(chaRef) == True ]

    # recherche des reference dans kingofsat
    results_kof = [ x for x in ChannelsCSatKingOfSatList if x.IsSameChannelWithFreqAndSID(chaRef) == True ]

    # creation des variables contenant le message
    messageheader = 'cha   :' + chaRef.__str__()
    message = ""
    idemScan = False
    idemKof = False
    
    # O correspondances dans scan
    if len(results_scan) == 0:
      messageheader += '( not found in scan !! )'

    # 1 correspondance dans le scan
    elif len(results_scan) == 1:
      # si les chaines sont differentes
      if not(results_scan[0] == chaRef):
        messageheader += ' ( channel != scan )'
        message += '-scan :' + results_scan[0].__str__() + ' ( update from scan ?)'
      else:
      # les chaines sont identiques
        idemScan = True
        messageheader += '  ( channel = scan )'
    
    # plusieurs correspondances dans le scan
    elif len(results_scan) > 1:
      correspondance = ""
      # affichage des correspondances
      for c in results_scan:
        # on affiche pas la correspondance qui est identique a la chaine
        if not(c == chaRef):
            if correspondance != "":
		correspondance += '\n'
            correspondance += '-scan :' + c.__str__()

      if correspondance != "":
         messageheader += ' ( multiples scan )'
         message += correspondance
      else:
         messageheader += ' ( multiples scan but correspondances are empty ???? )'
    
    # 0 correspondance dans kof
    if len(results_kof) == 0:
        messageheader += '( not found in kof !!)'

    # 1 correspondance dans kof
    elif len(results_kof) == 1:
        # la chaine est differente de king of sat
	if not( results_kof[0] == chaRef ):
                messageheader += ' ( channel != kof )'
		message += '-kof  :' + results_kof[0].__str__() + ' ( update from kof ? )'
        # la chaine est identique a king of sat
        else:
      		idemKof = True
                messageheader += ' ( channel = kof )'

    # plusieurs correspondances dans kof
    elif len(results_kof) > 1:
        correspondance = ""
        # on affiche la liste des correspondances
        for c in results_kof:
            if correspondance != "":
		correspondance += '\n'
            correspondance += '-kof  :' + c.__str__()

        if correspondance != "":
             messageheader += ' ( multiples kof )'
             message += correspondance
        else:
             messageheader += ' ( multiples kof but correspondances are empty ???? )'

    if ( idemKof == False ):
    	print messageheader
    	if message != "": 
    	    print message

  # affichage de toutes les chaines qui ne sont pas dans le fichier de reference mais dans king of sat et dans le scan
  newChannels = [item for item in ChannelsScanList if ( (item not in ChannelsRefList) and (item in ChannelsCSatKingOfSatList) and (item in ChannelsScanList ) )]

  print '--------- new channels ( not in channels.conf but in scan and King Of Sat )'
  for c in newChannels:
    print 'new   :' + c.__str__()

if ( __name__ == "__main__"):
  parser = argparse.ArgumentParser(description='maj de channel.conf avec un channels.conf issue de wscan')
  parser.add_argument('-c','--channels', help='vdr channels.conf',required=True)
  parser.add_argument('-s','--scan', help='Input channels.conf of wscan',required=True)
  #parser.add_argument('-o','--output', help='output channels.conf',required=True)
  args = parser.parse_args()


  # Ouverture du fichier source
  sourceRef = open(args.channels, "r")
  sourceScan = open(args.scan, "r")

  # Ouverture du fichier destination
  #destination = open(args.output, "w")

  try:
      # Appeler la fonction de traitement
      process(sourceRef, sourceScan ) #, destination)
  finally:
      #destination.close()
      sourceRef.close()
      sourceScan.close()
