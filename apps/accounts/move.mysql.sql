-- MySQL
-- Changing user table
ALTER TABLE auth_user ADD COLUMN site varchar(200);
ALTER TABLE auth_user ADD COLUMN email_new varchar(75);
UPDATE auth_user SET site = '' WHERE site IS NULL;
UPDATE auth_user SET email_new = '' WHERE email_new IS NULL;
ALTER TABLE auth_user MODIFY site VARCHAR(200) NOT NULL;
ALTER TABLE auth_user MODIFY email_new VARCHAR(75) NOT NULL;
