CREATE FUNCTION check_users_rights()
RETURNS trigger AS
$BODY$
BEGIN
    IF (OLD.manage_users = TRUE AND (TG_OP = 'DELETE' OR NOT NEW.manage_users)) THEN
        IF (SELECT COUNT(*) FROM admins WHERE manage_users = TRUE) = 1 THEN
            RAISE EXCEPTION 'At least one user should have the "manage users" right.';
        END IF;
    END IF;

    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    ELSE
        RETURN NEW;
    END IF;
END
$BODY$ LANGUAGE plpgsql;

CREATE TRIGGER at_least_one_manage_users
BEFORE UPDATE OR DELETE
ON admins
FOR EACH ROW
EXECUTE PROCEDURE check_users_rights();
