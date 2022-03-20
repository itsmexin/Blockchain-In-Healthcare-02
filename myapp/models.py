from __future__ import unicode_literals
from django.db import models

import rsa
from datetime import datetime
import pytz #(for timezone)
# Create your models here.
def gen_exist_prvkey(x):
    prvkey = x
    bracket_value = prvkey[prvkey.find("(")+1:prvkey.find(")")]
    prvkey_list = bracket_value.split(",")
    prvkey = rsa.PrivateKey(int(prvkey_list[0]),int(prvkey_list[1]),int(prvkey_list[2]),int(prvkey_list[3]),int(prvkey_list[4]))
    return prvkey

def gen_exist_pubkey(x):
    pubkey = x
    bracket_value = pubkey[pubkey.find("(")+1:pubkey.find(")")]
    pubkey_list = bracket_value.split(",")
    pubkey = rsa.PublicKey(int(pubkey_list[0]),int(pubkey_list[1]))
    return pubkey

# def block_data(prev_info, Info):
#     data_block = []
#     datetime = timestamp()
#     data_block.append(prev_info)
# #     new_block = input("Enter New Block : ")
#     data_block.append(datetime + Info)
#     data_block = " - ".join(data_block)
#     return data_block

# def generate_keys():
#     pubkey,prvkey = rsa.newkeys(2048)
#     return pubkey,prvkey

# def encryption(data, pubkey):
#     data_encrypted = rsa.encrypt(data.encode(),pubkey)
#     return data_encrypted

def timestamp():
#     datetime_now = datetime.now()
    tz_asia = pytz.timezone("Asia/Kuala_Lumpur")
    datetime_now = datetime.now(tz_asia)
    date = datetime_now.strftime("%d/%m/%Y|%H:%M")
    return date
