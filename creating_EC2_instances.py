#!/usr/bin/python
import datetime
from boto.exception import BotoServerError
import boto.ec2.connection
import sys
import os
import time
import boto
import boto.manage.cmdshell
from launching import launch
from boto.exception import BotoServerError
from cloud import stat
def launch_instance(ami='ami-3d4ff254',
    instance_type='t1.micro',
    key_name='key',
    key_extension='.pem',
    key_dir='~/',
    group_name='new-groupp',
    ssh_port=22,
    cidr='0.0.0.0/0',
    tag='paws',
    user_data=None,
    cmd_shell=False,
    login_user='ec2-user',
    ssh_passwd=None):

  ec2=boto.connect_ec2(aws_access_key_id="ABC",aws_secret_access_key="ABC")
  # Check to see if specified keypair already exists.
  # If we get an InvalidKeyPair.NotFound error back from EC2,
  # it means that it doesn't exist and we need to create it.

  try:
    print 'Check if specified keypair exists\n'
    key = ec2.get_all_key_pairs(keynames=[key_name])[0]
    print 'ff'
    
    print 'ff'
  except ec2.ResponseError, e:
    if e.code == 'InvalidKeyPair.NotFound':
      print 'Creating keypair: %s' % key_name
      key = ec2.create_key_pair(key_name)
      key.save(key_dir)
    else:
      raise
  try:
    group = ec2.get_all_security_groups(groupnames=[group_name])[0]
  except ec2.ResponseError, e:
    if e.code == 'InvalidGroup.NotFound':
      print 'Creating Security Group: %s' % group_name
      group = ec2.create_security_group(group_name,
          'A group that allows SSH access')
    else:
      raise

  #RRP
  try:
    group.authorize('tcp', ssh_port, ssh_port, cidr_ip=cidr)
  except ec2.ResponseError, e:
    if e.code == 'InvalidPermission.Duplicate':
      print 'Security Group: %s already authorized' % group_name
    else:
      raise

  #RRP
  try:
    group.authorize('icmp', cidr_ip=cidr)
  except ec2.ResponseError, e:
    if e.code == 'InvalidPermission.Duplicate':
      print 'Security Group: %s already authorized' % group_name
    else:
      raise
    
  # Now start up the instance.  The run_instances method
  reservation = ec2.run_instances(ami,
      key_name=key_name,                          
      min_count=2,
      max_count=2,                            
      security_groups=[group_name],
      instance_type=instance_type,
      user_data=user_data)
  instance1 = reservation.instances[0]
  print 'waiting for instance'
  while instance1.state != 'running':
    print '.'
    time.sleep(5)
    instance1.update()
    print 'Waiting'

  #RRP
  # Allocate an Elastic IP
  address1 = ec2.allocate_address()
  print address1.public_ip

  # Associate IP with VM
  ec2.associate_address(instance1.id, address1.public_ip)
  time.sleep(20)
  print 'Instance launched with public DNS: ',address1.public_ip
  

  instance1.add_tag(tag)
  vol1=ec2.create_volume(10,instance1.placement)
  vol1.attach(instance1.id, '/dev/sdh')
  print vol1.id
  
  instance2 = reservation.instances[1]
  print 'waiting for instance'
  while instance2.state != 'running':
    print '.'
    time.sleep(5)
    instance2.update()
    print 'Waiting'
  
  # Allocate an Elastic IP
  address2 = ec2.allocate_address()
  print address2.public_ip

  # Associate IP with VM
  ec2.associate_address(instance2.id, address2.public_ip)
  #RRP

  time.sleep(10)
  print 'Instance launched with public DNS: ',address2.public_ip
  instance2.add_tag(tag)

  vol2=ec2.create_volume(10,instance2.placement)
  vol2.attach(instance2.id, '/dev/sdh')
    
  #if cmd_shell:
  #  key_path = os.path.join(os.path.expanduser(key_dir)+
  #      key_name+key_extension)
  #  print 'Key Path: ', key_path
  #  cmd = boto.manage.cmdshell.sshclient_from_instance(instance,
  #      key_path,
  #      user_name=login_user)
    #RRP
  #  cmd.shell()
  print "Wait for 5minutes!!!!"
  time.sleep(300) 
  #return (instance, cmd)
  i1=instance1.id
  ip1=address1.public_ip
  i2=instance2.id
  ip2=address2.public_ip
  stat(instance1,i1,ip1,address1,instance2,i2,ip2,address2)
 
  

if __name__ == "__main__":
  sys.exit(launch_instance())  
