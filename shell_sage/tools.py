# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/02_tools.ipynb.

# %% auto 0
__all__ = ['tools', 'rgrep', 'view', 'create', 'insert', 'str_replace']

# %% ../nbs/02_tools.ipynb 2
from pathlib import Path
from subprocess import run

# %% ../nbs/02_tools.ipynb 3
def rgrep(term:str, path:str='.', grep_args:str='')->str:
    "Perform recursive grep search for `term` in `path` with optional grep arguments"
    # Build grep command with additional arguments
    path = Path(path).expanduser().resolve()
    cmd = f"grep -r '{term}' {path} {grep_args}"
    return run(cmd, shell=True, capture_output=True, text=True).stdout

# %% ../nbs/02_tools.ipynb 5
def view(path:str, rng:tuple[int,int]=None, nums:bool=False):
    "View directory or file contents with optional line range and numbers"
    try:
        p = Path(path).expanduser().resolve()
        if not p.exists(): return f"Error: File not found: {p}"
        if p.is_dir(): return f"Directory contents of {p}:\n" + "\n".join([str(f) for f in p.glob("**/*")
                                                                           if not f.name.startswith(".")])
        
        lines = p.read_text().splitlines()
        s,e = 1,len(lines)
        if rng:
            s,e = rng
            if not (1 <= s <= len(lines)): return f"Error: Invalid start line {s}"
            if e != -1 and not (s <= e <= len(lines)): return f"Error: Invalid end line {e}"
            lines = lines[s-1:None if e==-1 else e]
            
        return "\n".join([f"{i+s-1:6d} │ {l}" for i,l in enumerate(lines,1)] if nums else lines)
    except Exception as e: return f"Error viewing file: {str(e)}"

# %% ../nbs/02_tools.ipynb 8
def create(path: str, file_text: str, overwrite:bool=False) -> str:
    "Creates a new file with the given content at the specified path"
    try:
        p = Path(path)
        if p.exists():
            if not overwrite: return f"Error: File already exists: {p}"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(file_text)
        return f"Created file {p} containing:\n{file_text}"
    except Exception as e: return f"Error creating file: {str(e)}"

# %% ../nbs/02_tools.ipynb 10
def insert(path: str, insert_line: int, new_str: str) -> str:
    "Insert new_str at specified line number"
    try:
        p = Path(path)
        if not p.exists(): return f"Error: File not found: {p}"
            
        content = p.read_text().splitlines()
        if not (0 <= insert_line <= len(content)): return f"Error: Invalid line number {insert_line}"
            
        content.insert(insert_line, new_str)
        new_content = "\n".join(content)
        p.write_text(new_content)
        return f"Inserted text at line {insert_line} in {p}.\nNew contents:\n{new_content}"
    except Exception as e: return f"Error inserting text: {str(e)}"

# %% ../nbs/02_tools.ipynb 12
def str_replace(path: str, old_str: str, new_str: str) -> str:
    "Replace first occurrence of old_str with new_str in file"
    try:
        p = Path(path)
        if not p.exists(): return f"Error: File not found: {p}"
            
        content = p.read_text()
        count = content.count(old_str)
        
        if count == 0: return "Error: Text not found in file"
        if count > 1: return f"Error: Multiple matches found ({count})"
            
        new_content = content.replace(old_str, new_str, 1)
        p.write_text(new_content)
        return f"Replaced text in {p}.\nNew contents:\n{new_content}"
    except Exception as e: return f"Error replacing text: {str(e)}"

# %% ../nbs/02_tools.ipynb 14
tools = [rgrep, view, create, insert, str_replace]
