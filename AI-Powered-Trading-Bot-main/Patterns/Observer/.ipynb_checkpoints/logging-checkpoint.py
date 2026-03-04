import datetime
import os
from .observer import Observer


class LoggingObserver(Observer):
    """ Concrete Observer: saves log recording. 
    All trading activities are logged into a file. """
    
    def __init__(self, log_file: str = "trade_log.txt"):
        """
        Initialize the log file.
        Args:
            log_file (str): name of the log file
        """
        self.log_file = log_file
        #if not os.path.exists(self.log_file):
        try:
            with open(self.log_file, "w", encoding="utf-8") as f:
                f.write("="*70 + "\n")
                f.write("TRADING BOT LOG FILE\n")
                f.write("="*70 + "\n\n")
        except IOError as e:
            print(f"ERROR: Could not create log file ({self.log_file}): {e}")
            self.log_file = None 
        
        if self.log_file:
            print(f"[LOG] LoggingObserver initialized - Log target: {self.log_file}")
    
    def update(self, message: str):
        """
        Write log message to file
        Args:
            message (str): Message to be logged
        """
        if not self.log_file:
            print(f"⚠️ [LOG SKIPPED] No log file. Message: {message}")
            return

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                if message == "Simulation complete":
                    f.write(f"[{timestamp}] {message}\n")
                    f.write("-"*70 + "\n\n")
                else:
                    f.write(f"[{timestamp}] {message}\n")
            
            #print(f"[LOG] {message}")
            
        except IOError as e:
            print(f"ERROR: Could not write to log file ({self.log_file}): {e}")