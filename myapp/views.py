from django.shortcuts import render, redirect

# Create your views here.
# from myapp.form import StudentForm
import rsa #for RSA
import psycopg2 #for postgresql
from datetime import datetime #for datetime
import pytz #(for timezone)
import qrcode #for qrcode
from PIL import Image
import hashlib #for sha256
from .models import gen_exist_prvkey
from .models import gen_exist_pubkey
from .models import timestamp




def login(request):
    return render(request, "login.html")

def Menu(request):
    if request.method == 'GET':
        username = request.GET.get('username')
        userpass = request.GET.get('userpass')
        conn = psycopg2.connect(
            database="d6jbrualnl8mna",
            user='ccflaniypxowwa',
            password="282ab7332a80a9ba371c9f1230c3a31c3e95d0f1ec16c60a7f754dc864866ac5",
            host='ec2-44-193-188-118.compute-1.amazonaws.com',
            port= '5432'
        )
        cursor = conn.cursor()
        hashname = hashlib.sha256(username.encode()).hexdigest()
        hashpass = hashlib.sha256(userpass.encode()).hexdigest()

        #retrieve staffpass(hashed) from staff table
        sql1 = ("SELECT staff_name FROM staff where staff_pass=%s")
        cursor.execute(sql1,(hashpass,))
        name = cursor.fetchall()
        name = [item for t in name for item in t]
        if name:
            name = name[0]
        #retrieve staffname(hashed) from staff table
        sql2 = ("SELECT staff_pass FROM staff where staff_name=%s")
        cursor.execute(sql2,(hashname,))
        password = cursor.fetchall()
        password = [item for t in password for item in t]
        if password:
            password = password[0]

        #validate password
        if hashname==name and hashpass==password:
            context={
                'username' : username,
                 'userpass' : userpass,
            }
            return render(request, "menu.html",context)
        else:
            msg="Invalid username or password !"
            context={
                'msg':msg,
            }
            return render(request, "newblock_fail.html",context)

def newblock(request):
    if request.method == 'GET' :
        username = request.GET.get('username')
        userpass = request.GET.get('userpass')

        #pass value from python to html
        context={
            'username' : username,
             'userpass' : userpass,
        }
    return render(request, "newblock.html", context)

