from __future__ import annotations

import logging
import sqlite3
import time
import uuid
from pathlib import Path

import structlog
from flask import Flask, g, request
from structlog.dev import set_exc_info
from structlog.processors import JSONRenderer, StackInfoRenderer, \
    TimeStamper, format_exc_info


def init_logging(app: Flask) -> None:

    log_db = app.config.get("LOG_DB")
    if not log_db:
        return

    log_db_path = str(Path(app.instance_path) / log_db)
    print(log_db_path)

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.handlers[0].setLevel(logging.INFO)
    sh = SQLiteHandler(log_db_path)
    # sh.setLevel(logging.INFO)
    logger.addHandler(sh)

    processors = [
        StackInfoRenderer(),
        set_exc_info,
        format_exc_info,
        TimeStamper(fmt="%Y-%m-%d %H:%M.%S", utc=False),
        JSONRenderer(),
    ]

    structlog.configure(
        processors=processors,
        context_class=structlog.threadlocal.wrap_dict(dict),
        logger_factory=structlog.stdlib.LoggerFactory(),
    )

    @app.before_request
    def inject_request_id():
        request_id = str(uuid.uuid4())
        logger = structlog.get_logger(request_id=request_id, path=request.path)
        g.request_id = request_id

        logger.debug("Request started.")

    @app.after_request
    def log_end_of_request(response):
        logger = structlog.get_logger()
        logger.debug("Request ended successfully.")
        return response


class MyRenderer:
    key_order = ["request_id", "path", "user"]

    def __call__(self, _, __, event_dict):
        event = event_dict.pop("event")
        result = event
        items = self.ordered_items(event_dict)
        if items:
            result += " | " + " ".join(k + "=" + repr(v) for k, v in items)
        return result

    def ordered_items(self, event_dict):
        items = []
        for key in self.key_order:
            value = event_dict.pop(key, None)
            if value is not None:
                items.append((key, value))
        items += event_dict.items()
        return items


# class LogEntry(db.Model):
#     date = db.DateTime(nullable=False)
#     request_id = db.String(nullable=False)
#     _data = db.JSON(nullable=False)
#
#
# class DbLogger:
#     def msg(self, message):
#         entry = LogEntry()
#         print(message)
#
#
# class DbLoggerFactory:
#     def __call__(self, *args):
#         return DbLogger()

initial_sql = """CREATE TABLE IF NOT EXISTS log(
                    TimeStamp TEXT,
                    Source TEXT,
                    LogLevel INT,
                    LogLevelName TEXT,
                    Message TEXT,
                    Args TEXT,
                    Module TEXT,
                    FuncName TEXT,
                    LineNo INT,
                    Exception TEXT,
                    Process INT,
                    Thread TEXT,
                    ThreadName TEXT
               )"""

insertion_sql = """INSERT INTO log(
                    TimeStamp,
                    Source,
                    LogLevel,
                    LogLevelName,
                    Message,
                    Args,
                    Module,
                    FuncName,
                    LineNo,
                    Exception,
                    Process,
                    Thread,
                    ThreadName
               )
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
               """


class SQLiteHandler(logging.Handler):
    """Thread-safe logging handler for SQLite."""

    def __init__(self, db_file):
        logging.Handler.__init__(self)
        self.formatter = logging.Formatter()
        self.db_file = db_file
        conn = sqlite3.connect(db_file)
        conn.execute(initial_sql)
        conn.close()

    def format_time(self, record):
        """Create a time stamp."""
        record.dbtime = time.strftime(
            "%Y-%m-%d %H:%M:%S", time.localtime(record.created)
        )

    def emit(self, record):
        # self.format(record)
        self.format_time(record)
        if record.exc_info:  # for exceptions
            record.exc_text = self.formatter.formatException(record.exc_info)
        else:
            record.exc_text = ""

        # Insert the log record
        r = record
        value = (
            r.dbtime,
            r.name,
            r.levelno,
            r.levelname,
            r.msg,
            str(r.args),
            r.module,
            r.funcName,
            r.lineno,
            r.exc_text,
            r.process,
            r.thread,
            r.threadName,
        )
        conn = sqlite3.connect(self.db_file)
        conn.execute(insertion_sql, value)
        conn.close()
