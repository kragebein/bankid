'''Warden is a singleton structlogger. '''

import logging
import os
import sys
from traceback import walk_tb
from types import TracebackType
from typing import Any, Optional, Type, Union

import attrs
import orjson
import structlog
from structlog.processors import _json_fallback_handler as orjson_fallback_handler
from structlog.types import EventDict, WrappedLogger

DEBUG = logging.DEBUG
INFO = logging.INFO
WARN = logging.WARN
ERROR = logging.ERROR
EXCEPTION = logging.ERROR


ExcInfo = tuple[Type[BaseException], BaseException, Optional[TracebackType]]
OptExcInfo = Union[ExcInfo, tuple[None, None, None]]


@attrs.define
class Frame:
    filename: str
    lineno: int
    name: str
    line: str = ""
    locals: Optional[dict[str, str]] = None


@attrs.define
class SyntaxError_:  # pylint: disable=invalid-name
    offset: int
    filename: str
    line: str
    lineno: int
    msg: str


@attrs.define
class Stack:
    exc_type: str
    exc_value: str
    syntax_error: Optional[SyntaxError_] = None
    is_cause: bool = False
    frames: list[Frame] = attrs.field(factory=list)


@attrs.define
class Trace:
    stacks: list[Stack]


class Warden:
    loglevel: logging = logging.DEBUG
    application_name: str = None
    catch_all: bool = True

    log: structlog.BoundLogger = structlog.get_logger()

    instance = None

    def __new__(cls):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self):
        '''
        How-we-work compliant structured logger.
        When initialized, it is a good idea to set Warden.application_name and Warden.loglevel which defaults to respectively
        None and DEBUG.

        Warden will hook into excepthooks and log all exceptions. To disable set Warden.catch_all to False
        '''

        self._init()

        self.show_locals = False
        self.locals_max_string = 0
        if self.loglevel == logging.DEBUG:
            self.show_locals = True
            self.locals_max_string = 80
        self.max_frames = 50

    def _safe_str(self, _object: Any) -> str:
        """Don't allow exceptions from __str__ to propegate."""
        try:
            return str(_object)
        except Exception as error:
            return f"<str-error {str(error)!r}>"

    def _to_repr(self, obj: Any, max_string: Optional[int] = None) -> str:
        """Get repr string for an object, but catch errors."""
        if isinstance(obj, str):
            obj_repr = obj
        else:
            try:
                obj_repr = repr(obj)
            except Exception as error:
                obj_repr = f"<repr-error {str(error)!r}>"

        if max_string is not None and len(obj_repr) > max_string:
            truncated = len(obj_repr) - max_string
            obj_repr = f"{obj_repr[:max_string]!r}+{truncated}"

        return obj_repr

    def _extract(
        self,
        exc_type: Type[BaseException],
        exc_value: BaseException,
        traceback: Optional[TracebackType],
        *,
        locals_max_string: int = None,
    ) -> Trace:
        """
        Extract traceback information.
        Args:
            exc_type: Exception type.
            exc_value: Exception value.
            traceback: Python Traceback object.
            locals_max_string: Maximum length of string before truncating, or ``None`` to
                disable.
            max_frames: Maximum number of frames in each stack
        Returns:
            Trace: A Trace instance which you can use to construct a :cls:`Traceback`.
        """
        locals_max_string = self.locals_max_string
        stacks: list[Stack] = []
        is_cause = False

        while True:
            stack = Stack(
                exc_type=self._safe_str(exc_type.__name__),
                exc_value=self._safe_str(exc_value),
                is_cause=is_cause,
            )

            if isinstance(exc_value, SyntaxError):
                stack.syntax_error = SyntaxError_(
                    offset=exc_value.offset or 0,
                    filename=exc_value.filename or "?",
                    lineno=exc_value.lineno or 0,
                    line=exc_value.text or "",
                    msg=exc_value.msg,
                )

            stacks.append(stack)
            append = stack.frames.append  # pylint: disable=no-member

            for frame_summary, line_no in walk_tb(traceback):
                filename = frame_summary.f_code.co_filename
                if filename and not filename.startswith("<"):
                    filename = os.path.abspath(filename)
                frame = Frame(
                    filename=filename or "?",
                    lineno=line_no,
                    name=frame_summary.f_code.co_name,
                    locals={
                        key: self._to_repr(value, max_string=locals_max_string) for key, value in frame_summary.f_locals.items()
                    }
                    if self.show_locals
                    else None,
                )
                append(frame)

            cause = getattr(exc_value, "__cause__", None)
            if cause and cause.__traceback__:
                exc_type = cause.__class__
                exc_value = cause
                traceback = cause.__traceback__
                is_cause = True
                continue

            cause = exc_value.__context__
            if cause and cause.__traceback__ and not getattr(exc_value, "__suppress_context__", False):
                exc_type = cause.__class__
                exc_value = cause
                traceback = cause.__traceback__
                is_cause = False
                continue

            # No cover, code is reached but coverage doesn't recognize it.
            break  # pragma: no cover

        return Trace(stacks=stacks)

    def _get_exc_info(self, v: Any) -> OptExcInfo:
        """
        Return an exception info tuple for the input value.
        Args:
            v: Usually an :exc:`BaseException` instance or an exception tuple
                ``(exc_cls, exc_val, traceback)``.  If it is someting ``True``-ish, use
                :func:`sys.exc_info()` to get the exception info.
        Return:
            An exception info tuple or ``(None, None, None)`` if there was no exception.
        """
        if isinstance(v, BaseException):
            return (type(v), v, v.__traceback__)

        if isinstance(v, tuple):
            return v  # type: ignore

        if v:
            return sys.exc_info()

        return (None, None, None)

    def _get_traceback_dicts(
        self,
        exception: Any,
        locals_max_string: int = None,
        max_frames: int = None,
    ) -> list[dict[str, Any]]:
        """
        Return a list of exception stack dictionaries for *exception*.
        These dictionaries are based on :cls:`Stack` instances generated by
        :func:`extract()` and can be dumped to JSON.
        """
        if self.locals_max_string < 0:
            raise ValueError(f'"locals_max_string" must be >= 0: {locals_max_string}')
        if self.max_frames < 2:
            raise ValueError(f'"max_frames" must be >= 2: {max_frames}')

        exc_info = self._get_exc_info(exception)
        if exc_info == (None, None, None):
            return []

        trace = self._extract(*exc_info, locals_max_string=locals_max_string)

        for stack in trace.stacks:
            if len(stack.frames) <= max_frames:
                continue

            half = max_frames // 2  # Force int division to handle odd numbers correctly
            fake_frame = Frame(
                filename="",
                lineno=-1,
                name=f"Skipped frames: {len(stack.frames) - (2 * half)}",
            )
            stack.frames[:] = [*stack.frames[:half], fake_frame, *stack.frames[-half:]]

        return [attrs.asdict(stack) for stack in trace.stacks]

    def __render_orjson(self, _logger: WrappedLogger, _name: str, event_dict: EventDict) -> str:
        """
        Modified version of :class:`structlog.processors.JSONRenderer` that works around
        the issues in https://github.com/hynek/structlog/issues/360
        """
        exc_info = event_dict.pop("exc_info", None)
        if exc_info:
            event_dict["exception"] = self._get_traceback_dicts(exc_info)

        return orjson.dumps(event_dict, default=orjson_fallback_handler).decode()  # noqa: E1101

    def _how_we_work(self, _, __, event_dict) -> dict:
        '''Comply with standardization of structured logging'''
        sha = os.getenv('GIT_SHA', None)
        if sha:
            event_dict['git_commit'] = sha
        event_dict['application_name'] = self.application_name

        return event_dict

    def _init(self):

        processors = [
            self._how_we_work,
            structlog.processors.TimeStamper(fmt='iso'),
            structlog.processors.add_log_level,
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            # Transform event dict into `logging.Logger` method arguments.
            # "event" becomes "msg" and the rest is passed as a dict in
            # "extra". IMPORTANT: This means that the standard library MUST
            # render "extra" for the context to appear in log entries! See
            # warning below.
            #structlog.stdlib.render_to_log_kwargs,
        ]
        render = structlog.dev.ConsoleRenderer()
        if os.getenv('AWS', 'localdev') in ['production', 'prod', 'test', 'testing']:
            render = self.__render_orjson
        if os.getenv('JSON', '0') == '1':
            render = self.__render_orjson
        if os.getenv('CONSOLE', '0') == '1':
            render = structlog.dev.ConsoleRenderer()

        processors.append(render)

        structlog.configure(
            wrapper_class=structlog.make_filtering_bound_logger(self.loglevel),
            processors=processors,
            logger_factory=structlog.stdlib.LoggerFactory(),
        )
        formatter = structlog.stdlib.ProcessorFormatter(
           processors=[structlog.dev.ConsoleRenderer()],
        )
        #handler = logging.StreamHandler()
        # Use OUR `ProcessorFormatter` to format all `logging` entries.
        #handler.setFormatter(formatter)
        #root_logger = logging.getLogger()
        #root_logger.addHandler(handler)
        #root_logger.setLevel(self.loglevel)
        self.log = structlog.get_logger()

        # Catches uncaught exceptions
        if self.catch_all:
            sys.excepthook = self._handle_exception

    def _handle_exception(self, exc_type, exc_value, exc_traceback):
        '''Properly logs uncaught exceptions'''
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        self.log.exception("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

    def debug(self, msg, *args, **kwargs) -> None:
        '''Logs to logging.DEBUG'''
        self.log.debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs) -> None:
        '''Logs to logging.INFO'''
        self.log.info(msg, *args, **kwargs)

    def warn(self, msg, *args, **kwargs) -> None:
        '''Logs to logging.WARN'''
        self.log.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs) -> None:
        '''Logs to logging.ERROR'''
        self.log.error(msg, *args, **kwargs)

    def exception(self, msg, *args, **kwargs) -> None:
        '''Logs to Logging.ERROR'''
        self.log.exception(msg, *args, **kwargs)
