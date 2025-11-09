#!/usr/bin/env python3
"""
Project Setup Script
Interactive configuration for Multi-Agent Travel System
"""

import os
import sys
from pathlib import Path
from typing import Optional


class Color:
    """ANSI color codes"""
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_header(text: str):
    """Print styled header"""
    print(f"\n{Color.BOLD}{Color.BLUE}{'='*60}{Color.END}")
    print(f"{Color.BOLD}{Color.BLUE}{text}{Color.END}")
    print(f"{Color.BOLD}{Color.BLUE}{'='*60}{Color.END}\n")


def print_success(text: str):
    """Print success message"""
    print(f"{Color.GREEN}✓ {text}{Color.END}")


def print_warning(text: str):
    """Print warning message"""
    print(f"{Color.YELLOW}⚠ {text}{Color.END}")


def print_error(text: str):
    """Print error message"""
    print(f"{Color.RED}✗ {text}{Color.END}")


def print_info(text: str):
    """Print info message"""
    print(f"{Color.BLUE}ℹ {text}{Color.END}")


def prompt_input(prompt: str, default: Optional[str] = None, required: bool = True) -> str:
    """Prompt user for input with optional default"""
    if default:
        prompt_text = f"{prompt} [{default}]: "
    else:
        prompt_text = f"{prompt}: "
    
    while True:
        value = input(prompt_text).strip()
        
        if not value and default:
            return default
        
        if not value and required:
            print_warning("This field is required. Please enter a value.")
            continue
        
        return value


def prompt_yes_no(prompt: str, default: bool = False) -> bool:
    """Prompt yes/no question"""
    default_str = "Y/n" if default else "y/N"
    response = input(f"{prompt} [{default_str}]: ").strip().lower()
    
    if not response:
        return default
    
    return response in ['y', 'yes']


def validate_ip(ip: str) -> bool:
    """Validate IP address format"""
    parts = ip.split('.')
    if len(parts) != 4:
        return False
    try:
        return all(0 <= int(part) <= 255 for part in parts)
    except ValueError:
        return False


def validate_url(url: str) -> bool:
    """Basic URL validation"""
    return url.startswith(('http://', 'https://'))


