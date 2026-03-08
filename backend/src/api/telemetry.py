import os 
import logging
from azure.monitor.opentelemetry import configure_azure_monitor

# CREATE A DEDICATED LOGGER
logger = logging.getLogger("Compliance-QA-telemetry")

def setup_telemetry():
    """
    Initialize Azure Monitor OpenTelemetry

    Track: HTTP requests, database queries, errors, performance metrics
    """
    connection_string = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")

    # CHECK IF CONFIGURED
    if not connection_string:
        logger.warning("No Instrumentation key found. Telemetry is Disabled.")
        return 
    
    # CONFIGURE AZURE MONITOR
    try:
        configure_azure_monitor(
            connection_string = connection_string,  # where to send data
            logger_name = "Compliance-QA-tracer"
        )

    except Exception as e:
        # ERROR HANDLING: If telemetry fails (bad connection string, network issues, etc.)
        logger.error(f"Failed to initialize Azure Monitor: {e}")
