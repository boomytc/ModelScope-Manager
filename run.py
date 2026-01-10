import sys
from pathlib import Path

# 将项目根目录添加到 sys.path
sys.path.append(str(Path(__file__).resolve().parent))

from gui.main import main

if __name__ == "__main__":
    main()
