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
        self.file_processing_times = {}  # Track when we processed each file
        
        # Commission statement file patterns
        self.commission_patterns = [
            'commission', 'commision', 'statement', 'stmt', 'payment', 'earnings',
            'producer', 'agent', 'aetna', 'blue_cross', 'cigna', 
            'unitedhealth', 'anthem', 'humana', 'kaiser', 'hne'
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
            
            # Get file modification time to avoid processing same file multiple times
            try:
                current_mtime = os.path.getmtime(file_path)
            except OSError:
                return  # File might be deleted or inaccessible
            
            # Check if we've recently processed this file (within last 5 minutes)
            current_time = datetime.now().timestamp()
            recent_threshold = current_time - 300  # 5 minutes ago
            
            if (file_path in self.processed_files and 
                file_path in self.file_processing_times and
                self.file_processing_times[file_path] >= recent_threshold):
                self.logger.debug(f"Skipping recently processed file: {os.path.basename(file_path)} (last processed: {datetime.fromtimestamp(self.file_processing_times[file_path]).strftime('%H:%M:%S')})")
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
            
            filename = os.path.basename(file_path_lower)
            
            # Exclude enrollment and system files
            excluded_patterns = ['enrollment', 'llm_integration', 'readme', 'config']
            if any(pattern in filename for pattern in excluded_patterns):
                return False
            
            # Check filename for commission-related keywords
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
            
            # Record when we processed this file
            current_time = datetime.now().timestamp()
            self.file_processing_times[file_path] = current_time
            
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
        cutoff_time = datetime.now().timestamp() - (max_age_hours * 3600)
        
        # Clean up old processing times
        old_files = [f for f, ptime in self.file_processing_times.items() if ptime < cutoff_time]
        for file_path in old_files:
            self.file_processing_times.pop(file_path, None)
            self.processed_files.discard(file_path)
        
        # Prevent memory buildup - clean if too many entries
        if len(self.processed_files) > 1000:
            self.processed_files.clear()
            self.file_processing_times.clear()


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
        """Main processing loop that handles queued files with batch processing"""
        self.logger.info("[LOOP] Processing loop started")
        batch_files = []
        last_activity = None
        batch_timeout = 10  # seconds to wait for more files before processing batch
        
        while self.is_running:
            try:
                # Wait for files to process with timeout
                try:
                    file_event = self.processing_queue.get(timeout=2)
                    
                    # Check for sentinel value (stop signal)
                    if file_event is None:
                        # Process any remaining files in batch before stopping
                        if batch_files:
                            self._process_commission_batch(batch_files)
                        break
                    
                    # Add file to batch
                    batch_files.append(file_event)
                    last_activity = time.time()
                    
                    filename = os.path.basename(file_event['file_path'])
                    self.logger.info(f"[BATCH] Added to processing batch: {filename} (batch size: {len(batch_files)})")
                    
                except queue.Empty:
                    # No new files - check if we should process current batch
                    if batch_files and last_activity:
                        time_since_last = time.time() - last_activity
                        if time_since_last >= batch_timeout:
                            self.logger.info(f"[BATCH] Timeout reached, processing batch of {len(batch_files)} files")
                            self._process_commission_batch(batch_files)
                            batch_files = []
                            last_activity = None
                    continue
                    
            except Exception as e:
                self.logger.error(f"[ERROR] Error in processing loop: {e}")
                continue
        
        self.logger.info("[LOOP] Processing loop stopped")
    
    def _process_commission_batch(self, batch_files):
        """Process a batch of commission statement files together"""
        try:
            if not batch_files:
                return
            
            filenames = [os.path.basename(f['file_path']) for f in batch_files]
            self.logger.info(f"[BATCH] Processing batch of {len(batch_files)} commission statements:")
            for filename in filenames:
                self.logger.info(f"[BATCH]   • {filename}")
            
            # Log the batch event details
            for file_event in batch_files:
                event_type = file_event['event_type']
                timestamp = file_event['timestamp']
                filename = os.path.basename(file_event['file_path'])
                self.logger.info(f"[EVENT] File: {filename}, Event: {event_type} at {timestamp.strftime('%H:%M:%S')}")
            
            # Import and run the main reconciliation process once for all files
            from main import run_reconciliation_workflow
            
            success = run_reconciliation_workflow()
            
            if success:
                self.logger.info(f"[SUCCESS] Successfully processed batch of {len(batch_files)} commission statements")
                self.logger.info("[EMAIL] Single consolidated report generated and emailed to stakeholders")
            else:
                self.logger.error(f"[FAILED] Failed to process commission statement batch")
            
        except Exception as e:
            self.logger.error(f"[ERROR] Error processing commission batch: {e}")
    
    def _process_commission_file(self, file_event):
        """Process a single commission statement file (legacy method for compatibility)"""
        self._process_commission_batch([file_event])
    
    def get_status(self):
        """Get current monitoring status"""
        return {
            'is_monitoring': self.is_running and self.observer.is_alive(),
            'watch_directory': self.watch_directory,
            'queue_size': self.processing_queue.qsize(),
            'processed_files_count': len(self.file_handler.processed_files)
        }
    
    def manual_scan(self):
        """Manually scan the docs directory for any existing files and batch process them"""
        self.logger.info("[SCAN] Performing manual scan of docs directory...")
        
        try:
            scan_files = []
            for file_path in Path(self.watch_directory).rglob('*'):
                if file_path.is_file() and self.file_handler._is_commission_statement(str(file_path)):
                    scan_files.append({
                        'file_path': str(file_path),
                        'event_type': "MANUAL_SCAN",
                        'timestamp': datetime.now(),
                        'file_size': os.path.getsize(str(file_path))
                    })
            
            # If we found commission files, process them as a single batch
            if scan_files:
                self.logger.info(f"[SCAN] Found {len(scan_files)} commission statements for batch processing")
                self._process_commission_batch(scan_files)
                
                # Mark files as processed to avoid duplicate processing
                current_time = datetime.now().timestamp()
                for file_event in scan_files:
                    file_path = file_event['file_path']
                    self.file_handler.processed_files.add(file_path)
                    self.file_handler.file_processing_times[file_path] = current_time
            
            self.logger.info("[SCAN] Manual scan completed")
            
        except Exception as e:
            self.logger.error(f"[ERROR] Error during manual scan: {e}")
    
    def _process_commission_batch(self, batch_files):
        """Process a batch of commission statement files at the monitor level"""
        try:
            if not batch_files:
                return
            
            filenames = [os.path.basename(f['file_path']) for f in batch_files]
            self.logger.info(f"[BATCH] Processing batch of {len(batch_files)} commission statements:")
            for filename in filenames:
                self.logger.info(f"[BATCH]   • {filename}")
            
            # Log the batch event details
            for file_event in batch_files:
                event_type = file_event['event_type']
                timestamp = file_event['timestamp']
                filename = os.path.basename(file_event['file_path'])
                self.logger.info(f"[EVENT] File: {filename}, Event: {event_type} at {timestamp.strftime('%H:%M:%S')}")
            
            # Import and run the main reconciliation process once for all files
            from main import run_reconciliation_workflow
            
            success = run_reconciliation_workflow()
            
            if success:
                self.logger.info(f"[SUCCESS] Successfully processed batch of {len(batch_files)} commission statements")
                self.logger.info("[EMAIL] Single consolidated report generated and emailed to stakeholders")
            else:
                self.logger.error(f"[FAILED] Failed to process commission statement batch")
            
        except Exception as e:
            self.logger.error(f"[ERROR] Error processing commission batch: {e}")


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