def newblockstore(request):
    if request.method == 'GET' :
        username = request.GET.get('username')
        userpass = request.GET.get('userpass')
        name = request.GET.get('name')
        age = request.GET.get('age')
        IC = request.GET.get('IC')
        secret = request.GET.get('secret')
        secretans = request.GET.get('secretans')
        prevhash = "0"
        block = 1
        datetime = timestamp()

        #connect db
        conn = psycopg2.connect(
            database="d6jbrualnl8mna",
            user='ccflaniypxowwa',
            password="282ab7332a80a9ba371c9f1230c3a31c3e95d0f1ec16c60a7f754dc864866ac5",
            host='ec2-44-193-188-118.compute-1.amazonaws.com',
            port= '5432'
         )
        cursor = conn.cursor()

        cursor.execute('''SELECT patient_ic FROM patient''')
        DB_IC = cursor.fetchall()
        DB_IC = [item for t in DB_IC for item in t]

        ICexist = False
        for i in DB_IC:
            if IC==i:
                ICexist=True
                break
            else:
                ICexist=False

        if all(x.isalpha() or x.isspace() for x in name)!=False and age.isdigit()!=False and len(age)<=3 and IC.isdigit()!=False and len(IC)==12 and secretans != "" and ICexist==False:
            #form a block
            info_datetime = datetime + ">" + IC + ">" + name + ">" + age + ">" + secret + ">" + secretans

            #generate RSA pub,prv keys
            pubkey, prvkey = rsa.newkeys(2048)

            #hash pub,prv keys (for displaying purpose)
            hashpub = hashlib.sha256(str(pubkey).encode()).hexdigest()[:16]
            hashprv = hashlib.sha256(str(prvkey).encode()).hexdigest()[:16]

            #encrypt the block
            Enc_info = rsa.encrypt(info_datetime.encode(),pubkey)

            #retrieve staff_id from staff table
            hashname = hashlib.sha256(username.encode()).hexdigest()
            hashpass = hashlib.sha256(userpass.encode()).hexdigest()
            staffid = ("SELECT staff_id FROM staff WHERE staff_name = %s AND staff_pass = %s")
            cursor.execute(staffid,(hashname,hashpass,))
            staffid = cursor.fetchone()
            staffid = staffid[0]

            #insert block into db
            sql = "INSERT INTO patient(patient_ic,patient_block,patient_info,previous_hash,publickey,privatekey,staff_id) VALUES(%s,%s,%s,%s,%s,%s,%s)"
            cursor.execute(sql, (IC, block, Enc_info, prevhash, str(pubkey), str(prvkey), staffid))
            conn.commit()
            conn.close()

            #pass value from python to html
            context = {
                'username' : username,
                'userpass' : userpass,
                'Name' : name,
                'Age' : age,
                'IC' : IC,
                'secret' : secret,
                'secretans' : secretans,
                'hashpub' : hashpub,
                'hashprv' : hashprv,
            }
            return render(request, "newblockstore.html", context)
        elif ICexist!=False:
            msg="Patient has been registered !"
            context={
                'msg':msg,
            }
            return render(request, "newblock_fail.html",context)
        elif all(x.isalpha() or x.isspace() for x in name)==False:
            msg="Name field must be alphabet only !"
            context={
                'msg':msg,
            }
            return render(request, "newblock_fail.html",context)
        elif age.isdigit() == False and len(age)>3:
            msg="Age Field must be digit and maximum 3 numbers only !"
            context={
                'msg':msg,
            }
            return render(request, "newblock_fail.html",context)
        elif IC.isdigit() == False or len(IC) != 12:
            msg="Invalid IC !"
            context={
                'msg':msg,
            }
            return render(request, "newblock_fail.html",context)
        elif secretans == "":
            msg="Secret answer should not be blank !"
            context={
                'msg':msg,
            }
            return render(request, "newblock_fail.html",context)
        else:
            msg="Register failed ! Please check again !"
            context={
                'msg':msg,
            }
            return render(request, "newblock_fail.html",context)

def insertblock(request):
    if request.method == 'GET' :
        username = request.GET.get('username')
        userpass = request.GET.get('userpass')

        #pass value from python to html
        context={
            'username' : username,
             'userpass' : userpass,
        }
    return render(request, "insertblock.html", context)

