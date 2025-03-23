import shutil
import os
from datetime import datetime
from typing import Optional
from .logging import logger
from .exception_handlers import exception_handler
from .email_utils import send_admin_email


@exception_handler()
def backup_database() -> Optional[str]:
    """
    Creates a backup of the database file by copying it to a backup directory.
    The backup file will overwrite any previous backup.

    :return: Path to the backup file if successful, None if an error occurs.
    """
    db_path: str = "instance/stefan.db"
    backup_dir: str = "instance/backup"
    now: datetime = datetime.now()
    formatted_now: str = now.strftime("%Y-%m-%d %H:%M:%S")

    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database file '{db_path}' does not exist.")

    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)

    db_name: str = os.path.basename(db_path)
    backup_path: str = os.path.join(backup_dir, f"backup_{db_name}")

    shutil.copy2(db_path, backup_path)
    logger.info(f"Database backup saved: {backup_path}")
    send_admin_email(
        "Database backup saved",
        f"StefanCryptoTradingBot\nDaily backup_database report.\n{formatted_now}\n\nDatabase backup saved successfully.\nDatabase backup path: {backup_path}",
    )
    return backup_path
