"""
Fog-Shrouded Chronicles - Setup Script
Checks dependencies and helps install requirements
Works on any PC with the pendrive
"""
import sys
import subprocess
import os
from pathlib import Path


class SetupManager:
    """Manages installation and verification of dependencies"""
    
    def __init__(self):
        self.required_packages = {
            'pandas': '2.0.0',
            'groq': '0.4.0',
            'sentence-transformers': '2.2.0',
            'networkx': '3.0',
            'numpy': '1.24.0',
            'Pillow': '10.0.0',  # For UI images
            'tk': 'built-in'      # Tkinter (usually comes with Python)
        }
        
        self.optional_packages = {
            'matplotlib': '3.7.0',  # For data visualization
        }
        
        self.python_version_required = (3, 8)
        
    def clear_screen(self):
        """Clear console screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self):
        """Print fancy header"""
        self.clear_screen()
        print("=" * 70)
        print(" " * 15 + "FOG-SHROUDED CHRONICLES")
        print(" " * 20 + "Setup & Installation")
        print("=" * 70)
        print()
    
    def check_python_version(self):
        """Check if Python version is compatible"""
        print("[1/6] Checking Python version...")
        
        current_version = sys.version_info[:2]
        required = self.python_version_required
        
        if current_version >= required:
            print(f"    ✓ Python {current_version[0]}.{current_version[1]} (OK)")
            return True
        else:
            print(f"    ❌ Python {current_version[0]}.{current_version[1]} (TOO OLD)")
            print(f"    Required: Python {required[0]}.{required[1]} or higher")
            print()
            print("    Please install a newer Python version from:")
            print("    https://www.python.org/downloads/")
            return False
    
    def check_pip(self):
        """Check if pip is installed"""
        print("\n[2/6] Checking pip (package manager)...")
        
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                print(f"    ✓ pip is installed")
                return True
            else:
                print(f"    ❌ pip not found")
                return False
                
        except Exception as e:
            print(f"    ❌ Error checking pip: {e}")
            return False
    
    def check_package(self, package_name):
        """Check if a package is installed"""
        try:
            if package_name == 'tk':
                # Special check for tkinter
                import tkinter
                return True
            else:
                __import__(package_name.replace('-', '_'))
                return True
        except ImportError:
            return False
    
    def check_all_packages(self):
        """Check all required packages"""
        print("\n[3/6] Checking required packages...")
        
        missing = []
        installed = []
        
        for package, version in self.required_packages.items():
            if package == 'tk':
                # Special handling for tkinter
                try:
                    import tkinter
                    print(f"    ✓ tkinter (built-in)")
                    installed.append(package)
                except ImportError:
                    print(f"    ❌ tkinter (missing - comes with Python)")
                    missing.append(package)
            else:
                if self.check_package(package):
                    print(f"    ✓ {package}")
                    installed.append(package)
                else:
                    print(f"    ❌ {package} (not installed)")
                    missing.append(package)
        
        return missing, installed
    
    def install_packages(self, packages):
        """Install missing packages"""
        if not packages:
            return True
        
        print(f"\n[4/6] Installing {len(packages)} missing package(s)...")
        print()
        
        # Filter out tkinter (can't pip install it)
        pip_packages = [p for p in packages if p != 'tk']
        
        if not pip_packages:
            if 'tk' in packages:
                print("    ⚠️  tkinter is missing but comes with Python")
                print("    Please reinstall Python with tkinter support")
            return False
        
        for package in pip_packages:
            print(f"    Installing {package}...", end=" ")
            
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", package],
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                
                if result.returncode == 0:
                    print("✓")
                else:
                    print("❌")
                    print(f"    Error: {result.stderr[:200]}")
                    return False
                    
            except subprocess.TimeoutExpired:
                print("❌ (timeout)")
                return False
            except Exception as e:
                print(f"❌ ({e})")
                return False
        
        print()
        print("    ✓ All packages installed successfully")
        return True
    
    def check_game_files(self):
        """Check if game files are present"""
        print("\n[5/6] Checking game files...")
        
        required_files = {
            'Data CSVs/Character_Info.csv': 'Character database',
            'Main.py': 'Main game file',
            'game/game_manager.py': 'Game manager',
            'ui/console.py': 'UI console'
        }
        
        base_dir = Path(__file__).parent
        missing_files = []
        
        for file_path, description in required_files.items():
            full_path = base_dir / file_path
            
            if full_path.exists():
                print(f"    ✓ {description}")
            else:
                print(f"    ❌ {description} (missing: {file_path})")
                missing_files.append(file_path)
        
        if missing_files:
            print()
            print("    ⚠️  Some game files are missing!")
            print("    Make sure all files are copied to the pendrive")
            return False
        
        return True
    
    def create_config(self):
        """Create config.json if it doesn't exist"""
        print("\n[6/6] Setting up configuration...")
        
        config_path = Path(__file__).parent / "config.json"
        
        if config_path.exists():
            print("    ✓ config.json already exists")
            return True
        
        import json
        
        default_config = {
            "groq_api_key": "YOUR_API_KEY_HERE",
            "model": "llama-3.1-70b-versatile",
            "max_tokens": 800,
            "temperature": 0.85,
            "game_settings": {
                "auto_save": True,
                "save_interval": 10,
                "max_history": 100
            }
        }
        
        try:
            with open(config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
            
            print(f"    ✓ Created config.json")
            print(f"    ⚠️  Don't forget to add your Groq API key!")
            return True
            
        except Exception as e:
            print(f"    ❌ Error creating config: {e}")
            return False
    
    def run_setup(self):
        """Run complete setup process"""
        self.print_header()
        
        # Step 1: Check Python
        if not self.check_python_version():
            print("\n" + "=" * 70)
            print("Setup failed: Python version too old")
            print("=" * 70)
            input("\nPress Enter to exit...")
            return False
        
        # Step 2: Check pip
        if not self.check_pip():
            print("\n" + "=" * 70)
            print("Setup failed: pip not found")
            print("=" * 70)
            print("\nTo install pip:")
            print("1. Download: https://bootstrap.pypa.io/get-pip.py")
            print("2. Run: python get-pip.py")
            print("=" * 70)
            input("\nPress Enter to exit...")
            return False
        
        # Step 3: Check packages
        missing, installed = self.check_all_packages()
        
        # Step 4: Install missing packages
        if missing:
            print(f"\nFound {len(missing)} missing package(s)")
            print("Do you want to install them now? (y/n): ", end="")
            
            choice = input().strip().lower()
            
            if choice == 'y':
                if not self.install_packages(missing):
                    print("\n" + "=" * 70)
                    print("Setup failed: Could not install all packages")
                    print("=" * 70)
                    input("\nPress Enter to exit...")
                    return False
            else:
                print("\nSetup cancelled by user")
                input("\nPress Enter to exit...")
                return False
        
        # Step 5: Check game files
        if not self.check_game_files():
            print("\n" + "=" * 70)
            print("Setup incomplete: Game files missing")
            print("=" * 70)
            input("\nPress Enter to exit...")
            return False
        
        # Step 6: Create config
        self.create_config()
        
        # Success!
        print("\n" + "=" * 70)
        print(" " * 25 + "✓ SETUP COMPLETE!")
        print("=" * 70)
        print()
        print("Next steps:")
        print("1. Edit config.json and add your Groq API key")
        print("   Get a free key at: https://console.groq.com/")
        print()
        print("2. Run Main.py to start the game")
        print("   Command: python Main.py")
        print()
        print("=" * 70)
        input("\nPress Enter to exit...")
        return True
    
    def create_requirements_txt(self):
        """Create requirements.txt file"""
        requirements_path = Path(__file__).parent / "requirements.txt"
        
        requirements = [
            "# Fog-Shrouded Chronicles - Requirements",
            "# Install all with: pip install -r requirements.txt",
            "",
            "# Core dependencies",
            "pandas>=2.0.0",
            "groq>=0.4.0",
            "sentence-transformers>=2.2.0",
            "networkx>=3.0",
            "numpy>=1.24.0",
            "Pillow>=10.0.0",
            "",
            "# Optional (for data visualization)",
            "matplotlib>=3.7.0",
            "",
            "# Note: tkinter comes with Python, no need to install"
        ]
        
        try:
            with open(requirements_path, 'w') as f:
                f.write('\n'.join(requirements))
            print(f"✓ Created requirements.txt")
            return True
        except Exception as e:
            print(f"❌ Error creating requirements.txt: {e}")
            return False


def show_manual_instructions():
    """Show manual installation instructions"""
    print("\n" + "=" * 70)
    print(" " * 20 + "MANUAL INSTALLATION GUIDE")
    print("=" * 70)
    print()
    print("If automatic installation fails, install manually:")
    print()
    print("1. Open Command Prompt / Terminal")
    print()
    print("2. Navigate to the pendrive folder:")
    print("   cd E:\\FogShroudedChronicles")
    print("   (replace E: with your pendrive letter)")
    print()
    print("3. Install requirements:")
    print("   pip install -r requirements.txt")
    print()
    print("   OR install individually:")
    print("   pip install pandas groq sentence-transformers networkx numpy Pillow")
    print()
    print("4. Run the game:")
    print("   python Main.py")
    print()
    print("=" * 70)
    print()
    print("Get Groq API Key (FREE):")
    print("1. Visit: https://console.groq.com/")
    print("2. Sign up (it's free)")
    print("3. Go to 'API Keys' and create a new key")
    print("4. Copy the key to config.json")
    print()
    print("=" * 70)


def main():
    """Main setup entry point"""
    
    try:
        setup = SetupManager()
        
        # Create requirements.txt first
        print("Creating requirements.txt...", end=" ")
        setup.create_requirements_txt()
        print()
        
        # Run setup
        success = setup.run_setup()
        
        if not success:
            print("\nWould you like to see manual installation instructions? (y/n): ", end="")
            if input().strip().lower() == 'y':
                show_manual_instructions()
    
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()