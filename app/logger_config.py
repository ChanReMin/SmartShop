import logging
import os

def setup_logger(name="app", log_file="app/logs/app.log", level=logging.INFO):
    """
    Thiết lập logger chung cho app:
    - name: tên logger
    - log_file: file log (relative path)
    - level: mức log
    """
    # Tạo folder logs nếu chưa có
    if os.path.dirname(log_file) and not os.path.exists(os.path.dirname(log_file)):
        os.makedirs(os.path.dirname(log_file))

    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Nếu logger đã có handler thì không thêm nữa
    if not logger.handlers:
        # Console
        ch = logging.StreamHandler()
        ch.setLevel(level)
        ch.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        logger.addHandler(ch)

        # File
        fh = logging.FileHandler(log_file)
        fh.setLevel(level)
        fh.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        logger.addHandler(fh)

        for h in logger.handlers:
            h.flush = h.flush if hasattr(h, 'flush') else lambda: None
    return logger