def insertblockstore(request):
    if request.method == 'GET' :
        username = request.GET.get('username')
        userpass = request.GET.get('userpass')
        inputIC = request.GET.get('IC')
        inputpubkey = request.GET.get('pubkey')
        illness = request.GET.get('illness')
        doctor = request.GET.get('doctor')
        prescription = request.GET.get('prescription')

        if inputIC.isdigit()!=False and len(inputIC)==12 and inputpubkey!="" and illness!="" and doctor!="" and prescription!="":
            #connect db
            conn = psycopg2.connect(
                database="d6jbrualnl8mna",
                user='ccflaniypxowwa',
                password="282ab7332a80a9ba371c9f1230c3a31c3e95d0f1ec16c60a7f754dc864866ac5",
                host='ec2-44-193-188-118.compute-1.amazonaws.com',
                port= '5432'
             )
            cursor = conn.cursor()

            #retrieve all the IC from patient table
            cursor.execute('''SELECT patient_ic FROM patient''')
            ALL_IC = cursor.fetchall()
            ALL_IC = [item for t in ALL_IC for item in t] #convert list of tuples to list

            #retrieve one publickey from patient table based on patient IC
            pubkey = ("SELECT publickey FROM patient WHERE patient_ic = %s")
            cursor.execute(pubkey, (inputIC,))
            ALL_PUBKEY = cursor.fetchall()
            pubkey = ALL_PUBKEY[0][0]

            #retrieve one privatekey from patient table based on patient IC
            prvkey = ("SELECT privatekey FROM patient WHERE patient_ic = %s")
            cursor.execute(prvkey, (inputIC,))
            ALL_PRVKEY = cursor.fetchall()
            prvkey = ALL_PRVKEY[0][0]

            #hash the publickey(retrieve from db) to compare with the publickey(user input)
            hashpub = hashlib.sha256(pubkey.encode()).hexdigest()[:16]

            for i in ALL_IC:
                if inputIC==str(i) and inputpubkey==hashpub:
                    #calculation for no. of blocks that have stored in db
                    block = "select count(patient_ic) from patient where patient_ic=%s"
                    cursor.execute(block,(inputIC,))
                    block = cursor.fetchall()
                    block = block[0][0]

                    #retrieve currenthash from the latest block
                    prevhash = ("SELECT patient_info FROM patient WHERE patient_ic = %s AND patient_block = %s")
                    cursor.execute(prevhash,(inputIC,block,))
                    prevhash = cursor.fetchone()
                    prevhash = prevhash[0]
                    prevhash = bytes(prevhash)

        #           #ADD NEW BLOCK
                    datetime = timestamp()
                    info_datetime = datetime + ">" + illness + ">" + doctor + ">" + prescription
                    block += 1

        #           #ENCRYPT NEW DATA
                    pubkeyclass = gen_exist_pubkey(pubkey)
                    Enc_info =  rsa.encrypt(info_datetime.encode(),pubkeyclass)

                    #retrieve staff_id from staff table
                    hashname = hashlib.sha256(username.encode()).hexdigest()
                    hashpass = hashlib.sha256(userpass.encode()).hexdigest()
                    staffid = ("SELECT staff_id FROM staff WHERE staff_name = %s AND staff_pass = %s")
                    cursor.execute(staffid,(hashname,hashpass,))
                    staffid = cursor.fetchone()
                    staffid = staffid[0]

        #           #UPDATE DB BY ADDING NEW BLOCK
                    sql = "INSERT INTO patient(patient_ic,patient_block,patient_info,previous_hash,publickey,privatekey,staff_id) VALUES(%s,%s,%s,%s,%s,%s,%s)"
                    cursor.execute(sql, (inputIC, block, Enc_info, prevhash, pubkey, prvkey,staffid,))

                    conn.commit()
                    conn.close()

                    #pass value from python to html
                    context = {
                                'username': username,
                                'userpass': userpass,
                                'IC' : inputIC,
                                'illness' : illness,
                                'doctor' : doctor,
                                'prescription' : prescription,
                            }
                    return render(request, "insertblockstore.html", context)
        elif inputIC=="" and inputpubkey=="" and illness=="" and doctor=="" and prescription=="":
            msg="Insert failed ! Should not have blank field !"
            context={
                'msg':msg,
            }
            return render(request, "newblock_fail.html",context)
        elif inputIC.isdigit() == False or len(inputIC) != 12:
            msg="Invalid IC !"
            context={
                'msg':msg,
            }
            return render(request, "newblock_fail.html",context)
        elif inputpubkey == "":
            msg="Public key field should not be blank !"
            context={
                'msg':msg,
            }
            return render(request, "newblock_fail.html",context)
        elif illness == "":
            msg="Illness field should not be blank !"
            context={
                'msg':msg,
            }
            return render(request, "newblock_fail.html",context)
        elif doctor == "":
            msg="Doctor field should not be blank !"
            # msg="So she said, \"Hey!, how are you?\". I said, 'I am fine, thanks'."
            context={
                'msg':msg,
            }
            return render(request, "newblock_fail.html",context)
        elif prescription == "":
            msg="Prescription field should not be blank !"
            context={
                'msg':msg,
            }
            return render(request, "newblock_fail.html",context)
        else:
            msg="Insert failed ! Should not have blank field !"
            context={
                'msg':msg,
            }
            return render(request, "newblock_fail.html",context)

def updateblock(request):
    if request.method == 'GET' :
        username = request.GET.get('username')
        userpass = request.GET.get('userpass')

        #pass value from python to html
        context={
            'username' : username,
            'userpass' : userpass,
        }
    return render(request, "updateblock.html", context)

