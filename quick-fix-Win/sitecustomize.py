# FIX BUG HERE #
import torch
import os
import sys
import ctypes

# --- [核心修复] 强制预加载 Conda 的 DLL ---
# 目的：在 Isaac Sim 或 h5py 加载任何 DLL 之前，先锁定正确的 zlib/blosc 版本

if os.name == 'nt': # 在 Windows 上执行
    conda_prefix = os.environ.get("CONDA_PREFIX")
    if not conda_prefix:
        # 如果 CONDA_PREFIX 没设置，尝试从当前 python.exe 路径推断
        import pathlib
        exe_path = pathlib.Path(sys.executable)
        if 'envs' in exe_path.parts:
            idx = exe_path.parts.index('envs')
            conda_prefix = str(pathlib.Path(*exe_path.parts[:idx+2]))
    
    if conda_prefix:
        conda_bin = os.path.join(conda_prefix, "Library", "bin")
        if os.path.isdir(conda_bin):
            # 1. 使用官方 API 添加搜索目录 (优先级最高)
            try:
                os.add_dll_directory(conda_bin)
                print(f"[FIX] Added DLL directory: {conda_bin}")
            except Exception as e:
                print(f"[WARN] add_dll_directory failed: {e}")

            # 2. 【关键步骤】显式预加载关键 DLL
            # 这样即使 Isaac Sim 试图加载自己的 dll，也会发现这些已经被加载了
            dlls_to_preload = ['zlib.dll', 'blosc2.dll', 'blosc.dll', 'hdf5.dll', 'libaec.dll']
            loaded_count = 0
            for dll_name in dlls_to_preload:
                dll_path = os.path.join(conda_bin, dll_name)
                if os.path.exists(dll_path):
                    try:
                        ctypes.CDLL(dll_path)
                        print(f"[FIX] Pre-loaded: {dll_name}")
                        loaded_count += 1
                    except OSError as e:
                        # 忽略已经加载的情况或其他非致命错误
                        pass
            
            if loaded_count > 0:
                print(f"[SUCCESS] Successfully pre-loaded {loaded_count} critical DLLs from Conda.")
            else:
                print(f"[WARN] No critical DLLs found in {conda_bin}. Check your installation.")
        else:
            print(f"[ERROR] Conda bin directory not found: {conda_bin}")
    else:
        print("[ERROR] Could not determine Conda prefix. Please ensure 'conda activate Matterix' was run.")
# ----------------------------------------