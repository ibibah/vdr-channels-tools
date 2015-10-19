
#!/usr/bin/python

import argparse
from collections import defaultdict

class Channels:
  def __init__(self, channelString):
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
    donnees = channelString.rstrip('\n\r').split(":")
    if len(donnees) != 13:
      print 'erreur'
    else:
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

  def __eq__(self, other):
    if isinstance(other, Channels):
        return ( (self.name_bouquet == other.name_bouquet) and 
                 (self.frequency == other.frequency) and
                 (self.parameter == other.parameter) and
                 (self.source == other.source) and
                 (self.SRate == other.SRate) )
    else:
        return NotImplemented
  
  def  __str__(self):
    return  self.name_bouquet + ':' + self.frequency + ':' + self.parameter + ':' + self.source + ':' + self.SRate + ':' + self.VPID + ':' + self.APID + ':' + self.TPID + ':' + self.CA + ':' + self.SID + ':' + self.NID + ':' + self.TID + ':' + self.RID + '('+ self.DVBS + ')' 
  

def process(srcref, srcScan, dst):
  
  ChannelsScanList = list()
  ChannelsRefList = list()
  
  # lecture du fichier scan
  for scanLigne in srcScan:
    Chan = Channels(scanLigne)
    ChannelsScanList.append(Chan)

  # lecture du fichier ref
  for refLigne in srcref:
    Chan = Channels(refLigne)
    ChannelsRefList.append(Chan)
  
  #pour chaque ligne du fichier source
  for chaRef in ChannelsRefList:

    # si le fichier scan a au moins une ref de la chaine
    results = [ x for x in ChannelsScanList if x == chaRef ]
    
    if len(results) == 1:
      # on compare les chaines
      if not(results[0] == chaRef):
        print chaRef.name_bouquet + ' modifie'
        print 'ref ' + chaRef.__str__() 
        print '->  ' + results[0].__str__()
      else:
        print chaRef.name_bouquet + ' identique'
    elif len(results) > 1:
      print chaRef.name_bouquet + ' a plusieurs  correspondance dans scan :'
      print 'ref ' + chaRef.__str__() 
      for c in results:
        print '->  ' + c.__str__()
  
  # affichage de toutes les chaines qui ne sont pas dans le fichier de reference
  newChannels = [item for item in ChannelsScanList if ((item not in ChannelsRefList) and ( (item.bouquet == "CSAT")))]
  
  for c in newChannels:
    print 'new   ' + c.__str__()

if ( __name__ == "__main__"):
  parser = argparse.ArgumentParser(description='maj de channel.conf avec un channels.conf issue de wscan') 
  parser.add_argument('-c','--channels', help='vdr channels.conf',required=True)
  parser.add_argument('-s','--scan', help='Input channels.conf of wscan',required=True)
  parser.add_argument('-o','--output', help='output channels.conf',required=True)
  args = parser.parse_args()
  
  
  # Ouverture du fichier source
  sourceRef = open(args.channels, "r")
  sourceScan = open(args.scan, "r")
  
  # Ouverture du fichier destination
  destination = open(args.output, "w")
    
  try:
      # Appeler la fonction de traitement
      process(sourceRef, sourceScan, destination)
  finally:
      destination.close()
      sourceRef.close()
      sourceScan.close()
