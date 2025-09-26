"""
File Monitor Service
Automatically triggers commission reconciliation when new commission statements are added to docs folder
"""

import os
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading
import queue


class CommissionFileHandler(FileSystemEventHandler):
    """Handler for file system events related to commission statements"""
    
    def __init__(self, processing_queue, logger):
        super().__init__()
        self.processing_queue = processing_queue
        self.logger = logger
        self.processed_files = set()  # Track recently processed files
        self.file_timers = {}  # Track file modification timers
        
        # Commission statement file patterns
        self.commission_patterns = [
            'commission', 'statement', 'payment', 'earnings',
            'producer', 'agent', 'aetna', 'blue_cross', 'cigna', 
            'unitedhealth', 'anthem', 'humana', 'kaiser'
        ]
        
        self.valid_extensions = ['.pdf', '.xlsx', '.xls', '.csv']
    
    def on_created(self, event):
        """Handle file creation events"""
        if not event.is_directory:
            self._handle_file_event(event.src_path, "CREATED")
    
    def on_modified(self, event):
        """Handle file modification events"""
        if not event.is_directory:
            self._handle_file_event(event.src_path, "MODIFIED")
    
    def on_moved(self, event):
        """Handle file move/rename events"""
        if not event.is_directory:
            self._handle_file_event(event.dest_path, "MOVED")
    
    def _handle_file_event(self, file_path, event_type):
        """Process file system events for commission statements"""
        try:
            # Check if file is a commission statement
            if not self._is_commission_statement(file_path):
                return
            
            # Avoid duplicate processing of the same file
            if file_path in self.processed_files:
                return
            
            # Cancel existing timer for this file if it exists
            if file_path in self.file_timers:
                self.file_timers[file_path].cancel()
            
            # Set a small delay to ensure file is fully written
            timer = threading.Timer(2.0, self._queue_file_for_processing, [file_path, event_type])
            self.file_timers[file_path] = timer
            timer.start()
            
        except Exception as e:
            self.logger.error(f"Error handling file event for {file_path}: {e}")
    
    def _is_commission_statement(self, file_path):
        """Check if file is likely a commission statement"""
        try:
            # Check file extension
            file_path_lower = file_path.lower()
            if not any(file_path_lower.endswith(ext) for ext in self.valid_extensions):
                return False
            
            # Check filename for commission-related keywords
            filename = os.path.basename(file_path_lower)
            has_commission_keyword = any(pattern in filename for pattern in self.commission_patterns)
            
            # Check file size (avoid empty or tiny files)
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                if file_size < 1024:  # Less than 1KB
                    return False
            
            return has_commission_keyword
            
        except Exception as e:
            self.logger.error(f"Error checking file type for {file_path}: {e}")
            return False
    
    def _queue_file_for_processing(self, file_path, event_type):
        """Queue file for processing"""
        try:
            # Double-check file still exists and is complete
            if not os.path.exists(file_path):
                return
            
            # Add to processed files set
            self.processed_files.add(file_path)
            
            # Add to processing queue
            self.processing_queue.put({
                'file_path': file_path,
                'event_type': event_type,
                'timestamp': datetime.now(),
                'file_size': os.path.getsize(file_path)
            })
            
            filename = os.path.basename(file_path)
            self.logger.info(f"[NEW FILE] Commission statement detected: {filename} ({event_type})")
            
            # Clean up timer reference
            if file_path in self.file_timers:
                del self.file_timers[file_path]
                
        except Exception as e:
            self.logger.error(f"Error queueing file {file_path}: {e}")
    
    def cleanup_processed_files(self, max_age_hours=24):
        """Clean up old entries from processed files set"""
        # Remove files from processed set after specified hours
        # This allows reprocessing of files that might be updated later
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        # For now, we'll just clear the set periodically
        if len(self.processed_files) > 1000:  # Prevent memory buildup
            self.processed_files.clear()


