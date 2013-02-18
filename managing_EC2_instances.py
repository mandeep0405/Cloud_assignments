import datetime
import os
import sys
from launching import launch
from boto.exception import BotoServerError
import boto
import boto.ec2.connection
import time
class Error(Exception):
    pass

class InstanceDimension(dict):
    def __init__(self, name, value):
        self[name] = value

def stat(instance1,i1,ip1,address1,instance2,i2,ip2,address2):
#def stat():    

        ec2=boto.connect_ec2(aws_access_key_id="xyz",aws_secret_access_key="abc")        
        c = boto.connect_cloudwatch(AWS_ACCESS_KEY, AWS_SECRET_KEY)
        end   = datetime.datetime.utcnow()
        start = end - datetime.timedelta(minutes=10)
        print" Monitoring instance1"
        print instance1.id
        stats1 = c.get_metric_statistics(
            60, 
            start, 
            end, 
            'CPUUtilization', 
            'AWS/EC2', 
            'Average',
            { 'InstanceId': i1}
           # InstanceDimension('InstanceId', i1)
        )
        print stats1
        var=stats1[0]
        print var['Average']
        if var['Average']>20:
            print "No need for image"
            done1=0
        else:
            
            instanceID1=i1
            print instanceID1
            ec2.disassociate_address(ip1)
            Eip1=ip1
            print Eip1
            ami_name="Assignment2_AMI"+instanceID1
            print 'AMI : ', ami_name
            amiID1 = ec2.create_image(instanceID1, name=ami_name, description="Saved AMI for Assignment 2 of Cloud")
            print amiID1
            ami=unicode(amiID1)
            print "terminating instance 1"
            #ec2.terminate_instances(instance_ids=instanceID1)
      
            time.sleep(60)
            launch(ami=ami, instance_type='t1.micro', key_name='key',key_extension='.pem', key_dir='~/', group_name='new-groupp',ssh_port=22,    cidr='0.0.0.0/0', tag='paws',user_data=None,cmd_shell=False,login_user='ec2-user',  ssh_passwd=None , address=Eip1)
            done1=1 
            instance1.terminate()
            
        print "Monitoring Instance 2"
        print instance2.id
        stats2 = c.get_metric_statistics(
            60, 
            start, 
            end, 
            'CPUUtilization', 
            'AWS/EC2', 
            'Average',
            { 'InstanceId': i2}
        )
        print stats2
        var=stats2[0]
        print var['Average']
        if var['Average']>20:
            print "No need for image"
            done2=0
        else:
            instanceID2=i2
            ec2.disassociate_address(ip2)
            Eip2=ip2
            ami_name="Assignment2_AMI"+instanceID2
            print 'AMI : ', ami_name
            amiID2 = ec2.create_image(instanceID2, name=ami_name, description="Saved AMI for Assignment 2 of Cloud") 
            print "terminating instance 2"
            #ec2.terminate_instances(instance_ids=instanceID2)
          
            time.sleep(60) 
            launch(ami=amiID2,instance_type='t1.micro', key_name='key',key_extension='.pem', key_dir='~/', group_name='new-groupp',ssh_port=22,    cidr='0.0.0.0/0', tag='paws',user_data=None,cmd_shell=True,    login_user='ec2-user',  ssh_passwd=None ,address=Eip2)
            instance2.terminate()
            done2=1
        
        if done1==0 or done2==0:
            print "5pm so shutting down everything "
            if done1==0:
                instanceID1=i1
                print instanceID1
                ec2.disassociate_address(ip1)
                Eip1=ip1
                print Eip1
                ami_name="Assignment2_AMI"+instanceID1
                print 'AMI : ', ami_name
                amiID1 = ec2.create_image(instanceID1, name=ami_name, description="Saved AMI for Assignment 2 of Cloud")
                print amiID1
                ami=unicode(amiID1)
                print "terminating instance 1"
                #ec2.terminate_instances(instance_ids=instanceID1)
                
                time.sleep(60)
                
                launch(ami=ami, instance_type='t1.micro', key_name='key',key_extension='.pem', key_dir='~/', group_name='new-groupp',ssh_port=22,    cidr='0.0.0.0/0', tag='paws',user_data=None,cmd_shell=False,login_user='ec2-user',  ssh_passwd=None , address=Eip1)
                instance1.terminate()
                
            elif done2==0:
                instanceID2=i2
                ec2.disassociate_address(ip2)
                Eip2=ip2
                ami_name="Assignment2_AMI"+instanceID2
                print 'AMI : ', ami_name
                amiID2 = ec2.create_image(instanceID2, name=ami_name, description="Saved AMI for Assignment 2 of Cloud") 
                print "terminating instance 2"
                #ec2.terminate_instances(instance_ids=instanceID2)
                
                time.sleep(60)
                
                
                launch(ami=amiID2,instance_type='t1.micro', key_name='key',key_extension='.pem', key_dir='~/', group_name='new-groupp',ssh_port=22,    cidr='0.0.0.0/0', tag='paws',user_data=None,cmd_shell=True,    login_user='ec2-user',  ssh_passwd=None ,address=Eip2)
                instance2.terminate()
            else:
                print "bazinga"
        else:
            print "already terminated"


                
                
