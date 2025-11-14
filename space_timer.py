import sys
import time
import tty
import termios
from typing import Optional, List, Any

class SpaceTimer:
    
    def __init__(self, pause_threshold: float = 1.0) -> None:
        self.pause_threshold: float = pause_threshold
        self.last_space_time: Optional[float] = None
        self.current_stroke_count: int = 0
        self.last_sequence_count: int = 0  
        self._old_termios_settings: Optional[List[Any]] = None 

    def _platform_get_char(self) -> bytes:
        return sys.stdin.read(1).encode('utf-8') 

    def _platform_setup(self) -> None:
        fd = sys.stdin.fileno()
        try:
            self._old_termios_settings = termios.tcgetattr(fd)
        except termios.error:
            self._old_termios_settings = None
            print("Warning: Could not get terminal attributes.", file=sys.stderr)
            return

        try:
            tty.setcbreak(fd)
        except termios.error:
            print("Warning: Could not set terminal to cbreak mode.", file=sys.stderr)
            self._old_termios_settings = None 

    def _platform_cleanup(self) -> None:
        if self._old_termios_settings:
            fd = sys.stdin.fileno()
            termios.tcsetattr(fd, termios.TCSADRAIN, self._old_termios_settings)
            
    def get_last_sequence_count(self) -> int:
        return self.last_sequence_count

    def run(self) -> int:
        print(f"Start typing spaces. A pause > {self.pause_threshold:.1f}s between spaces will stop.")
        print("Pressing any other key or Ctrl+C will also stop.")
        
        self._platform_setup() 
        self.current_stroke_count = 0
        self.last_sequence_count = 0
        self.last_space_time = None 

        try:
            while True:
                char = self._platform_get_char()
                current_time = time.time()
                
                if char == b' ':
                    if self.last_space_time is None:
                        self.current_stroke_count = 1
                        sys.stdout.write(f"\r[Sequence started: 1]   ")
                        sys.stdout.write('\a')
                        
                    else:
                        time_delta = current_time - self.last_space_time
                        
                        if time_delta >= self.pause_threshold:
                            sys.stdout.write(f"\n--- Slow stroke (>{self.pause_threshold:.1f}s). Sequence ended. ---")
                            self.last_sequence_count = self.current_stroke_count
                            break 
                        else:
                            self.current_stroke_count += 1
                            sys.stdout.write(f"\r[Current sequence: {self.current_stroke_count}]   ")
                            sys.stdout.write('\a')
                    
                    self.last_space_time = current_time
                    sys.stdout.flush()

                elif char == b'\x03':
                    print("\n--- Interrupted ---")
                    if self.current_stroke_count > 0:
                        self.last_sequence_count = self.current_stroke_count
                    break 
                    
                else:
                    # Handle non-space characters
                    if self.current_stroke_count > 0 and self.last_space_time is not None:
                        # Check if too much time has passed since last space
                        time_delta = current_time - self.last_space_time
                        if time_delta >= self.pause_threshold:
                            sys.stdout.write(f"\n--- Slow stroke (>{self.pause_threshold:.1f}s). Sequence ended. ---")
                            self.last_sequence_count = self.current_stroke_count
                            break 
                        else:
                            # Update the delta time but don't interrupt the sequence
                            self.last_space_time = current_time
                            sys.stdout.write(f"\r[Current sequence: {self.current_stroke_count}] (non-space key pressed)   ")
                            sys.stdout.flush()
                    else:
                        sys.stdout.write(f"\r[Non-space key. Waiting for spaces...]   ")
                        sys.stdout.flush()

        except KeyboardInterrupt:
            print("\n--- Interrupted (KB) ---")
            if self.current_stroke_count > 0:
                self.last_sequence_count = self.current_stroke_count
            pass
        except Exception as e:
            print(f"\nAn error occurred: {e}", file=sys.stderr)
        finally:
            self._platform_cleanup()
            print(f"\n\n--- Stopping ---")
            
            print(f"Final sequence count: {self.last_sequence_count}")

        return self.last_sequence_count


if __name__ == "__main__":
    timer = SpaceTimer()
    final_count = timer.run()
    print(f"Last recorded sequence count: {final_count}")