class ProjectSetup:
    def __init__(self):
        self.config = {}
        self.project_root = Path.cwd()
        self.env_file = self.project_root / ".env"
        
    def welcome(self):
        """Display welcome message"""
        print_header("Multi-Agent Travel System - Project Setup")
        print("This script will help you configure the project with your Azure resources.")
        print("\nWhat this script does:")
        print("  • Creates .env file with your configuration")
        print("  • Validates your inputs")
        print("  • Provides next steps for deployment")
        print("\nYou'll need:")
        print("  • Azure Kubernetes Service (AKS) public IP")
        print("  • Azure OpenAI endpoint and deployment name")
        print("  • Azure Container Registry (ACR) name")
        print()
    
    def check_existing_config(self):
        """Check for existing .env file"""
        if self.env_file.exists():
            print_warning(f"Found existing .env file: {self.env_file}")
            if not prompt_yes_no("Overwrite existing configuration?", default=False):
                print_info("Keeping existing configuration. Exiting.")
                return False
        return True
    
    def gather_kubernetes_config(self):
        """Gather Kubernetes configuration"""
        print_header("Kubernetes Configuration")
        
        while True:
            public_ip = prompt_input("Enter your AKS LoadBalancer Public IP")
            if validate_ip(public_ip):
                self.config['PUBLIC_IP'] = public_ip
                break
            print_error("Invalid IP address format. Please use format: xxx.xxx.xxx.xxx")
        
        self.config['K8S_NAMESPACE'] = prompt_input(
            "Kubernetes namespace",
            default="multiagent-microservices"
        )
        
        self.config['BASE_URL'] = f"http://{self.config['PUBLIC_IP']}"
        print_success(f"Base URL: {self.config['BASE_URL']}")
    
    def gather_openai_config(self):
        """Gather Azure OpenAI configuration"""
        print_header("Azure OpenAI Configuration")
        
        print_info("Example: my-openai-resource (not the full URL)")
        resource_name = prompt_input("Azure OpenAI resource name")
        
        endpoint = f"https://{resource_name}.openai.azure.com/"
        self.config['AZURE_OPENAI_ENDPOINT'] = endpoint
        print_success(f"Endpoint: {endpoint}")
        
        self.config['AZURE_OPENAI_DEPLOYMENT'] = prompt_input(
            "Azure OpenAI deployment name",
            default="gpt-4o-mini"
        )
        
        self.config['AZURE_OPENAI_API_VERSION'] = prompt_input(
            "Azure OpenAI API version",
            default="2025-01-01-preview"
        )
    
    def gather_acr_config(self):
        """Gather Azure Container Registry configuration"""
        print_header("Azure Container Registry Configuration")
        
        print_info("Example: myregistry (not the full .azurecr.io URL)")
        acr_name = prompt_input("Azure Container Registry name")
        
        self.config['ACR_NAME'] = acr_name
        self.config['ACR_URL'] = f"{acr_name}.azurecr.io"
        print_success(f"ACR URL: {self.config['ACR_URL']}")
        
        self.config['IMAGE_TAG'] = prompt_input(
            "Docker image tag",
            default="latest"
        )
    
    def gather_optional_config(self):
        """Gather optional configuration"""
        print_header("Optional Configuration")
        
        if prompt_yes_no("Configure Azure authentication (service principal)?", default=False):
            self.config['AZURE_CLIENT_ID'] = prompt_input("Azure Client ID", required=False)
            self.config['AZURE_CLIENT_SECRET'] = prompt_input("Azure Client Secret", required=False)
            self.config['AZURE_TENANT_ID'] = prompt_input("Azure Tenant ID", required=False)
        else:
            self.config['AZURE_USE_MANAGED_IDENTITY'] = 'true'
            print_info("Using managed identity for Azure authentication")
        
        self.config['LOG_LEVEL'] = prompt_input(
            "Log level (DEBUG, INFO, WARNING, ERROR)",
            default="INFO"
        )
        
        self.config['DEBUG_MODE'] = 'true' if prompt_yes_no("Enable debug mode?", default=False) else 'false'
    
    def write_env_file(self):
        """Write configuration to .env file"""
        print_header("Writing Configuration")
        
        env_content = f"""# ======================================
# Multi-Agent Travel System Configuration
# Generated by setup_project.py
# ======================================

# =====================================
# Azure Kubernetes Service (AKS)
# =====================================
PUBLIC_IP={self.config['PUBLIC_IP']}
K8S_NAMESPACE={self.config['K8S_NAMESPACE']}
BASE_URL={self.config['BASE_URL']}

# =====================================
# Azure OpenAI Configuration
# =====================================
AZURE_OPENAI_ENDPOINT={self.config['AZURE_OPENAI_ENDPOINT']}
AZURE_OPENAI_DEPLOYMENT={self.config['AZURE_OPENAI_DEPLOYMENT']}
AZURE_OPENAI_API_VERSION={self.config['AZURE_OPENAI_API_VERSION']}

# =====================================
# Azure Container Registry (ACR)
# =====================================
ACR_NAME={self.config['ACR_NAME']}
ACR_URL={self.config['ACR_URL']}
IMAGE_TAG={self.config['IMAGE_TAG']}

# =====================================
# Service URLs
# =====================================
A2A_ENDPOINT={self.config['BASE_URL']}/a2a
CURRENCY_AGENT_URL=http://localhost:8001
ACTIVITY_AGENT_URL=http://localhost:8002
COORDINATOR_URL=http://localhost:8000

# =====================================
# Authentication
# =====================================
"""
        if 'AZURE_CLIENT_ID' in self.config:
            env_content += f"""AZURE_CLIENT_ID={self.config['AZURE_CLIENT_ID']}
AZURE_CLIENT_SECRET={self.config['AZURE_CLIENT_SECRET']}
AZURE_TENANT_ID={self.config['AZURE_TENANT_ID']}
"""
        else:
            env_content += f"""AZURE_USE_MANAGED_IDENTITY={self.config.get('AZURE_USE_MANAGED_IDENTITY', 'true')}
"""
        
        env_content += f"""
# =====================================
# Development Settings
# =====================================
LOG_LEVEL={self.config['LOG_LEVEL']}
DEBUG_MODE={self.config['DEBUG_MODE']}

# =====================================
# External APIs
# =====================================
FRANKFURTER_API_URL=https://api.frankfurter.app

# =====================================
# Docker Images
# =====================================
COORDINATOR_IMAGE={self.config['ACR_URL']}/multiagent-kubecon-microservices/coordinator:{self.config['IMAGE_TAG']}
CURRENCY_AGENT_IMAGE={self.config['ACR_URL']}/multiagent-kubecon-microservices/currency-agent:{self.config['IMAGE_TAG']}
ACTIVITY_AGENT_IMAGE={self.config['ACR_URL']}/multiagent-kubecon-microservices/activity-agent:{self.config['IMAGE_TAG']}
"""
        
        try:
            with open(self.env_file, 'w') as f:
                f.write(env_content)
            print_success(f"Configuration written to: {self.env_file}")
        except Exception as e:
            print_error(f"Failed to write .env file: {e}")
            return False
        
        return True
    
    def show_next_steps(self):
        """Display next steps"""
        print_header("Next Steps")
        
        print("1. Verify your configuration:")
        print(f"   cat {self.env_file}")
        print()
        
        print("2. Test Azure OpenAI connection:")
        print("   python -c 'from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv(\"AZURE_OPENAI_ENDPOINT\"))'")
        print()
        
        print("3. Deploy to AKS:")
        print("   kubectl apply -f manifests/")
        print()
        
        print("4. Verify deployment:")
        print(f"   curl http://{self.config['PUBLIC_IP']}/a2a/.well-known/agent-card.json")
        print()
        
        print("5. Test the system:")
        print("   python test_system_complete.py")
        print()
        
        print_success("Setup complete! Your project is ready to use.")
        print()
    
    def run(self):
        """Run the setup process"""
        try:
            self.welcome()
            
            if not self.check_existing_config():
                return 0
            
            self.gather_kubernetes_config()
            self.gather_openai_config()
            self.gather_acr_config()
            self.gather_optional_config()
            
            if not self.write_env_file():
                return 1
            
            self.show_next_steps()
            
            return 0
            
        except KeyboardInterrupt:
            print("\n\nSetup cancelled by user.")
            return 130
        except Exception as e:
            print_error(f"Setup failed: {e}")
            return 1


def main():
    """Main entry point"""
    setup = ProjectSetup()
    return setup.run()


if __name__ == "__main__":
    sys.exit(main())
