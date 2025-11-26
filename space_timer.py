import sys
import time
import tty
import termios
import select
from typing import Optional, List, Any

class SpaceTimer:
    
    def __init__(self, pause_threshold: float = 1.5) -> None:
        self.pause_threshold: float = pause_threshold
        self.last_space_time: Optional[float] = None
        self.current_stroke_count: int = 0
        self.last_sequence_count: int = 0  
        self._old_termios_settings: Optional[List[Any]] = None 

    def _platform_get_char(self, timeout: float = 0.1) -> Optional[bytes]:
        if select.select([sys.stdin], [], [], timeout)[0]:
            return sys.stdin.read(1).encode('utf-8')
        return None

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
        print(f"Start typing spaces. A pause > {self.pause_threshold:.1f}s will automatically end the sequence.")
        print("Pressing Ctrl+C will stop the program or simply waiting a brief while after pressing any key after startiing a space bar sequence.")
        
        self._platform_setup() 
        self.current_stroke_count = 0
        self.last_sequence_count = 0
        self.last_space_time = None 

        try:
            while True:
                current_time = time.time()
                
                if (self.last_space_time is not None and 
                    self.current_stroke_count > 0 and 
                    current_time - self.last_space_time >= self.pause_threshold):
                    
                    sys.stdout.write(f"\n--- Sequence ended after {self.pause_threshold:.1f}s pause ---")
                    return self.current_stroke_count
                
                char = self._platform_get_char(timeout=0.1)
                
                if char is None:
                    continue
                
                if char == b' ':
                    current_time = time.time() 
                    
                    if self.last_space_time is None or self.current_stroke_count == 0:
                        self.current_stroke_count = 1
                        sys.stdout.write(f"\r[Sequence started: 1]   ")
                        sys.stdout.write('\a')
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
                    if self.current_stroke_count > 0:
                        current_time = time.time() 
                        self.last_space_time = current_time
                        sys.stdout.write(f"\r[Current sequence: {self.current_stroke_count}] (non-space ignored)   ")
                    else:
                        sys.stdout.write(f"\r[Waiting for spaces...]   ")
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
            
            if self.last_sequence_count > 0:
                print(f"Last recorded sequence count: {self.last_sequence_count}")

        return self.last_sequence_count


if __name__ == "__main__":
    timer = SpaceTimer()
    final_count = timer.run()
    print(f"Last recorded sequence count: {final_count}")