def updateblockstore(request):
    if request.method == 'GET' :
        inputIC = request.GET.get('IC')
        inputpubkey = request.GET.get('pubkey')
        illness = request.GET.get('illness')
        doctor = request.GET.get('doctor')
        prescription = request.GET.get('prescription')
        username = request.GET.get('username')
        userpass = request.GET.get('userpass')

        if inputIC.isdigit()!=False and len(inputIC)==12 and inputpubkey!="" and illness!="" and doctor!="" and prescription!="":
            conn = psycopg2.connect(
                database="d6jbrualnl8mna",
                user='ccflaniypxowwa',
                password="282ab7332a80a9ba371c9f1230c3a31c3e95d0f1ec16c60a7f754dc864866ac5",
                host='ec2-44-193-188-118.compute-1.amazonaws.com',
                port= '5432'
             )
            cursor = conn.cursor()

            #retrieve all the IC from patient table
            cursor.execute('''SELECT patient_ic FROM patient''')
            ALL_IC = cursor.fetchall()
            ALL_IC = [item for t in ALL_IC for item in t] #convert list of tuples to list

            #retrieve one publickey from patient table based on patient IC
            pubkey = ("SELECT publickey FROM patient WHERE patient_ic = %s")
            cursor.execute(pubkey, (inputIC,))
            ALL_PUBKEY = cursor.fetchall()
            pubkey = ALL_PUBKEY[0][0]

            #hash the publickey(retrieve from db) to compare with the publickey(user input)
            hashpub = hashlib.sha256(pubkey.encode()).hexdigest()[:16]

            for i in ALL_IC:
                if inputIC==str(i) and inputpubkey==hashpub:
                    #add new block
                    datetime = timestamp()
                    info_datetime = datetime + ">" + illness + ">" + doctor + ">" + prescription

                    #calculation for no. of block in db
                    block = "select count(patient_ic) from patient where patient_ic=%s"
                    cursor.execute(block,(inputIC,))
                    block = cursor.fetchall()
                    block = block[0][0]

                    #ENCRYPT NEW DATA
                    pubkey = gen_exist_pubkey(pubkey)
                    enc_data = rsa.encrypt(info_datetime.encode(),pubkey)


                    #UPDATE DB BY ADDING NEW BLOCK
                    update_value = ("UPDATE patient SET patient_info = %s WHERE patient_block = %s AND patient_ic = %s")
                    cursor.execute(update_value, (enc_data, block,inputIC,))

                    conn.commit()
                    conn.close()

                    #pass value from python to html
                    context = {
                        'username' : username,
                        'userpass' : userpass,
                        'IC' : inputIC,
                        'illness' : illness,
                        'doctor' : doctor,
                        'prescription' : prescription,
                    }
                    return render(request, "updateblockstore.html", context)
        elif inputIC=="" and inputpubkey=="" and illness=="" and doctor=="" and prescription=="":
            msg="Update failed ! Should not have blank field !"
            context={
                'msg':msg,
            }
            return render(request, "newblock_fail.html",context)
        elif inputIC.isdigit() == False or len(inputIC) != 12:
            msg="Invalid IC !"
            context={
                'msg':msg,
            }
            return render(request, "newblock_fail.html",context)
        elif inputpubkey == "":
            msg="Public key field should not be blank !"
            context={
                'msg':msg,
            }
            return render(request, "newblock_fail.html",context)
        elif illness == "":
            msg="Illness field should not be blank !"
            context={
                'msg':msg,
            }
            return render(request, "newblock_fail.html",context)
        elif doctor == "":
            msg="Doctor field should not be blank !"
            context={
                'msg':msg,
            }
            return render(request, "newblock_fail.html",context)
        elif prescription == "":
            msg="Prescription field should not be blank !"
            context={
                'msg':msg,
            }
            return render(request, "newblock_fail.html",context)
        else:
            msg="update failed ! Should not have blank field !"
            context={
                'msg':msg,
            }
            return render(request, "newblock_fail.html",context)

def viewblock(request):
    if request.method == 'GET' :
        username = request.GET.get('username')
        userpass = request.GET.get('userpass')

        #pass value from python to html
        context={
            'username' : username,
            'userpass' : userpass,
        }
        return render(request, "viewblock.html",context)
    # if request.method =="POST":
    #     inputIC = request.POST.get('IC')
    #     inputprvkey = request.POST.get('prvkey')
    #     username = request.POST.get('username')
    #     userpass = request.POST.get('userpass')

