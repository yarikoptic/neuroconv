"""Author: Cody Baker."""
import math
from typing import Optional

import numpy as np

from ..utils import ArrayType


def get_rising_frames_from_ttl(trace: np.ndarray, threshold: Optional[float] = None) -> np.ndarray:
    """
    Return the frame indices for rising events in a TTL pulse.

    Parameters
    ----------
    trace : numpy.ndarray
        A TTL signal.
    threshold : float, optional
        The threshold used to distinguish on/off states in the trace.
        The mean of the trace is used by default.

    Returns
    -------
    rising_frames : numpy.ndarray
        The frame indices of rising events.
    """
    if math.prod(trace.shape[1:]) != 1:
        raise ValueError(f"This function expects a one-dimensional array! Received shape of {trace.shape}.")
    flattened_trace = np.ravel(trace)

    threshold = threshold if threshold is not None else np.mean(trace)

    sign = np.sign(flattened_trace - threshold)
    diff = np.diff(sign)
    rising_frames = np.where(diff > 0)[0] + 1

    return rising_frames


def get_falling_frames_from_ttl(trace: np.ndarray, threshold: Optional[float] = None) -> np.ndarray:
    """
    Return the frame indices for falling events in a TTL pulse.

    Parameters
    ----------
    trace : numpy.ndarray
        A TTL signal.
    threshold : float, optional
        The threshold used to distinguish on/off states in the trace.
        The mean of the trace is used by default.

    Returns
    -------
    falling_frames : numpy.ndarray
        The frame indices of falling events.
    """
    if math.prod(trace.shape[1:]) != 1:
        raise ValueError(f"This function expects a one-dimensional array! Received shape of {trace.shape}.")
    flattened_trace = np.ravel(trace)

    threshold = threshold if threshold is not None else np.mean(trace)

    sign = np.sign(flattened_trace - threshold)
    diff = np.diff(sign)
    falling_frames = np.where(diff < 0)[0] + 1

    return falling_frames
