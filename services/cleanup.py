import os
import time

# CONFIG (ADJUST IF NEEDED)
MAX_FOLDER_SIZE_MB = 500      # Hard limit
MAX_FILE_AGE_SEC = 30 * 60    # 30 minutes

def get_folder_size(path):
    total = 0
    for root, _, files in os.walk(path):
        for f in files:
            fp = os.path.join(root, f)
            if os.path.isfile(fp):
                total += os.path.getsize(fp)
    return total

def cleanup_music_folder(folder_path):
    if not os.path.exists(folder_path):
        return

    now = time.time()

    files = []
    for f in os.listdir(folder_path):
        fp = os.path.join(folder_path, f)
        if os.path.isfile(fp):
            files.append(fp)

    # 1️⃣ DELETE OLD FILES
    for fp in files:
        age = now - os.path.getmtime(fp)
        if age > MAX_FILE_AGE_SEC:
            try:
                os.remove(fp)
                print(f"🧹 Deleted old file: {fp}")
            except Exception as e:
                print("Cleanup error:", e)

    # 2️⃣ ENFORCE DISK QUOTA
    size = get_folder_size(folder_path)
    max_size = MAX_FOLDER_SIZE_MB * 1024 * 1024

    if size <= max_size:
        return

    # Sort files by oldest first
    files.sort(key=lambda f: os.path.getmtime(f))

    for fp in files:
        if size <= max_size:
            break
        try:
            file_size = os.path.getsize(fp)
            os.remove(fp)
            size -= file_size
            print(f"🧹 Deleted for quota: {fp}")
        except Exception as e:
            print("Quota cleanup error:", e)