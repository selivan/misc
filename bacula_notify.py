#!/usr/bin/python2.6

# Simple script to send Bacula reports to Zabbix
# Made by Pavel Selivanov <selivan5@yandex.ru>
# Should be used in Bacula-dir config instead of mail command:
#       mail = <> = all, !skipped
#       mailcommand = "/etc/zabbix/bacula_notify.py %r %c"
#       operatorcommand = "/etc/zabbix/bacula_notify.py %r <bacula-sd server name>"
# Hostnames in Zabbix and Bacula must correspond

import sys, re, subprocess
import datetime

if len(sys.argv) < 3:
        print "Usage:"
        print sys.argv[0], " ZABBIX_SERVER HOSTNAME [CUSTOM_MESSAGE]"
        quit(1)

# some logging
now=datetime.datetime.today()
log=sys.stdout # open('/var/log/bacula/notify_log', 'a')
log.write('--------------------------------------\n')
log.write(now.isoformat() + '\n')
log.write('sys.argv: ')
for str in sys.argv:
    log.write(str + ' ')
log.write('\n')

# settings
zabbix_sender = "/usr/bin/zabbix_sender"
zabbix_server=sys.argv[1]
hostname=sys.argv[2]
if len(sys.argv) >= 4:
        custom_message = sys.argv[3]
else:
        custom_message = False

# define how to get values from input
tests = (
        ("\s*Termination:\s*\**\s+Backup\s+(.*)\s*\**\s*",
        "bacula.backup.result",
        lambda x:  x.group(1) == "OK" and '0' or x.group(1) == "OK -- with warnings" and '1' or '2'),

        ("\s*Termination:\s+Verify\s+(.*)\s",
        "bacula.verify.result",
        lambda x: x.group(1) == "OK" and '0' or '2'),

        ("\s*FD Files Written:\s+([0-9]+)\s*",
        "bacula.fd.fileswritten",
        lambda x: x.group(1)),

        ("\s*SD Files Written:\s+([0-9]+)\s*",
        "bacula.sd.fileswritten",
        lambda x: x.group(1)),

        ("\s*FD Bytes Written:\s+([0-9][,0-9]*)\s+\(.*\)\s*",
        "bacula.fd.byteswritten",
        lambda x: x.group(1).translate(None,",")),

        ("\s*SD Bytes Written:\s+([0-9][,0-9]*)\.*",
        "bacula.sd.byteswritten",
        lambda x: x.group(1).translate(None,",")),

        ("\s*Last Volume Bytes:\s+([0-9][,0-9]*).*",
        "bacula.lastvolumebytes",
        lambda x: x.group(1).translate(None,",")),

        ("\s*Files Examined:\s+([0-9][,0-9]*)\s*",
        "bacula.verify.filesexamined",
        lambda x: x.group(1).translate(None,","))
        )

# process input and send results to zabbix
if custom_message:
        command = "%(zabbix_sender)s -z %(zabbix_server)s -s %(hostname)s -k 'bacula.custommessage' -o '%(custom_message)s'" % vars()
        log.write(command + '\n')
        subprocess.call (command, shell=True)
else:
        for line in sys.stdin.readlines():
                log.write(line)
                for regexp, key, value in tests:
                        match = re.match(regexp, line);
                        if match:
                                command = "%(zabbix_sender)s -z %(zabbix_server)s -s %(hostname)s -k '%(key)s' -o '%%s'" % vars()
                                log.write(command % value(match) + '\n')
                                subprocess.call (command % value(match), shell=True)
log.close()