class AutoCommissionMonitor:
    """
    Automated Commission Statement Monitor
    Watches docs folder and triggers reconciliation when new statements are added
    """
    
    def __init__(self, watch_directory="docs", processing_delay=5):
        self.watch_directory = os.path.abspath(watch_directory)
        self.processing_delay = processing_delay  # Seconds to wait before processing
        self.logger = logging.getLogger(__name__)
        
        # Create processing queue
        self.processing_queue = queue.Queue()
        
        # Initialize file handler
        self.file_handler = CommissionFileHandler(self.processing_queue, self.logger)
        
        # Initialize observer
        self.observer = Observer()
        self.observer.schedule(self.file_handler, self.watch_directory, recursive=True)
        
        # Processing control
        self.is_running = False
        self.processing_thread = None
        
        # Ensure watch directory exists
        os.makedirs(self.watch_directory, exist_ok=True)
        
    def start_monitoring(self):
        """Start the file monitoring service"""
        try:
            self.logger.info(f"[MONITOR] Starting commission statement monitor for: {self.watch_directory}")
            
            # Start file system observer
            self.observer.start()
            
            # Start processing thread
            self.is_running = True
            self.processing_thread = threading.Thread(target=self._processing_loop, daemon=True)
            self.processing_thread.start()
            
            self.logger.info("[SUCCESS] Commission statement monitor started successfully")
            self.logger.info("[WATCHING] Monitoring for new commission statements...")
            self.logger.info("[AUTO] System will automatically process new files and send reports")
            
            return True
            
        except Exception as e:
            self.logger.error(f"[ERROR] Failed to start commission monitor: {e}")
            return False
    
    def stop_monitoring(self):
        """Stop the file monitoring service"""
        try:
            self.logger.info("[STOP] Stopping commission statement monitor...")
            
            # Stop processing
            self.is_running = False
            
            # Stop file system observer
            if self.observer.is_alive():
                self.observer.stop()
                self.observer.join(timeout=5)
            
            # Signal processing thread to stop
            self.processing_queue.put(None)  # Sentinel value
            
            if self.processing_thread and self.processing_thread.is_alive():
                self.processing_thread.join(timeout=10)
            
            self.logger.info("[SUCCESS] Commission statement monitor stopped")
            
        except Exception as e:
            self.logger.error(f"[ERROR] Error stopping monitor: {e}")
    
    def _processing_loop(self):
        """Main processing loop that handles queued files"""
        self.logger.info("[LOOP] Processing loop started")
        
        while self.is_running:
            try:
                # Wait for files to process
                file_event = self.processing_queue.get(timeout=1)
                
                # Check for sentinel value (stop signal)
                if file_event is None:
                    break
                
                # Process the commission statement
                self._process_commission_file(file_event)
                
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"[ERROR] Error in processing loop: {e}")
                continue
        
        self.logger.info("[LOOP] Processing loop stopped")
    
    def _process_commission_file(self, file_event):
        """Process a single commission statement file"""
        file_path = file_event['file_path']
        event_type = file_event['event_type']
        timestamp = file_event['timestamp']
        
        try:
            filename = os.path.basename(file_path)
            self.logger.info(f"[PROCESS] Processing commission statement: {filename}")
            self.logger.info(f"[EVENT] File event: {event_type} at {timestamp.strftime('%H:%M:%S')}")
            
            # Import and run the main reconciliation process
            from main import run_reconciliation_workflow
            
            success = run_reconciliation_workflow()
            
            if success:
                self.logger.info(f"[SUCCESS] Successfully processed commission statement: {filename}")
                self.logger.info("[EMAIL] Reports generated and emailed to stakeholders")
            else:
                self.logger.error(f"[FAILED] Failed to process commission statement: {filename}")
            
        except Exception as e:
            self.logger.error(f"[ERROR] Error processing commission file {file_path}: {e}")
    
    def get_status(self):
        """Get current monitoring status"""
        return {
            'is_monitoring': self.is_running and self.observer.is_alive(),
            'watch_directory': self.watch_directory,
            'queue_size': self.processing_queue.qsize(),
            'processed_files_count': len(self.file_handler.processed_files)
        }
    
    def manual_scan(self):
        """Manually scan the docs directory for any existing files"""
        self.logger.info("[SCAN] Performing manual scan of docs directory...")
        
        try:
            for file_path in Path(self.watch_directory).rglob('*'):
                if file_path.is_file():
                    self.file_handler._handle_file_event(str(file_path), "MANUAL_SCAN")
            
            self.logger.info("[SCAN] Manual scan completed")
            
        except Exception as e:
            self.logger.error(f"[ERROR] Error during manual scan: {e}")


def setup_monitoring_logging():
    """Setup logging specifically for the monitoring service"""
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Create dedicated logger for monitoring
    monitor_logger = logging.getLogger('commission_monitor')
    monitor_logger.setLevel(logging.INFO)
    
    # Create file handler for monitoring logs
    monitor_log_file = os.path.join(log_dir, f'commission_monitor_{datetime.now().strftime("%Y%m%d")}.log')
    file_handler = logging.FileHandler(monitor_log_file)
    file_handler.setLevel(logging.INFO)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers to logger
    monitor_logger.addHandler(file_handler)
    monitor_logger.addHandler(console_handler)
    
    return monitor_logger


if __name__ == "__main__":
    """Run the monitoring service standalone"""
    import signal
    import sys
    
    # Setup logging
    monitor_logger = setup_monitoring_logging()
    
    # Create and start monitor
    monitor = AutoCommissionMonitor()
    
    def signal_handler(sig, frame):
        monitor_logger.info('📥 Received interrupt signal...')
        monitor.stop_monitoring()
        sys.exit(0)
    
    # Handle graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start monitoring
    if monitor.start_monitoring():
        monitor_logger.info("🎯 Commission Statement Auto-Monitor is running!")
        monitor_logger.info("📁 Drop commission statements into the 'docs' folder to trigger automatic processing")
        monitor_logger.info("⚡ Press Ctrl+C to stop monitoring")
        
        try:
            # Keep the main thread alive
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            monitor_logger.info("📥 Keyboard interrupt received")
        finally:
            monitor.stop_monitoring()
    else:
        monitor_logger.error("❌ Failed to start commission statement monitor")
        sys.exit(1)