def viewprofile(request):
    if request.method == 'GET' :
        inputIC = request.GET.get('IC')
        inputprvkey = request.GET.get('prvkey')
        username = request.GET.get('username')
        userpass = request.GET.get('userpass')

        if inputIC.isdigit()!=False and len(inputIC)==12 and inputprvkey!="":
            conn = psycopg2.connect(
                database="d6jbrualnl8mna",
                user='ccflaniypxowwa',
                password="282ab7332a80a9ba371c9f1230c3a31c3e95d0f1ec16c60a7f754dc864866ac5",
                host='ec2-44-193-188-118.compute-1.amazonaws.com',
                port= '5432'
            )
            cursor = conn.cursor()

            #retrieve all the IC from patient table
            cursor.execute('''SELECT patient_ic FROM patient''')
            ALL_IC = cursor.fetchall()
            ALL_IC = [item for t in ALL_IC for item in t] #convert list of tuples to list

            #retrieve one privatekey from patient table based on patient IC
            prvkey = ("SELECT privatekey FROM patient WHERE patient_ic = %s")
            cursor.execute(prvkey, (inputIC,))
            prvkey = cursor.fetchall()
            if prvkey:
                prvkey = prvkey[0][0]
                hashprv = hashlib.sha256(prvkey.encode()).hexdigest()[:16]

            #hash the privatekey(retrieve from db) to compare with the privatekey(user input)
            checkIC = False
            for i in ALL_IC:
                if i==inputIC:
                    checkIC = True
                    break
                else:
                    checkIC = False

            # for i in ALL_IC:

            if checkIC == True and inputprvkey==hashprv:
                #convert privatekey from string type to prvkey type
                prvkey = gen_exist_prvkey(prvkey)

                #retrieve patient healthcare data
                info = ("SELECT patient_info FROM patient WHERE patient_ic = %s AND patient_block='1'")
                cursor.execute(info,(inputIC,))
                info = cursor.fetchall()
                info = info[0]

                #decrypt all the data and append into a list
                cc=0
                infodec = []
                for j in info:
                    data_decrypted = rsa.decrypt(info[cc], prvkey).decode()
                    infodec.append(data_decrypted)
                    cc+=1
                personalinfo = []
                personalinfo.append(infodec[0])

                #retrieve previous hash of first block
                prev = ("SELECT previous_hash FROM patient WHERE patient_block = '1' AND patient_ic=%s")
                cursor.execute(prev,(inputIC,))
                prev = cursor.fetchall()
                prev = [item for t in prev for item in t]
                prev = prev[0].tobytes().decode()

                #generate current block hash
                currentcipher = infodec[0]
                currenthash = hashlib.sha256(currentcipher.encode()).hexdigest()[:32]

                #generate previous block hash
                prevcipher = prev
                prevhash = hashlib.sha256(prevcipher.encode()).hexdigest()[:32]

                #split string to specific variable
                personalinfo = personalinfo[0].split(">") #output [datetime, IC, name, age]
                datetime = []
                datetime = personalinfo[0].split("|") #output [date, time]
                date = datetime[0]
                time = datetime[1]
                IC = personalinfo[1]
                patientname = personalinfo[2]
                age = personalinfo[3]

                #convert python value to html
                context = {
                    'date' : date,
                    'time' : time,
                    'IC' : IC,
                    'patient' : patientname,
                    'age' : age,
                    'currenthash':currenthash,
                    'previoushash':prevhash,
                    'username' : username,
                    'userpass' : userpass,
                    }
                return render(request, "viewprof.html", context)
            else:
                msg="Invalid IC or Private Key"
                context={
                    'msg':msg,
                }
                return render(request, "newblock_fail.html",context)
        elif inputIC=="" and inputprvkey=="":
            msg="View failed ! Should not have blank field !"
            context={
                'msg':msg,
            }
            return render(request, "newblock_fail.html",context)
        elif inputIC.isdigit() == False or len(inputIC) != 12:
            msg="Invalid IC !"
            context={
                'msg':msg,
            }
            return render(request, "newblock_fail.html",context)
        elif inputprvkey == "":
            msg="Private key field should not be blank !"
            context={
                'msg':msg,
            }
            return render(request, "newblock_fail.html",context)
        else:
            msg="View failed ! Should not have blank field !"
            context={
                'msg':msg,
            }
            return render(request, "newblock_fail.html",context)


