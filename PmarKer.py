#!/usr/bin/env python

import os
import json
import codecs
import ecdsa
import hashlib
import base58
import requests
import time
from smtplib import SMTP_SSL as SMTP
import logging


wif = ""



logging.basicConfig(filename='BTC_Priv_'+time.strftime("%Y-%m-%d-%H-%M")+'.csv', \
level=logging.INFO, format='%(message)s', datefmt='%Y-%m-%d,%H:%M:%S')
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("blockcypher").setLevel(logging.WARNING)
logging.info ('Timestamp, WifKey, PublicAddress')



wif = ""

def ping_address(publicAddress):
	global pk
	global wif
	global publicKey
    
	resp = requests.get("https://www.sochain.com/api/v2/get_address_balance/bitcoin/"+ publicAddress)

	if resp.ok:
		ourJSON = resp.json()
		balance = dict(ourJSON['data'])['confirmed_balance']
		print( balance )

	else:
		print(resp.text)
		raise ValueError("cannot reach block explorer for balance", resp)
	# "WifKey", "HexKey", "PublicAddress", "PublicKey", "Balance"
	#Comment out this line if you wish to NOT record blank keys
	logging.info (''+ time.strftime("%m-%d-%y %H:%M:%S") +','+ wif.decode('utf-8') +','+ publicAddress)

	if float(balance) > 0.00000000:
		logging.info (''+ time.strftime("%m-%d-%y %H:%M:%S") +','+ wif.decode('utf-8') +','+publicAddress+' ,balance '+balance)
		
		print( "Congratulations...alert the world cause you just made some sort of history friend!" )
		print(wif.decode('utf-8'))

def wif_conversion(pk):
	global wif
	padding = '80' + pk
	# print padding

	hashedVal = hashlib.sha256(padding.decode('hex')).hexdigest()
	checksum = hashlib.sha256(hashedVal.decode('hex')).hexdigest()[:8]
	# print hashedVal
	# print padding+checksum

	payload = padding + checksum
	wif = base58.b58encode(payload.decode('hex'))
	print wif


while True:

	pk = os.urandom(32).encode("hex")
	wif_conversion(pk)

	sk = ecdsa.SigningKey.from_string(pk.decode("hex"), curve = ecdsa.SECP256k1)
	vk = sk.verifying_key
	publicKey = ("\04" + vk.to_string())
	ripemd160 = hashlib.new('ripemd160')
	ripemd160.update(hashlib.sha256(publicKey).digest())
	networkAppend = '\00' + ripemd160.digest()
	checksum = hashlib.sha256(hashlib.sha256(networkAppend).digest()).digest()[:4]
	binary_address = networkAppend + checksum
	publicAddress = base58.b58encode(binary_address)
	print publicAddress
    
	while True:
		try:
			ping_address(publicAddress.decode('utf-8'))
			# probably does nothing...who knows ;)
			time.sleep(.47)	
		except ValueError:
			print( "Aaaannnnd we got Timed Out" )
			print( pk )
			print( publicAddress )
			time.sleep(3)
			continue
		except KeyError:
			print( "we may be denied or something, keep the script moving" )
			time.sleep(10)			
		break

# msg = "I own your Private Key for %s" %(publicAddress)
# signed_msg = sk.sign(msg)
# encoded_msg = signed_msg.encode("hex")
