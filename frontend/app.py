import streamlit as st
import requests

# Define the API endpoints
API_ENDPOINT = "http://localhost:5000/create_vm"  
GET_IP_ENDPOINT = "http://localhost:5000/get_vm_ip"  

# App Title
st.title("KVM EC2 Replica - VM Creator")

# Input Form for VM Creation
with st.form(key="vm_form"):
    st.subheader("Configure Your Virtual Machine")
    
    # VM Name
    vm_name = st.text_input("Enter VM Name", value="test-vm", help="Enter a unique name for your virtual machine.")
    
    # VM Configuration Inputs
    col1, col2, col3 = st.columns(3)
    with col1:
        vcpu = st.number_input("Number of CPUs", min_value=1, max_value=16, value=2, step=1, help="Select the number of CPUs for the VM.")
    with col2:
        ram = st.number_input("RAM (in MiB)", min_value=512, max_value=32768, value=2048, step=512, help="Set the amount of RAM for the VM (in MiB).")
    with col3:
        storage = st.number_input("Storage (in GB)", min_value=1, max_value=1000, value=7, step=1, help="Set the size of the VM's disk storage (in GB).")
    
    # Submit Button
    submitted = st.form_submit_button("Create VM")
    
    if submitted:
        if not vm_name.strip():
            st.error("VM name is required!")
        else:
            with st.spinner("Creating your VM..."):
                try:
                    # Prepare the payload for the API request
                    payload = {
                        "vm_name": vm_name,
                        "vcpu": vcpu,
                        "ram": ram,
                        "storage": storage
                    }
                    
                    # Send POST request to the backend API
                    response = requests.post(API_ENDPOINT, json=payload)
                    
                    # Check the response status
                    if response.status_code == 200:
                        result = response.json()
                        st.success(f"VM '{vm_name}' created successfully!")
                        # Optionally show initial IP fetch message
                        st.write("VM IP address may not be available immediately.")
                    else:
                        # Handle errors returned by the API
                        error_message = response.json().get("error", "Unknown error occurred.")
                        st.error(f"Error: {error_message}")
                
                except requests.exceptions.RequestException as e:
                    # Handle network errors or other exceptions
                    st.error(f"An error occurred: {e}")

# Add a button outside of the form to fetch the VM IP
ip_fetch_button = st.button("Get VM IP")

if ip_fetch_button:
    if not vm_name.strip():
        st.error("Please create a VM first!")
    else:
        with st.spinner("Fetching VM IP..."):
            try:
                # Send a GET request to fetch the IP address of the VM
                ip_response = requests.get(f"{GET_IP_ENDPOINT}?vm_name={vm_name}")
                if ip_response.status_code == 200:
                    # Print all the output as received from the virsh command (raw output)
                    ip_data = ip_response.text  # This is the full output, no extraction or processing
                    st.text_area("VM IP Information", value=ip_data, height=300)  # Display in a text box
                else:
                    st.error("Failed to fetch IP address.")
            except requests.exceptions.RequestException as e:
                st.error(f"An error occurred: {e}")

# About Section
st.sidebar.markdown("### About")
st.sidebar.info(
    """
    This application allows you to create and configure virtual machines (VMs) on a local KVM host.
    Customize CPU, RAM, and storage to suit your requirements.
    """
)