def viewmedical(request):
    if request.method == 'GET' :
        inputIC = request.GET.get('IC')
        username = request.GET.get('username')
        userpass = request.GET.get('userpass')

        conn = psycopg2.connect(
            database="d6jbrualnl8mna",
            user='ccflaniypxowwa',
            password="282ab7332a80a9ba371c9f1230c3a31c3e95d0f1ec16c60a7f754dc864866ac5",
            host='ec2-44-193-188-118.compute-1.amazonaws.com',
            port= '5432'
        )
        cursor = conn.cursor()

        #retrieve one privatekey from patient table based on patient IC
        prvkey = ("SELECT privatekey FROM patient WHERE patient_ic = %s")
        cursor.execute(prvkey, (inputIC,))
        ALL_PRVKEY = cursor.fetchall()
        prvkey = ALL_PRVKEY[0][0]

        #convert prvkey from string type to prvkey type
        prvkey = gen_exist_prvkey(prvkey)

        # retrieve patient healthcare data
        info = ("SELECT patient_info FROM patient WHERE patient_ic = %s ORDER BY patient_block ASC")
        cursor.execute(info,(inputIC,))
        info = cursor.fetchall()
        info = [item for t in info for item in t]

        #retrieve all the previous hash based on patient IC and the time of the block stored
        prev = ("SELECT previous_hash FROM patient WHERE patient_ic=%s ORDER BY patient_block ASC")
        cursor.execute(prev,(inputIC,))
        prev = cursor.fetchall()
        prev = [item for t in prev for item in t]
        prev.pop(0)

        #decrypt all the data and append into a list
        cc=0
        infodec = []
        for j in info:
            data_decrypted = rsa.decrypt(info[cc], prvkey).decode()
            infodec.append(data_decrypted)
            cc+=1

        #retrieve patient name (for displaying at the top of page)
        pname = infodec[0].split(">")
        patientname = pname[2]
        infodec.pop(0)

        infos = []
        count = 0
        for i in infodec:
            #hash previous block
            prevcipher = rsa.decrypt(prev[count], prvkey).decode()
            prevhash = hashlib.sha256(prevcipher.encode()).hexdigest()[:32]

            #hash current block
            currenthash = hashlib.sha256(i.encode()).hexdigest()[:32]

            #split string to specific variable
            x = i.split(">")
            dt = x[0].split("|")
            dt.append(x[1])
            dt.append(x[2])
            dt.append(x[3])
            dt.append(prevhash)
            dt.append(currenthash)
            count+=1
            dt.append(count)
            infos.append(dt)

        #pass python value to html
        context = {
            'username' : username,
            'userpass' : userpass,
            'patientname' : patientname,
            'info' : infos,
        }
    return render(request, "viewmed.html", context)

