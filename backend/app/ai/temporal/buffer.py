import collections
import numpy as np
from typing import List, Union, Optional

class LandmarkTemporalBuffer:
    """
    Temporal Landmark FIFO Buffer (Sliding Window):
    Maintains the latest 20-30 landmark vectors (each 63 features).
    Provides structured sequence arrays (N, 63) for future sequence models (LSTM, GRU, Transformer).
    """
    def __init__(self, max_capacity: int = 20):
        self.max_capacity = max_capacity
        self.buffer = collections.deque(maxlen=max_capacity)

    def add_frame(self, landmarks_63: Union[List[float], np.ndarray]):
        """Pushes a new 63-element landmark vector into the FIFO queue."""
        arr = np.array(landmarks_63, dtype=np.float32)
        if arr.shape[0] != 63:
            raise ValueError(f"Expected 63 features per frame, got {arr.shape[0]}")
        self.buffer.append(arr)

    def is_full(self) -> bool:
        """Returns True if buffer capacity (e.g. 20 frames) is reached."""
        return len(self.buffer) == self.max_capacity

    def get_sequence_matrix(self) -> np.ndarray:
        """
        Returns stacked 2D NumPy array of shape (N, 63).
        Ready for sequential dynamic gesture models.
        """
        if not self.buffer:
            return np.empty((0, 63), dtype=np.float32)
        return np.stack(list(self.buffer), axis=0)

    def clear(self):
        """Clears all buffered frames."""
        self.buffer.clear()

    def __len__(self) -> int:
        return len(self.buffer)
