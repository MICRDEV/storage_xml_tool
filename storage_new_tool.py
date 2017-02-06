from Crypto.Cipher import AES
from Crypto.Hash import SHA256
import argparse
import sys
from base64 import b64encode, b64decode
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape as xml_escape
from xml.sax.saxutils import unescape as xml_unescape

fromstrnew = ''
tostrnew = ''
def makekeycipher(key):
    hashedkey= SHA256.new(key).digest()

    return AES.new(hashedkey, AES.MODE_ECB)

def makevalcipher(key):
    hashedkey= SHA256.new(key).digest()

    return AES.new(hashedkey, AES.MODE_CBC, "fldsjfodasjifuds")


""" ====================================================================== """
def parse_xml(xml):
    """ convert xml to config dict """

    d={}
    root= ET.fromstring(xml)
    # root.tag=="map"
    for line in list(root):
        # line.tag=="string"
        k= line.attrib["name"]
        v= line.text
        d[k]= v

    return d

def create_xml(cfg):
    """ convert config dict to xml """
    xml= "<?xml version='1.0' encoding='utf-8' standalone='yes' ?>\n"
    xml += "<map>\n"
    for k,v in cfg.items():
        xml += "    <string name=\"%s\">%s</string>\n" % (xml_escape(k), xml_escape(v))
    xml += "</map>\n"

    return xml

""" ====================================================================== """
def pkcs5_pad(s):
    BLOCK_SIZE= 16
    return s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)

def pkcs5_unpad(s):
    return s[0:-ord(s[-1])]
 

""" ====================================================================== """
def decrypt(value, cipher):
    return pkcs5_unpad(cipher.decrypt(b64decode(value)))
def encrypt(value, cipher):
    return b64encode(cipher.encrypt(pkcs5_pad(value)))

""" ====================================================================== """
def decode_xml(xml, key):
    """ decrypted xml config to config dict """
    enc= parse_xml(xml)
    if key is None:
        return enc

    dec= {}

    keycipher= makekeycipher(key)
    for k, v in enc.items():
        valcipher= makevalcipher(key)
        dec[decrypt(k, keycipher)]= decrypt(v, valcipher)

    return dec

def encode_xml(cfg, key):
    """ convert config dict to encrypted xml """
    if key is None:
        return create_xml(cfg)

    enc= {}

    keycipher= makekeycipher(key)
    for k, v in cfg.items():
        valcipher= makevalcipher(key)
        enc[encrypt(k, keycipher)]= encrypt(v, valcipher)

    return create_xml(enc)


""" ====================================================================== """
def handle_fh(fh, args):
    xml= fh.read()
    cfg= decode_xml(xml, fromstrnew)
    print encode_xml(cfg, tostrnew)

def handle_xmlfile(fn, args):
    with open(fn) as fh:
        handle_fh(fh, args)

""" ====================================================================== """
parser = argparse.ArgumentParser(description='Clash-of-Clans configuration editor')
parser.add_argument("--from", dest='from_', type=str, help="source android_id")
parser.add_argument("--to", type=str, help="target android_id")
parser.add_argument("xmlfiles", type=str, metavar="XML", nargs="*", help="a xml config file")

args = parser.parse_args()

if args.from_ == 'CR':
    fromstrnew = '3;G39;A:<N6MI9726MM<AGE35'
elif args.from_ == 'HD':
    fromstrnew = '0HMDC=MI9726MM<AGE35'
else:
    fromstrnew = None

if args.to == 'CR':
    tostrnew = '3;G39;A:<N6MI9726MM<AGE35'
elif args.to == 'HD':
    tostrnew = '0HMDC=MI9726MM<AGE35'
else:
    tostrnew = None

if not args.xmlfiles:
    handle_fh(sys.stdin, args)
else:
    for fn in args.xmlfiles:
        handle_xmlfile(fn, args)

