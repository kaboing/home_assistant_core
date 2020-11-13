"""The tests for time_date sensor platform."""
import pytest

import homeassistant.components.time_date.sensor as time_date
import homeassistant.util.dt as dt_util

from tests.async_mock import patch

ORIG_TZ = dt_util.DEFAULT_TIME_ZONE


@pytest.fixture(autouse=True)
def restore_ts():
    """Restore default TZ."""
    yield
    dt_util.DEFAULT_TIME_ZONE = ORIG_TZ


# pylint: disable=protected-access
async def test_intervals(hass):
    """Test timing intervals of sensors."""
    device = time_date.TimeDateSensor(hass, "time")
    now = dt_util.utc_from_timestamp(45)
    with patch("homeassistant.util.dt.utcnow", return_value=now):
        next_time = device.get_next_interval()
    assert next_time == dt_util.utc_from_timestamp(60)

    device = time_date.TimeDateSensor(hass, "beat")
    now = dt_util.utc_from_timestamp(29)
    with patch("homeassistant.util.dt.utcnow", return_value=now):
        next_time = device.get_next_interval()
    assert next_time == dt_util.utc_from_timestamp(86.4)

    device = time_date.TimeDateSensor(hass, "date_time")
    now = dt_util.utc_from_timestamp(1495068899)
    with patch("homeassistant.util.dt.utcnow", return_value=now):
        next_time = device.get_next_interval()
    assert next_time == dt_util.utc_from_timestamp(1495068900)

    now = dt_util.utcnow()
    device = time_date.TimeDateSensor(hass, "time_date")
    next_time = device.get_next_interval()
    assert next_time > now


async def test_states(hass):
    """Test states of sensors."""
    now = dt_util.utc_from_timestamp(1495068856)
    device = time_date.TimeDateSensor(hass, "time")
    device._update_internal_state(now)
    assert device.state == "00:54"

    device = time_date.TimeDateSensor(hass, "date")
    device._update_internal_state(now)
    assert device.state == "2017-05-18"

    device = time_date.TimeDateSensor(hass, "time_utc")
    device._update_internal_state(now)
    assert device.state == "00:54"

    device = time_date.TimeDateSensor(hass, "date_time")
    device._update_internal_state(now)
    assert device.state == "2017-05-18, 00:54"

    device = time_date.TimeDateSensor(hass, "date_time_utc")
    device._update_internal_state(now)
    assert device.state == "2017-05-18, 00:54"

    device = time_date.TimeDateSensor(hass, "beat")
    device._update_internal_state(now)
    assert device.state == "@079"

    device = time_date.TimeDateSensor(hass, "date_time_iso")
    device._update_internal_state(now)
    assert device.state == "2017-05-18T00:54:00"


async def test_states_non_default_timezone(hass):
    """Test states of sensors in a timezone other than UTC."""
    new_tz = dt_util.get_time_zone("America/New_York")
    assert new_tz is not None
    dt_util.set_default_time_zone(new_tz)

    now = dt_util.utc_from_timestamp(1495068856)
    device = time_date.TimeDateSensor(hass, "time")
    device._update_internal_state(now)
    assert device.state == "20:54"

    device = time_date.TimeDateSensor(hass, "date")
    device._update_internal_state(now)
    assert device.state == "2017-05-17"

    device = time_date.TimeDateSensor(hass, "time_utc")
    device._update_internal_state(now)
    assert device.state == "00:54"

    device = time_date.TimeDateSensor(hass, "date_time")
    device._update_internal_state(now)
    assert device.state == "2017-05-17, 20:54"

    device = time_date.TimeDateSensor(hass, "date_time_utc")
    device._update_internal_state(now)
    assert device.state == "2017-05-18, 00:54"

    device = time_date.TimeDateSensor(hass, "beat")
    device._update_internal_state(now)
    assert device.state == "@079"

    device = time_date.TimeDateSensor(hass, "date_time_iso")
    device._update_internal_state(now)
    assert device.state == "2017-05-17T20:54:00"


# pylint: disable=no-member
async def test_timezone_intervals(hass):
    """Test date sensor behavior in a timezone besides UTC."""
    new_tz = dt_util.get_time_zone("America/New_York")
    assert new_tz is not None
    dt_util.set_default_time_zone(new_tz)

    device = time_date.TimeDateSensor(hass, "date")
    now = dt_util.utc_from_timestamp(50000)
    with patch("homeassistant.util.dt.utcnow", return_value=now):
        next_time = device.get_next_interval()
    # start of local day in EST was 18000.0
    # so the second day was 18000 + 86400
    assert next_time.timestamp() == 104400

    new_tz = dt_util.get_time_zone("America/Edmonton")
    assert new_tz is not None
    dt_util.set_default_time_zone(new_tz)
    now = dt_util.parse_datetime("2017-11-13 19:47:19-07:00")
    device = time_date.TimeDateSensor(hass, "date")
    with patch("homeassistant.util.dt.utcnow", return_value=now):
        next_time = device.get_next_interval()
    assert next_time.timestamp() == dt_util.as_timestamp("2017-11-14 00:00:00-07:00")


@patch(
    "homeassistant.util.dt.utcnow",
    return_value=dt_util.parse_datetime("2017-11-14 02:47:19-00:00"),
)
async def test_timezone_intervals_empty_parameter(hass):
    """Test get_interval() without parameters."""
    new_tz = dt_util.get_time_zone("America/Edmonton")
    assert new_tz is not None
    dt_util.set_default_time_zone(new_tz)
    device = time_date.TimeDateSensor(hass, "date")
    next_time = device.get_next_interval()
    assert next_time.timestamp() == dt_util.as_timestamp("2017-11-14 00:00:00-07:00")


async def test_icons(hass):
    """Test attributes of sensors."""
    device = time_date.TimeDateSensor(hass, "time")
    assert device.icon == "mdi:clock"
    device = time_date.TimeDateSensor(hass, "date")
    assert device.icon == "mdi:calendar"
    device = time_date.TimeDateSensor(hass, "date_time")
    assert device.icon == "mdi:calendar-clock"
    device = time_date.TimeDateSensor(hass, "date_time_utc")
    assert device.icon == "mdi:calendar-clock"
    device = time_date.TimeDateSensor(hass, "date_time_iso")
    assert device.icon == "mdi:calendar-clock"