def reset(request):
    if request.method == "GET":
        username = request.GET.get('username')
        userpass = request.GET.get('userpass')

        #pass python value to html
        context1 = {
            'username' : username,
            'userpass' : userpass,
        }
        return render(request, "reset.html",context1)

    elif request.method == 'POST' :
        IC = request.POST.get('IC')
        username = request.POST.get('username')
        userpass = request.POST.get('userpass')

        if IC.isdigit()!=False and len(IC)==12:
            conn = psycopg2.connect(
                database="d6jbrualnl8mna",
                user='ccflaniypxowwa',
                password="282ab7332a80a9ba371c9f1230c3a31c3e95d0f1ec16c60a7f754dc864866ac5",
                host='ec2-44-193-188-118.compute-1.amazonaws.com',
                port= '5432'
            )
            cursor = conn.cursor()

            #retrieve all the IC from patient table
            cursor.execute('''SELECT patient_ic FROM patient''')
            ALL_IC = cursor.fetchall()
            ALL_IC = [item for t in ALL_IC for item in t] #convert list of tuples to list

            #retrieve one privatekey from patient table based on patient IC
            prvkey = ("SELECT privatekey FROM patient WHERE patient_ic = %s AND patient_block='1'")
            cursor.execute(prvkey, (IC,))
            prvkey = cursor.fetchall()
            if prvkey:
                prvkey = prvkey[0][0]

            checkIC = False
            for i in ALL_IC:
                if i==IC:
                    checkIC = True
                    break
                else:
                    checkIC = False

            # genpub,genprv = rsa.newkeys(2048)
            # for i in ALL_IC:
            if checkIC == True:
                #convert prvkey from string type to prvkey type
                prvkey = gen_exist_prvkey(prvkey)

                #retrieve patient healthcare data
                info = ("SELECT patient_info FROM patient WHERE patient_ic = %s AND patient_block='1'")
                cursor.execute(info,(IC,))
                info = cursor.fetchall()
                info = [item for t in info for item in t]

                #decrypt the information
                infodec = rsa.decrypt(info[0], prvkey).decode()

                #cplit string to specific variable
                x = infodec.split(">")
                secret = x[4]
                secretans = x[5]

                #pass python value to html
                context = {
                    'username' : username,
                    'userpass' : userpass,
                    'secret' : secret,
                    'IC' : IC,
                }
                return render(request, "resetquest.html", context)
            else:
                msg="Invalid IC !!"
                context={
                    'msg':msg,
                }
                return render(request, "newblock_fail.html",context)
        elif IC=="":
            msg="Reset failed ! Should not have blank field !"
            context={
                'msg':msg,
            }
            return render(request, "newblock_fail.html",context)
        elif IC.isdigit() == False or len(IC) != 12:
            msg="Invalid IC !"
            context={
                'msg':msg,
            }
            return render(request, "newblock_fail.html",context)
        else:
            msg="Reset failed ! Should not have blank field !"
            context={
                'msg':msg,
            }
            return render(request, "newblock_fail.html",context)
