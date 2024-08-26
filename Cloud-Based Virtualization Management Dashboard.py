import boto3
import threading
import time
from flask import Flask, render_template, jsonify

app = Flask(__name__)

# AWS EC2 client
ec2 = boto3.client('ec2', region_name='us-west-2')

# Function to manage EC2 instances
def manage_instance(action, instance_id):
    if action == 'start':
        ec2.start_instances(InstanceIds=[instance_id])
    elif action == 'stop':
        ec2.stop_instances(InstanceIds=[instance_id])
    elif action == 'reboot':
        ec2.reboot_instances(InstanceIds=[instance_id])

# Background task to check VM status
def check_vm_status():
    while True:
        instances = ec2.describe_instances()['Reservations']
        for reservation in instances:
            for instance in reservation['Instances']:
                print(f"Instance {instance['InstanceId']} status: {instance['State']['Name']}")
        
        time.sleep(60)  # Check every minute

# Flask route for VM dashboard
@app.route('/')
def index():
    instances = ec2.describe_instances()['Reservations']
    return render_template('index.html', instances=instances)

# Route to handle VM actions (start, stop, reboot)
@app.route('/manage_vm/<action>/<instance_id>')
def manage_vm(action, instance_id):
    threading.Thread(target=manage_instance, args=(action, instance_id)).start()
    return jsonify({'message': f'Action {action} initiated on instance {instance_id}'}), 200

if __name__ == '__main__':
    threading.Thread(target=check_vm_status).start()  # Start background VM status check
    app.run(debug=True)
