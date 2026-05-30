#配置文件
#统一管理路径，后面所有文件都从这里读取配置

import os
from pathlib import Path
#项目根目录
BASE_DIR=Path(__file__).resolve().parent.parent

#数据目录
DATA_DIR=BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

#sqlite连接url
DATABASE_URL=f"sqlite:///{DATA_DIR/'Kykg_punch-in_system.db'}"

#备份 / 导出目录
BACKUP_DIR=DATA_DIR / "backup"
BACKUP_DIR.mkdir(exist_ok=True)

EXPORT_DIR=DATA_DIR / "export"
EXPORT_DIR.mkdir(exist_ok=True)

# 会话密钥（从环境变量读取，缺省给开发用固定值）
SECRET_KEY = os.getenv("SECRET_KEY", "kaoyan-kaogong-dev-secret-key-change-in-production")

