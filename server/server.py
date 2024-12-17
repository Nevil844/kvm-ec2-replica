import subprocess
import time
from flask import Flask, request, jsonify

app = Flask(__name__)

# Helper function to get the IP address of the VM
def get_vm_ip(vm_name):
    try:
        result = subprocess.run(
            ['virsh', 'domifaddr', vm_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        output = result.stdout.decode() 
        return output, 200
    except subprocess.CalledProcessError as e:
        return "Unable to fetch IP address", 500
    
# Helper function to create a VM
def create_vm(vm_name, iso_path, vcpu, ram, disk_size):
    disk_path = f"/var/lib/libvirt/images/{vm_name}.qcow2"
    try:
        # Create the VM with graphical output
        subprocess.run(
            [
                "/usr/bin/virt-install",
                "--name", vm_name,
                "--os-variant", "ubuntu24.10",
                "--vcpu", str(vcpu),
                "--ram", str(ram),
                "--graphics", "spice", 
                "--cdrom", iso_path,
                "--network", "network=default",
                "--disk", f"path={disk_path},size={disk_size}",
                "--noautoconsole"
            ],
            check=True
        )
        return {"success": True, "message": "VM created successfully!"}
    except subprocess.CalledProcessError as e:
        return {"success": False, "error": f"Failed to create VM: {e}"}

@app.route('/create_vm', methods=['POST'])
def create_vm_api():
    try:
        # Parse the incoming request
        data = request.json
        vm_name = data.get('vm_name')
        vcpu = data.get('vcpu', 2)
        ram = data.get('ram', 2048)
        storage = data.get('storage', 7)
        
        if not vm_name:
            return jsonify({"error": "VM name is required"}), 400

        iso_path = "/home/nevil/Downloads/ubuntu-24.10.iso"  # Adjust path as needed
        
        # Create the VM
        result = create_vm(vm_name, iso_path, vcpu, ram, storage)
        
        if result["success"]:
            # Wait for 5 seconds to allow the VM to initialize and get an IP address
            time.sleep(5)
            
            # Fetch the IP address of the newly created VM
            ip_address = get_vm_ip(vm_name)
            if ip_address:
                return jsonify({"message": result["message"], "ip_address": ip_address}), 200
            else:
                return jsonify({"message": result["message"], "warning": "VM IP not available yet"}), 200
        else:
            return jsonify({"error": result["error"]}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_vm_ip', methods=['GET'])
def get_vm_ip_api():
    try:
        vm_name = request.args.get('vm_name')
        if not vm_name:
            return jsonify({"error": "VM name is required"}), 400
        
        # Get the IP address of the VM
        ip_address = get_vm_ip(vm_name)
        
        if ip_address:
            return jsonify({"ip_address": ip_address}), 200
        else:
            return jsonify({"warning": "VM IP not available yet"}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)