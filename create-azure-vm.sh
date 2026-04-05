#!/bin/bash

################################################################################
# Create Azure VM for CarbonScope
# Quick VM setup with Docker pre-installed
################################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

clear
echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║     Create Azure VM for CarbonScope                           ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Configuration
RESOURCE_GROUP="carbonscope-vm-rg"
VM_NAME="carbonscope-vm"
LOCATION="eastus"
VM_SIZE="Standard_B2s"  # 2 vCPU, 4GB RAM - $30/month
SSH_KEY="/teamspace/studios/this_studio/VM Key.pem"

print_info "VM Configuration:"
echo "  Name: $VM_NAME"
echo "  Size: $VM_SIZE (2 vCPU, 4GB RAM)"
echo "  Location: $LOCATION"
echo "  OS: Ubuntu 22.04 LTS"
echo "  Cost: ~$30/month"
echo ""

read -p "$(echo -e ${YELLOW}Create VM? [y/N]: ${NC})" -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_info "Cancelled"
    exit 0
fi

# Check Azure login
print_header "Checking Azure Authentication"

if ! az account show &> /dev/null; then
    print_error "Not logged in to Azure"
    echo "Run: az login"
    exit 1
fi

print_success "Logged in to Azure"
SUBSCRIPTION=$(az account show --query name -o tsv)
echo "  Subscription: $SUBSCRIPTION"

# Create resource group
print_header "Creating Resource Group"

az group create \
    --name "$RESOURCE_GROUP" \
    --location "$LOCATION" \
    --output table

print_success "Resource group created"

# Create VM
print_header "Creating Virtual Machine"

print_info "This will take 2-3 minutes..."

# Cloud-init script to install Docker
cat > /tmp/cloud-init.txt << 'CLOUDINIT'
#cloud-config
package_upgrade: true
packages:
  - docker.io
  - docker-compose
  - git
  - curl
runcmd:
  - systemctl start docker
  - systemctl enable docker
  - usermod -aG docker ubuntu
  - ufw allow 22/tcp
  - ufw allow 80/tcp
  - ufw allow 443/tcp
  - ufw --force enable
CLOUDINIT

# Generate new SSH key pair
print_info "Generating SSH key pair..."
ssh-keygen -t rsa -b 2048 -f /tmp/carbonscope-vm-key -N "" -q

# Create VM
az vm create \
    --resource-group "$RESOURCE_GROUP" \
    --name "$VM_NAME" \
    --image Ubuntu2204 \
    --size "$VM_SIZE" \
    --admin-username ubuntu \
    --ssh-key-values @/tmp/carbonscope-vm-key.pub \
    --public-ip-sku Standard \
    --custom-data /tmp/cloud-init.txt \
    --output table

# Get VM IP
VM_IP=$(az vm show \
    --resource-group "$RESOURCE_GROUP" \
    --name "$VM_NAME" \
    --show-details \
    --query publicIps -o tsv)

# Open ports
print_header "Configuring Firewall"

az vm open-port \
    --resource-group "$RESOURCE_GROUP" \
    --name "$VM_NAME" \
    --port 80 \
    --priority 1001

az vm open-port \
    --resource-group "$RESOURCE_GROUP" \
    --name "$VM_NAME" \
    --port 443 \
    --priority 1002

print_success "Firewall configured"

# Save SSH key
print_header "Saving SSH Key"

mv /tmp/carbonscope-vm-key "/teamspace/studios/this_studio/CarbonScope VM Key.pem"
chmod 600 "/teamspace/studios/this_studio/CarbonScope VM Key.pem"

print_success "SSH key saved"

# Cleanup
rm -f /tmp/carbonscope-vm-key.pub /tmp/cloud-init.txt

# Summary
print_header "VM Created Successfully!"

echo ""
echo -e "${GREEN}✓ VM is ready!${NC}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "VM INFORMATION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  VM Name: $VM_NAME"
echo "  IP Address: $VM_IP"
echo "  Username: ubuntu"
echo "  SSH Key: /teamspace/studios/this_studio/CarbonScope VM Key.pem"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "NEXT STEPS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. Test SSH connection:"
echo "   ssh -i \"/teamspace/studios/this_studio/CarbonScope VM Key.pem\" ubuntu@$VM_IP"
echo ""
echo "2. Configure Cloudflare DNS:"
echo "   • Login: https://dash.cloudflare.com"
echo "   • Domain: ensimu.space"
echo "   • Add A record: carbonscope → $VM_IP"
echo ""
echo "3. Deploy CarbonScope:"
echo "   ./deploy-to-vm.sh"
echo "   # When prompted, enter: $VM_IP"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Save VM info
cat > vm-info.txt << EOF
CarbonScope VM Information
==========================
Created: $(date)

VM Name: $VM_NAME
IP Address: $VM_IP
Username: ubuntu
SSH Key: /teamspace/studios/this_studio/CarbonScope VM Key.pem
Resource Group: $RESOURCE_GROUP
Location: $LOCATION
Size: $VM_SIZE

SSH Command:
ssh -i "/teamspace/studios/this_studio/CarbonScope VM Key.pem" ubuntu@$VM_IP

Cloudflare DNS:
Type: A
Name: carbonscope
IPv4: $VM_IP
Proxy: ON

Cost: ~$30/month
EOF

print_success "VM information saved to vm-info.txt"
