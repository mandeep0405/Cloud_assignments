#!/usr/bin/python
import sys
import os
import time
import boto
import boto.manage.cmdshell

def launch(ami,
    instance_type,
    key_name,
    key_extension,
    key_dir,
    group_name,
    ssh_port,
    cidr,
    tag,
    user_data,
    cmd_shell,
    login_user,
    ssh_passwd,
    address):

  ec2=boto.connect_ec2(aws_access_key_id="abc",aws_secret_access_key="abc")
  # Check to see if specified keypair already exists.
  # If we get an InvalidKeyPair.NotFound error back from EC2,
  # it means that it doesn't exist and we need to create it.

  try:
    print 'Check if specified keypair exists\n'
    key = ec2.get_all_key_pairs(keynames=[key_name])[0]

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
      min_count=1,
      max_count=1,                            
      security_groups=[group_name],
      instance_type=instance_type,
      user_data=user_data)
  print "sdf"
  instance1 = reservation.instances[0]
  print 'waiting for instance'
  while instance1.state != 'running':
    print '.'
    time.sleep(5)
    instance1.update()
    print 'Waiting'
  
  # Associate IP with VM
  ec2.associate_address(instance1.id, address) 
  #RRP
  print 'Instance launched with public DNS: ',instance1.public_dns_name
  time.sleep(60)

  instance1.add_tag(tag)
  
  
  
  
    
  #if cmd_shell:
  #  key_path = os.path.join(os.path.expanduser(key_dir)+
  #      key_name+key_extension)
  #  print 'Key Path: ', key_path
  #  cmd = boto.manage.cmdshell.sshclient_from_instance(instance,
  #      key_path,
  #      user_name=login_user)
    #RRP
  #  cmd.shell()

  #return (instance, cmd)
  
  

