create or replace trigger EMPLOYEE_AUTO_INSERT_DATE
    before insert
    on "Employee"
    for each row
BEGIN
    :NEW."CREATE_BY" := USER;
    :NEW."CREATE_DATE" := SYSDATE;
    :NEW."LAST_MODIFIED_BY" := USER;
    :NEW."LAST_MODIFIED_DATE" := SYSDATE;
END;
/
create or replace trigger EMPLOYEE_AUTO_UPDATE_DATE
    before update of "LAST_MODIFIED_BY", "LAST_MODIFIED_DATE"
    on "Employee"
    for each row
BEGIN
    :NEW."LAST_MODIFIED_BY" := USER;
    :NEW."LAST_MODIFIED_DATE" := SYSDATE;
END;
/



CREATE OR REPLACE TRIGGER account_auto_insert_date
BEFORE INSERT ON "Account"
FOR EACH ROW
BEGIN
    :NEW."CREATE_DATE" := SYSDATE;
    :NEW."CREATE_BY" := USER;
    :NEW."LAST_MODIFIED_DATE" := SYSDATE;
    :NEW."LAST_MODIFIED_BY" := USER;
END ;
/
CREATE OR REPLACE TRIGGER account_token_auto_insert_date
BEFORE INSERT ON "AccountToken"
    FOR EACH ROW
BEGIN
    :NEW."EXPIRE" := SYSDATE + 1;
     :NEW."CREATE_DATE" := SYSDATE;
    :NEW."CREATE_BY" := USER;
    :NEW."LAST_MODIFIED_DATE" := SYSDATE;
    :NEW."LAST_MODIFIED_BY" := USER;
END;
/

CREATE OR REPLACE TRIGGER GOODS_AUTO_INSERT_DATE
    BEFORE INSERT ON "Goods"
    FOR EACH ROW
   BEGIN
    :NEW."CREATE_BY" := USER;
    :NEW."CREATE_DATE" := SYSDATE;
    :NEW."LAST_MODIFIED_BY" := USER;
    :NEW."LAST_MODIFIED_DATE" := SYSDATE;
END;
create or replace trigger GOODS_AUTO_UPDATE_DATE
    before update of "LAST_MODIFIED_BY", "LAST_MODIFIED_DATE"
    on "Goods"
    for each row
BEGIN
    :NEW."LAST_MODIFIED_BY" := USER;
    :NEW."LAST_MODIFIED_DATE" := SYSDATE;
END;
/

CREATE OR REPLACE TRIGGER CATEGORY_AUTO_INSERT_DATE
    BEFORE INSERT ON "Category"
    FOR EACH ROW
   BEGIN
    :NEW."CREATE_BY" := USER;
    :NEW."CREATE_DATE" := SYSDATE;
    :NEW."LAST_MODIFIED_BY" := USER;
    :NEW."LAST_MODIFIED_DATE" := SYSDATE;
END;
CREATE OR REPLACE TRIGGER CATEGORY_AUTO_UPDATE_DATE
    BEFORE UPDATE OF "LAST_MODIFIED_BY", "LAST_MODIFIED_DATE"
    ON "Category"
    FOR EACH ROW
BEGIN
    :NEW."LAST_MODIFIED_BY" := USER;
    :NEW."LAST_MODIFIED_DATE" := SYSDATE;
END;

/

CREATE OR REPLACE TRIGGER PROMOTION_AUTO_INSERT_DATE
    BEFORE INSERT ON "Promotion"
    FOR EACH ROW
   BEGIN
    :NEW."CREATE_BY" := USER;
    :NEW."CREATE_DATE" := SYSDATE;
    :NEW."LAST_MODIFIED_BY" := USER;
    :NEW."LAST_MODIFIED_DATE" := SYSDATE;
END;
CREATE OR REPLACE TRIGGER PROMOTION_AUTO_UPDATE_DATE
    BEFORE UPDATE OF "LAST_MODIFIED_BY", "LAST_MODIFIED_DATE"
    ON "Promotion"
    FOR EACH ROW
BEGIN
    :NEW."LAST_MODIFIED_BY" := USER;
    :NEW."LAST_MODIFIED_DATE" := SYSDATE;
END;
/
CREATE OR REPLACE TRIGGER trg_bill_insert
    BEFORE INSERT ON "Bill"
    FOR EACH ROW
    BEGIN
        :NEW."CREATE_BY" := USER;
        :NEW."LAST_MODIFIED_BY" := USER;
        :NEW."CREATE_DATE" := SYSDATE;
        :NEW."LAST_MODIFIED_DATE" := SYSDATE;
    end;
/
create or replace trigger trg_bill_update
    before update on "Bill"
    for each row
    begin
        :new."LAST_MODIFIED_DATE" := sysdate;
        :new."LAST_MODIFIED_BY" := user;
    end;
/
create or replace trigger trg_bill_delete
    before delete on "Bill"
    for each row
    begin
        delete from "Payment" where bill_id = :old.bill_id;
        delete from "BillDetails" where bill_id = :old.bill_id;
    end;




CREATE OR REPLACE TRIGGER trg_insert_account
AFTER INSERT ON "Employee"
FOR EACH ROW
BEGIN
    INSERT INTO "Account" (USERNAME,emp_id,ROLE_ID, STATUS, create_date, create_by, last_modified_date, last_modified_by)
    VALUES (:new.username, :new.emp_id, :new.role_id,'pw_not_set', SYSDATE, 'trg_insert_account', SYSDATE, 'trg_insert_account');
END;
create or replace trigger trg_update_account
AFTER UPDATE ON "Employee"
FOR EACH ROW
BEGIN
    UPDATE "Account" SET USERNAME = :new.username, ROLE_ID = :new.role_id, last_modified_date = SYSDATE, last_modified_by = 'trg_update_account' WHERE emp_id = :new.emp_id;
END;

/
create or replace trigger trg_delete_account
AFTER DELETE ON "Employee"
FOR EACH ROW
BEGIN
    DELETE FROM "Account" WHERE emp_id = :old.emp_id;
END;

/
CREATE OR REPLACE TRIGGER trg_insert_import_note
    BEFORE INSERT ON "ImportNote"
    FOR EACH ROW
    BEGIN
        :NEW."CREATE_BY" := USER;
        :NEW."LAST_MODIFIED_BY" := USER;
        :NEW."CREATE_DATE" := SYSDATE;
        :NEW."LAST_MODIFIED_DATE" := SYSDATE;
    end;
/
create or replace trigger trg_update_import_note
    before update on "ImportNote"
    for each row
    begin
        :new."LAST_MODIFIED_DATE" := sysdate;
        :new."LAST_MODIFIED_BY" := user;
    end;

CREATE OR REPLACE TRIGGER trg_insert_shipment
    BEFORE INSERT ON "Shipment"
    FOR EACH ROW
    BEGIN
        :NEW."CREATE_BY" := USER;
        :NEW."LAST_MODIFIED_BY" := USER;
        :NEW."CREATE_DATE" := SYSDATE;
        :NEW."LAST_MODIFIED_DATE" := SYSDATE;
    end;
/
create or replace trigger trg_update_shipment
    before update on "Shipment"
    for each row
    begin
        :new."LAST_MODIFIED_DATE" := sysdate;
        :new."LAST_MODIFIED_BY" := user;
    end;