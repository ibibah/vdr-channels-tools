
#!/usr/bin/python

import xml.sax
import argparse


ChannelIds = {}

class ChannelHandler( xml.sax.ContentHandler ):
  def __init__(self):
    self.CurrentData = ""
    self.ChannelId = ""
  
  # Call when an element starts
  def startElement(self, tag, attributes):
    self.CurrentData = tag
    if tag == "channel":
        self.ChannelId = attributes["id"]
  
  # Call when an elements ends
  def endElement(self, tag):
    self.CurrentData = ""
  
  # Call when a character is read
  def characters(self, content):
    if self.CurrentData == "display-name":
      ChannelIds[content] = self.ChannelId 

def process(src, dst):

  for ligne in src:
    donnees = ligne.rstrip('\n\r').split(":")
    channelName = donnees[0].split(";")[0]
    if ChannelIds.has_key(channelName):
      chanId = ChannelIds[channelName]
      dst.write("%s:%s\n" %(ligne.rstrip('\n\r'), chanId ))
      print channelName + ' updated'
    else:
      print channelName + ' not found'
        
if ( __name__ == "__main__"):
  parser = argparse.ArgumentParser(description='ajout des channelsId xmlttv dans channels.conf') 
  parser.add_argument('-c','--channels', help='Input channels.conf',required=True)
  parser.add_argument('-x','--xmltv', help='Input channels.xml',required=True)
  parser.add_argument('-o','--output', help='Output channels.conf',required=True)
  args = parser.parse_args()
  
  # create an XMLReader
  parser = xml.sax.make_parser()
  # turn off namespaces
  parser.setFeature(xml.sax.handler.feature_namespaces, 0)
  
  # override the default ContextHandler
  Handler = ChannelHandler()
  parser.setContentHandler( Handler )
  
  parser.parse(args.xmltv)
  
  # Ouverture du fichier source
  source = open(args.channels, "r")
    
  # Ouverture du fichier destination
  destination = open(args.output, "w")
    
  try:
      # Appeler la fonction de traitement
      process(source, destination)
  finally:
      # Fermeture du fichier destination
      destination.close()
    
      # Fermerture du fichier source
      source.close()
