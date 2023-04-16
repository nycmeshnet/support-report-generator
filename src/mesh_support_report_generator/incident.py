from datetime import datetime
import pytz

from enum import Enum


class IncidentType(Enum):
    OUTAGE = "Outage"
    POOR_EXPERIENCE = "Poor Experience"
    POOR_SIGNAL = "Poor Signal"

    def __repr__(self):
        return f"{self.__class__.__name__}.{self.name}"


from datetime import datetime
import pytz


class Incident:
    def __init__(
        self,
        device_name: str,
        incident_type: IncidentType,
        event_time: datetime = None,
        site_name: str = None,
        metric_value: float = None,
    ):
        self.device_name = device_name
        self.site_name = site_name
        self.event_time = event_time
        self.incident_type = incident_type
        self.metric_value = metric_value

        if self.incident_type == IncidentType.POOR_SIGNAL and self.metric_value is None:
            raise ValueError("metric_value is required for IncidentType.POOR_SIGNAL")

        if (
            self.incident_type == IncidentType.POOR_EXPERIENCE
            and self.metric_value is None
        ):
            raise ValueError(
                "metric_value is required for IncidentType.POOR_EXPERIENCE"
            )

    def __str__(self) -> str:
        # Build the output string
        output = f"{self.device_name}"
        if self.site_name:
            output += f" ({self.site_name})"

        if self.event_time:
            # Convert event time to US Eastern time zone
            eastern = pytz.timezone("US/Eastern")
            event_time_eastern = self.event_time.astimezone(eastern)
            output += (
                f" (offline since {event_time_eastern.strftime('%Y-%m-%d @ %H:%M')})"
            )

        if self.incident_type == IncidentType.POOR_EXPERIENCE:
            output += f" ({self.metric_value}%)"

        if self.incident_type == IncidentType.POOR_SIGNAL:
            output += f" ({self.metric_value} dBm)"

        return output

    def __repr__(self) -> str:
        return (
            f"Incident("
            f"device_name={repr(self.device_name)}, "
            f"site_name={repr(self.site_name)}, "
            f"event_time={repr(self.event_time)}, "
            f"incident_type={repr(self.incident_type)}, "
            f"metric_value={repr(self.metric_value)})"
        )

    def __eq__(self, other):
        if not isinstance(other, Incident):
            return False
        return (
            self.device_name == other.device_name
            and self.site_name == other.site_name
            and self.event_time == other.event_time
            and self.incident_type == other.incident_type
            and self.metric_value == other.metric_value
        )
