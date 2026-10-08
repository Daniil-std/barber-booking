from django.db import migrations


FORWARD = """
CREATE FUNCTION form_lock_appointment_staff() RETURNS trigger AS $$
BEGIN
    -- Lock before inserting the appointment, so direct SQL/ORM writes use the
    -- same staff ordering as the API and do not race in the exclusion index.
    PERFORM id FROM studio_barber
    WHERE id IN (NEW.barber_id, NEW.supervisor_id)
    ORDER BY id FOR NO KEY UPDATE;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER form_appointment_lock_staff
BEFORE INSERT OR UPDATE OF barber_id, supervisor_id, starts_at, ends_at, status
ON studio_appointment FOR EACH ROW EXECUTE FUNCTION form_lock_appointment_staff();
"""

REVERSE = """
DROP TRIGGER form_appointment_lock_staff ON studio_appointment;
DROP FUNCTION form_lock_appointment_staff();
"""


class Migration(migrations.Migration):
    dependencies = [("studio", "0003_staff_occupancy_trigger")]
    operations = [migrations.RunSQL(FORWARD, REVERSE)]
