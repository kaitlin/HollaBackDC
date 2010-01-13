-- PGSQL
-- Changing user table
ALTER TABLE auth_user ADD COLUMN site varchar(200);
ALTER TABLE auth_user ADD COLUMN email_new varchar(75);
UPDATE auth_user SET site = '';
UPDATE auth_user SET email_new = '';
ALTER TABLE auth_user ALTER COLUMN site SET NOT NULL;
ALTER TABLE auth_user ALTER COLUMN email_new SET NOT NULL;
