"""
FFmpeg-Related Exceptions.

Exceptions for FFmpeg operations, conversion errors,
and FFmpeg installation issues.
"""

from typing import Optional

from dml_stream.exceptions.base import DMLBaseException


class FFmpegError(DMLBaseException):
    """
    Base exception for FFmpeg-related errors.
    
    This includes:
    - FFmpeg execution failures
    - Conversion errors
    - Stream probing failures
    
    Attributes:
        message: Error message.
        command: Optional FFmpeg command that failed.
        output: Optional FFmpeg output/error message.
    """

    def __init__(
        self,
        message: str,
        command: Optional[str] = None,
        output: Optional[str] = None,
    ) -> None:
        """
        Initialize FFmpeg error.
        
        Args:
            message: Error message.
            command: Optional command that failed.
            output: Optional FFmpeg output.
        """
        super().__init__(message)
        self.command = command
        self.output = output


class ConversionError(FFmpegError):
    """
    Raised when a media conversion fails.
    
    This includes:
    - Format conversion failures
    - Codec encoding failures
    - Merge operation failures
    - Audio extraction failures
    """

    def __init__(
        self,
        message: str = "Conversion failed",
        command: Optional[str] = None,
        output: Optional[str] = None,
        input_path: Optional[str] = None,
        output_path: Optional[str] = None,
    ) -> None:
        """
        Initialize conversion error.
        
        Args:
            message: Error message.
            command: Optional command that failed.
            output: Optional FFmpeg output.
            input_path: Optional input file path.
            output_path: Optional output file path.
        """
        super().__init__(message, command, output)
        self.input_path = input_path
        self.output_path = output_path


class FFmpegNotFoundError(DMLBaseException):
    """
    Raised when FFmpeg is not found in the system PATH.
    
    FFmpeg is required for:
    - Merging video and audio streams
    - Format conversion
    - Audio extraction
    - Media probing
    """

    def __init__(
        self,
        message: Optional[str] = None,
    ) -> None:
        """
        Initialize FFmpeg not found error.
        
        Args:
            message: Optional custom error message.
        """
        default_message = (
            "FFmpeg is required for this operation but was not found in the system PATH. "
            "Please install FFmpeg from https://ffmpeg.org/download.html and ensure it's "
            "added to your system PATH."
        )
        super().__init__(message or default_message)


class FFmpegVersionError(DMLBaseException):
    """
    Raised when FFmpeg version is incompatible.
    
    This includes:
    - Version too old for required features
    - Missing required codecs
    - Broken FFmpeg installation
    """

    def __init__(
        self,
        message: str = "Incompatible FFmpeg version",
        required_version: Optional[str] = None,
        found_version: Optional[str] = None,
    ) -> None:
        """
        Initialize FFmpeg version error.
        
        Args:
            message: Error message.
            required_version: Optional minimum required version.
            found_version: Optional detected version.
        """
        super().__init__(message)
        self.required_version = required_version
        self.found_version = found_version
