from loguru import logger
import sys
from pathlib import Path
from datetime import datetime

def setup_logger():
    """配置日志系统
    
    Returns:
        logger: 配置好的loguru logger实例
    """
    # 创建日志目录
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # 生成日志文件路径
    log_file_path = log_dir / f"app_{datetime.now().strftime('%Y%m%d')}.log"
    
    # 移除默认处理器
    logger.remove()
    
    # 添加文件处理器
    logger.add(
        str(log_file_path),
        rotation="00:00",
        retention="7 days",
        enqueue=True,
        encoding="utf-8",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
    )
    
    # 添加控制台处理器
    logger.add(
        sys.stdout,
        level="INFO",
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )
    
    return logger