def resetquestion(request):
    if request.method == 'POST' :
        IC = request.POST.get('IC')
        inputans = request.POST.get('secretans')
        username = request.POST.get('username')
        userpass = request.POST.get('userpass')

        if inputans != "":
            conn = psycopg2.connect(
                database="d6jbrualnl8mna",
                user='ccflaniypxowwa',
                password="282ab7332a80a9ba371c9f1230c3a31c3e95d0f1ec16c60a7f754dc864866ac5",
                host='ec2-44-193-188-118.compute-1.amazonaws.com',
                port= '5432'
            )
            cursor = conn.cursor()

            #retrieve privatekey from db based on patient IC
            prvkey = ("SELECT privatekey FROM patient WHERE patient_ic = %s")
            cursor.execute(prvkey, (IC,))
            ALL_PRVKEY = cursor.fetchall()
            prvkey = ALL_PRVKEY[0][0]

            #convert prikey from string type to prikey type
            prvkey = gen_exist_prvkey(prvkey)

            #generate new pub,prv keys
            genpub,genprv = rsa.newkeys(2048)
            hashpub = hashlib.sha256(str(genpub).encode()).hexdigest()[:16]
            hashprv = hashlib.sha256(str(genprv).encode()).hexdigest()[:16]

            # retrieve patient healthcare data
            info = ("SELECT patient_info FROM patient WHERE patient_ic = %s ORDER BY patient_block ASC")
            cursor.execute(info,(IC,))
            info = cursor.fetchall()
            info = [item for t in info for item in t]

            #decrypt all the infos of one patient
            cc=0
            infodec = []
            for j in info:
                data_decrypted = rsa.decrypt(info[cc], prvkey).decode()
                infodec.append(data_decrypted)
                cc+=1

            #get secret question and secret answer from db
            x = infodec[0].split(">")
            secret = x[4]
            secretans = x[5]

            #pass python value to html
            context = {
                'username' : username,
                'userpass' : userpass,
                'IC' : IC,
                'hashpub' : hashpub,
                'hashprv' : hashprv,
            }

            #compare input secret ans with secret ans from db
            if inputans == secretans:
                #retrieve all the staff_id from patient table based on IC and the time of the block stored
                staffid = ("SELECT staff_id FROM patient WHERE patient_ic = %s ORDER BY patient_block ASC")
                cursor.execute(staffid,(IC,))
                staffid = cursor.fetchall()
                staffid = [item for t in staffid for item in t]

                #delete all the record in the patient table based on patient IC
                query = "DELETE FROM patient WHERE patient_ic IN (SELECT patient_ic FROM patient WHERE patient_ic = %s)"
                cursor.execute(query,(IC,))
                conn.commit()

                #store the first block into db
                block=1
                prevhash = "0"
                Enc_info =  rsa.encrypt(infodec[0].encode(),genpub)
                sql = "INSERT INTO patient(patient_ic,patient_block,patient_info,previous_hash,publickey,privatekey,staff_id) VALUES(%s,%s,%s,%s,%s,%s,%s)"
                cursor.execute(sql, (IC, block, Enc_info, prevhash, str(genpub),str(genprv),staffid[0]))
                conn.commit()

                #remove first element in list
                infodec.pop(0)
                staffid.pop(0)

                count=0
                for i in infodec:
                    #retrieve prevhash
                    prevhash = ("SELECT patient_info FROM patient WHERE patient_ic = %s AND patient_block = %s")
                    cursor.execute(prevhash,(IC,block,))
                    prevhash = cursor.fetchone()
                    prevhash = prevhash[0]
                    prevhash = bytes(prevhash)

                    #store the following block into db
                    block +=1
                    Enc_info =  rsa.encrypt(i.encode(),genpub)
                    sql = "INSERT INTO patient(patient_ic,patient_block,patient_info,previous_hash,publickey,privatekey,staff_id) VALUES(%s,%s,%s,%s,%s,%s,%s)"
                    cursor.execute(sql, (IC, block, Enc_info, prevhash, str(genpub),str(genprv),staffid[count],))
                    count+=1
                    conn.commit()
                conn.close()

                return render(request, "resetresult.html", context)
            else:
                msg="Incorrect Secret Answer! Please try again !"
                context={
                    'msg':msg,
                }
                return render(request, "newblock_fail.html",context)
        elif inputans=="":
            msg="Reset failed ! Secret Answer should not be blank !"
            context={
                'msg':msg,
            }
            return render(request, "newblock_fail.html",context)
    return render(request, "resetquest.html",context)

# def resetresult(request):
#     return render(request, "resetresult.html")
# def Display_DB(request):
#     if request.method == 'GET' :
#         username = request.GET.get('username')
#         pass1 = request.GET.get('pass')
#         IC = request.GET.get('IC')
#         Name = request.GET.get('Name')
#         Age = request.GET.get('Age')
#         Info = request.GET.get('Info')
        # context = {
        #     'username' : username,
        #     'pass' : pass1,
#             'IC' : IC,
#             'Name' : Name,
#             'Age' : Age,
#             'Info' : Info,
        # }
#         conn = psycopg2.connect(
#             database="d6jbrualnl8mna",
#             user='ccflaniypxowwa',
#             password="282ab7332a80a9ba371c9f1230c3a31c3e95d0f1ec16c60a7f754dc864866ac5",
#             host='ec2-44-193-188-118.compute-1.amazonaws.com',
#             port= '5432'
#          )
#         cursor = conn.cursor()
#         sql = "INSERT INTO test(username,pass) VALUES(%s,%s)"
#         cursor.execute(sql, (username,pass1))
#         conn.commit()
#         conn.close()
        # return render(request, "Disp_DB.html", context)


# def num_form(request):
#     return render(request, "num_form.html")

# def add_num(request):
#     if request.method == 'GET':
#         num1 = request.GET.get('num1')
#         num2 = request.GET.get('num2')
#         tot = int(num1) + int(num2)

#         context = {
#             'num1': num1,
#             'num2': num2,
#             'tot': tot,
#         }
#     return render(request, "dispnum.html", context)
