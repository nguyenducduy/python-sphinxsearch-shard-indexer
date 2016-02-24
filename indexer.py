import subprocess
import os
import json
import sys
import smtplib
import re
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email import Encoders

gmail_user = "receiver@gmail.com"
gmail_pwd = "your_password"
gmail_rev = "sender@gmail.com"

def mail(to, subject, text):
    msg = MIMEMultipart()

    msg['From'] = gmail_user
    msg['To'] = to
    msg['Subject'] = subject

    msg.attach(MIMEText(text))

    mailServer = smtplib.SMTP("smtp.gmail.com", 587)
    mailServer.ehlo()
    mailServer.starttls()
    mailServer.ehlo()
    mailServer.login(gmail_user, gmail_pwd)
    mailServer.sendmail(gmail_user, to, msg.as_string())
    # Should be mailServer.quit(), but that crashes...
    mailServer.close()

# Sphinx Config variables
sphinxLocatePath = "/data/sphinx/"
sphinxLogPath = "/data/sphinx/searchd.log"
sphinxConfigPath = "/etc/sphinx/sphinx.conf"
executePath = "/usr/bin/"
command = executePath + "indexer --config " + sphinxConfigPath
shardPart = 8
threshold = 3500 # MB
xenforoThread = "xenforo_post"
xenforoUser = "xenforo_user"
xenforoBlank = "xenforo_post_blank"

success = []
error = {}
# First index of xenforo post source
commandIndexer = command + " " + xenforoThread + " --rotate"
proc = subprocess.Popen(commandIndexer, shell=True, stdout=subprocess.PIPE)
proc.wait()
if proc.returncode == 0:
    success.append(True)
else:
    for msg in proc.stdout:
        error[commandIndexer] = msg

# Index 8 shard of xenforo post source
for part in range(0, shardPart):
    index = format(part, '02')

    if index == "00":
        commandIndexer = command + " " + xenforoThread + " --rotate"
    else:
        commandIndexer = command + " " + xenforoThread + "_" + index + " --rotate"
    print commandIndexer
    proc = subprocess.Popen(commandIndexer, shell=True, stdout=subprocess.PIPE)
    proc.wait()
    if proc.returncode == 0:
        success.append(True)
    else:
        for msg in proc.stdout:
            error[commandIndexer] = msg

# All shard done, reset blank index
if (all(success) == True):
    commandIndexer = command + " " + xenforoBlank + " --rotate"
    proc = subprocess.Popen(commandIndexer, shell=True, stdout=subprocess.PIPE)
    proc.wait()
    if proc.returncode == 0:
        success.append(True)
    else:
        for msg in proc.stdout:
            error[commandIndexer] = msg

# Index xenforo post user
commandIndexer = command + " " + xenforoUser + " --rotate"
proc = subprocess.Popen(commandIndexer, shell=True, stdout=subprocess.PIPE)
proc.wait()
if proc.returncode == 0:
    success.append(True)
else:
    for msg in proc.stdout:
        error[commandIndexer] = msg

if (len(error) > 0):
    print ">>> Error: %r" % error
    mail(gmail_rev, "(FAILED) - SphinxSearch", "Error messages: " + json.dumbs(error))
else:
    mail(gmail_rev, "(COMPLETED) - SphinxSearch", "Index COMPLETED.")

# Check maximum limit size of index (max 4GB)
for part in range(0, shardPart):
    index = format(part, '02')

    if index == "00":
        commandIndexTool = executePath + "indextool --config " + sphinxConfigPath + " --dumpheader " + sphinxLocatePath + xenforoThread + ".sph"
    else:
        commandIndexTool = executePath + "indextool --config " + sphinxConfigPath + " --dumpheader " + sphinxLocatePath + xenforoThread + "_" + index + ".sph"

    proc = subprocess.Popen(commandIndexTool, shell=True, stdout=subprocess.PIPE)
    outputString = proc.communicate()[0]
    proc.wait()
    match = re.search('total-bytes: ([0-9]+)', outputString)
    totalBytes = match.group(1)
    # Convert bytes to megabytes
    indexSize = int(totalBytes) / 1000000
    if indexSize >= threshold:
        mail(gmail_rev, "Threshold Limited Index Size -- Five.vn SphinxSearch", commandIndexTool)
