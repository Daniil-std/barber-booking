from django.db import migrations


FORWARD = """
CREATE FUNCTION form_sync_staff_reservations() RETURNS trigger AS $$
BEGIN
    DELETE FROM studio_staffreservation WHERE appointment_id = NEW.id;
    IF NEW.status = 'confirmed' THEN
        INSERT INTO studio_staffreservation (appointment_id, barber_id, starts_at, ends_at)
        SELECT NEW.id, staff_id, NEW.starts_at, NEW.ends_at
        FROM (VALUES (NEW.barber_id), (NEW.supervisor_id)) AS staff(staff_id)
        WHERE staff_id IS NOT NULL
        ORDER BY staff_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER form_appointment_staff_occupancy
AFTER INSERT OR UPDATE OF barber_id, supervisor_id, starts_at, ends_at, status
ON studio_appointment FOR EACH ROW EXECUTE FUNCTION form_sync_staff_reservations();

INSERT INTO studio_staffreservation (appointment_id, barber_id, starts_at, ends_at)
SELECT id, barber_id, starts_at, ends_at FROM studio_appointment WHERE status = 'confirmed';

UPDATE studio_service SET senior_price = price * 1.25, top_price = price * 1.50;
"""

REVERSE = """
DROP TRIGGER form_appointment_staff_occupancy ON studio_appointment;
DROP FUNCTION form_sync_staff_reservations();
DELETE FROM studio_staffreservation;
"""


class Migration(migrations.Migration):
    dependencies = [("studio", "0002_staffreservation_appointment_barber_level_and_more")]
    operations = [migrations.RunSQL(FORWARD, REVERSE)]
