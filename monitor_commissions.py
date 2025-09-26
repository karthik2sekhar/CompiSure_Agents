"""
Commission Statement Auto-Monitor
Run this script to start automatic processing of commission statements

This script will:
1. Monitor the 'docs' folder for new commission statements
2. Automatically trigger the reconciliation process when files are added
3. Generate and email reports automatically
4. Run continuously until stopped

Usage:
    python monitor_commissions.py

The system will automatically:
- Detect PDF, Excel, and CSV commission statements
- Process them using AI-powered extraction
- Generate variance reports
- Email reports to stakeholders
- Log all activities
"""

import os
import sys
import logging
import signal
import time
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.file_monitor import AutoCommissionMonitor, setup_monitoring_logging


class CommissionMonitorApp:
    """Main application for running the commission statement monitor"""
    
    def __init__(self):
        self.monitor = None
        self.logger = None
        self.is_running = False
    
    def setup_logging(self):
        """Setup application logging"""
        # Create logs directory
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Setup main logger
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(os.path.join(log_dir, f'monitor_app_{datetime.now().strftime("%Y%m%d")}.log')),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        
        # Also setup monitoring-specific logging
        setup_monitoring_logging()
    
    def display_banner(self):
        """Display startup banner"""
        banner = """
================================================================================
                    COMMISSION STATEMENT AUTO-MONITOR                      
                                                                              
  AI-Powered Automated Commission Reconciliation System                      
  • Monitors docs folder for new commission statements                       
  • Processes files using GPT-3.5 for intelligent extraction                
  • Generates variance reports automatically                                 
  • Emails reports to stakeholders                                          
                                                                              
  Status: READY FOR PRODUCTION                                               
================================================================================
        """
        print(banner)
        self.logger.info("Commission Statement Auto-Monitor starting up...")
    
    def display_instructions(self):
        """Display usage instructions"""
        instructions = """
INSTRUCTIONS:
   1. Drop commission statement files into the 'docs' folder
   2. Supported formats: PDF, Excel (.xlsx/.xls), CSV
   3. System will automatically detect and process new files
   4. Reports will be generated and emailed automatically
   5. All activities are logged in the 'logs' folder

MONITORING ACTIVE:
   • Watching: {watch_dir}
   • Pattern matching: commission, statement, payment, carrier names
   • Auto-processing: Enabled with AI extraction
   • Email reports: Configured and ready

CONTROLS:
   • Press Ctrl+C to stop monitoring
   • View logs in real-time for processing status
   • Check 'reports' folder for generated reports

        """.format(watch_dir=os.path.abspath('docs'))
        
        print(instructions)
        self.logger.info("System instructions displayed")
    
    def setup_signal_handlers(self):
        """Setup graceful shutdown handlers"""
        def signal_handler(sig, frame):
            signal_name = "SIGINT" if sig == signal.SIGINT else "SIGTERM"
            self.logger.info(f'[SHUTDOWN] Received {signal_name} signal - initiating graceful shutdown...')
            self.shutdown()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def check_dependencies(self):
        """Check if all required dependencies are available"""
        try:
            # Check if all required dependencies are available
            import pandas
            import pdfplumber
            import openai
            import matplotlib
            import seaborn
            import smtplib
            from watchdog.observers import Observer
            
            self.logger.info("[SUCCESS] All dependencies verified")
            return True
            
        except ImportError as e:
            self.logger.error(f"[ERROR] Missing dependency: {e}")
            print(f"\n[ERROR] Missing required dependency: {e}")
            print("Please run: pip install -r requirements.txt")
            return False
    
    def check_configuration(self):
        """Check if system is properly configured"""
        try:
            # Check if docs directory exists
            docs_dir = "docs"
            if not os.path.exists(docs_dir):
                os.makedirs(docs_dir)
                self.logger.info(f"[SETUP] Created docs directory: {docs_dir}")
            
            # Check for OpenAI API key
            if not os.getenv('OPENAI_API_KEY'):
                self.logger.warning("[WARNING] OPENAI_API_KEY environment variable not set")
                print("[WARNING] OPENAI_API_KEY not configured. LLM extraction may not work.")
            
            # Check for email configuration
            if not os.getenv('SENDER_PASSWORD'):
                self.logger.warning("[WARNING] SENDER_PASSWORD environment variable not set")
                print("[WARNING] SENDER_PASSWORD not configured. Email reports may not work.")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Configuration error: {e}")
            return False
    
    def start_monitoring(self):
        """Start the commission statement monitoring service"""
        try:
            # Create monitor instance
            self.monitor = AutoCommissionMonitor(
                watch_directory="docs",
                processing_delay=3  # 3 second delay to ensure files are fully written
            )
            
            # Start monitoring
            if self.monitor.start_monitoring():
                self.is_running = True
                self.logger.info("[SUCCESS] Commission statement monitor started successfully")
                
                # Perform initial scan of existing files
                self.monitor.manual_scan()
                
                return True
            else:
                self.logger.error("[ERROR] Failed to start commission statement monitor")
                return False
            
        except Exception as e:
            self.logger.error(f"[ERROR] Error starting monitor: {e}")
            return False
    
    def run_monitoring_loop(self):
        """Main monitoring loop"""
        self.logger.info("[LOOP] Entering main monitoring loop")
        
        try:
            last_status_report = time.time()
            status_interval = 300  # Report status every 5 minutes
            
            while self.is_running:
                # Check if monitor is still running
                if not self.monitor or not self.monitor.get_status()['is_monitoring']:
                    self.logger.error("[ERROR] Monitor stopped unexpectedly")
                    break
                
                # Periodic status report
                current_time = time.time()
                if current_time - last_status_report >= status_interval:
                    status = self.monitor.get_status()
                    self.logger.info(f"[STATUS] Queue={status['queue_size']}, Processed={status['processed_files_count']}")
                    last_status_report = current_time
                
                # Sleep to prevent busy waiting
                time.sleep(1)
                
        except KeyboardInterrupt:
            self.logger.info("[INTERRUPT] Keyboard interrupt received in monitoring loop")
        except Exception as e:
            self.logger.error(f"[ERROR] Error in monitoring loop: {e}")
    
    def shutdown(self):
        """Gracefully shutdown the monitoring service"""
        self.logger.info("[SHUTDOWN] Shutting down commission statement monitor...")
        
        self.is_running = False
        
        if self.monitor:
            self.monitor.stop_monitoring()
        
        self.logger.info("[SUCCESS] Commission statement monitor shutdown complete")
        print("\n[SUCCESS] Commission Statement Auto-Monitor stopped successfully")
    
    def run(self):
        """Main application entry point"""
        try:
            # Setup logging
            self.setup_logging()
            
            # Display banner
            self.display_banner()
            
            # Check dependencies
            if not self.check_dependencies():
                return 1
            
            # Check configuration
            if not self.check_configuration():
                return 1
            
            # Setup signal handlers
            self.setup_signal_handlers()
            
            # Display instructions
            self.display_instructions()
            
            # Start monitoring
            if not self.start_monitoring():
                return 1
            
            print("*** Commission Statement Auto-Monitor is now ACTIVE! ***")
            print("*** Monitoring docs folder for new commission statements... ***")
            print("*** Press Ctrl+C to stop ***")
            print("-" * 80)
            
            # Run main loop
            self.run_monitoring_loop()
            
            return 0
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"[ERROR] Fatal error in main application: {e}")
            else:
                print(f"[ERROR] Fatal error: {e}")
            return 1
        finally:
            self.shutdown()


if __name__ == "__main__":
    """Application entry point"""
    app = CommissionMonitorApp()
    exit_code = app.run()
    sys.exit(exit_code)