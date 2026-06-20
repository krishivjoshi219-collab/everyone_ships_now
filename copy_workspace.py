import os
import sys

def build_workspace_blueprint():
    # Target directory is the current folder where the script runs
    target_dir = os.getcwd()
    output_file = "project_blueprint.txt"
    
    # Explicit files/folders to completely skip to keep your blueprint clean and compact
    skip_dirs = {'.git', '__pycache__', '.venv', 'env', 'sample_logs'}
    skip_files = {'key.json', 'project_blueprint.txt', 'copy_workspace.py', '.gitignore'}
    
    # Valid code extensions we want to capture
    valid_extensions = {'.py', '.txt', '.sh', '.md', '.json'}
    
    blueprint_content = []
    blueprint_content.append("==================================================")
    blueprint_content.append(f"📦 DEPENDENCE DOC FULL ARCHITECTURE BLUEPRINT")
    blueprint_content.append(f"📂 Root Directory: {target_dir}")
    blueprint_content.append("==================================================\n\n")
    
    print("🔍 Scanning directory tree arrays...")
    
    for root, dirs, files in os.walk(target_dir):
        # Filter out directories we don't want to crawl
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        
        for file in files:
            if file in skip_files:
                continue
                
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, target_dir)
            _, ext = os.path.splitext(file)
            
            if ext in valid_extensions:
                blueprint_content.append(f"▶️ FILE NODE START: {relative_path}")
                blueprint_content.append("-" * 60)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        blueprint_content.append(f.read())
                except Exception as e:
                    blueprint_content.append(f"[ERROR READING FILE: {str(e)}]")
                blueprint_content.append("-" * 60)
                blueprint_content.append(f"⏹️ FILE NODE END: {relative_path}\n\n")
    
    final_text = "\n".join(blueprint_content)
    
    # 💾 Layer 1: Save to file asset
    with open(output_file, "w", encoding="utf-8") as out_f:
        out_f.write(final_text)
    print(f"✅ Success! Compiled blueprint saved locally to: `{output_file}`")
    
    # 📋 Layer 2: Push directly to System Clipboard
    try:
        import pyperclip
        pyperclip.copy(final_text)
        print("🚀 Absolute Win! The entire workspace has been copied straight to your clipboard matrix!")
    except ImportError:
        print("\n⚠️ Pyperclip package not isolated in environment loops.")
        print("💡 Run this command to lock in clipboard support: `pip install pyperclip`")
        print(f"📝 You can still open `{output_file}` to grab the text manually!")

if __name__ == "__main__":
    build_workspace_blueprint()
