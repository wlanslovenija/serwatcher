#!/usr/bin/python
#
# Simple script for simulating nodewatcher output on server nodes in
# order to use with the monitoring system. It should be put into cron
# to run every few minutes and redirect the output into the proper
# location.
#
# Sample netfilter configuration in use on wlan slovenia:
#
#   iptables -I FORWARD -i tap+ -o venet0 -m comment --comment "nw-iface:internet.up"
#   iptables -I FORWARD -i venet0 -o tap+ -m comment --comment "nw-iface:internet.down"
#   iptables -I FORWARD -i tap+ -o tap+ -m comment --comment "nw-iface:internal."
#   iptables -I FORWARD -i tap+ -o tun+ -m comment --comment "nw-iface:peering.up"
#   iptables -I FORWARD -i tun+ -i tap+ -m comment --comment "nw-iface:peering.down"
#
# You can of course do something completely different as long as you use
# the above comment naming.
#
import subprocess

IPTABLES_COMMENT_MARKER = 'nw-iface:'

# Fetch traffic statistics from iptables
stats = {}
process = subprocess.Popen(
  ['/sbin/iptables', '-v', '-n', '-x', '--list'],
  stdout = subprocess.PIPE,
  stderr = subprocess.PIPE
)

while True:
  line = process.stdout.readline()
  if not line:
    break

  if IPTABLES_COMMENT_MARKER not in line:
    continue

  line = line.strip().split()
  if len(line) != 11:
    continue

  try:
    int(line[0])
  except:
    continue

  bytes = int(line[1])
  comment = line[9][len(IPTABLES_COMMENT_MARKER):]
  stats[comment] = bytes

# Format and print nodewatcher output
print(";")
print("; nodewatcher monitoring system")
print(";")
print("META.version: 2")
print("META.modules.core-traffic.serial: 1")

for key, bytes in stats.iteritems():
  # Properly handle two-way interfaces (down equals up)
  if key[-1] == '.':
    key = (key + "down", key + "up")
  else:
    key = (key,)

  for iface in key:
    print("iface.{0}: {1}".format(iface, bytes))


