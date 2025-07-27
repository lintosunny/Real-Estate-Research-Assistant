import sys
import os
from pathlib import Path

def main():
    """Main entry point"""
    try:
        # Get the project root directory
        project_root = Path(__file__).parent.absolute()
        
        # Add project root to Python path if not already there
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))
        
        # Add the real_estate_assistant directory to Python path
        real_estate_assistant_path = project_root / "real_estate_assistant"
        if str(real_estate_assistant_path) not in sys.path:
            sys.path.insert(0, str(real_estate_assistant_path))
        
        # Set PYTHONPATH environment variable
        current_pythonpath = os.environ.get('PYTHONPATH', '')
        paths_to_add = [str(project_root), str(real_estate_assistant_path)]
        
        for path in paths_to_add:
            if path not in current_pythonpath:
                if current_pythonpath:
                    current_pythonpath = f"{path}{os.pathsep}{current_pythonpath}"
                else:
                    current_pythonpath = path
        
        os.environ['PYTHONPATH'] = current_pythonpath
        
        print(f"Project root: {project_root}")
        print(f"Real estate assistant path: {real_estate_assistant_path}")
        print(f"Python path: {sys.path[:3]}...")  # Show first 3 entries
        
        # Import and run the Streamlit app
        try:
            from frontend import main as run_app
            print("Successfully imported frontend module")
        except ImportError as e:
            print(f"Failed to import frontend: {e}")
            # Try alternative import
            from src.frontend import main as run_app
            print("Successfully imported using real_estate_assistant.frontend")
        
        run_app()
        
    except ImportError as e:
        print(f"Error importing modules: {e}")
        print("Make sure all dependencies are installed and the project structure is correct.")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Project root: {Path(__file__).parent.absolute()}")
        
        # Debug information
        print("\nDebugging information:")
        print("Contents of project root:")
        for item in Path(__file__).parent.iterdir():
            print(f"  {item.name} ({'dir' if item.is_dir() else 'file'})")
        
        real_estate_dir = Path(__file__).parent / "real_estate_assistant"
        if real_estate_dir.exists():
            print(f"\nContents of {real_estate_dir}:")
            for item in real_estate_dir.iterdir():
                print(f"  {item.name} ({'dir' if item.is_dir() else 'file'})")
        
        sys.exit(1)
        
    except Exception as e:
        print(f"Error running application: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()