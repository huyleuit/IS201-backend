CREATE OR REPLACE FUNCTION CheckAccountPermission(
    p_username IN VARCHAR2,
    p_permission IN VARCHAR2
) RETURN BOOLEAN IS
    v_role_id NUMBER;
    v_permission NUMBER;
BEGIN
    -- Get the role id of the account
    SELECT role INTO v_role_id
    FROM "Account"
    WHERE username = p_username;

    -- Get the permission value
    EXECUTE IMMEDIATE 'SELECT ' || p_permission || ' FROM "Role" WHERE role_id = :1' INTO v_permission USING v_role_id;

    -- Return the result
    IF v_permission = 1 THEN
        RETURN TRUE;  -- Permission granted
    ELSE
        RETURN FALSE;  -- Permission denied
    END IF;
EXCEPTION
    WHEN NO_DATA_FOUND THEN
        RETURN FALSE;  -- Account or permission not found
    WHEN OTHERS THEN
        RETURN FALSE;  -- Other errors
END CheckAccountPermission;
/



create or replace function GetCurrentUserByToken(
    p_token in Varchar2(255)
) return varchar2 is
    v_username varchar2(50);
begin
    select "Account".USERNAME into v_username
    from "AccountToken","Account"
    where "AccountToken".USERNAME = "Account".USERNAME and TOKEN = p_token;
    return v_username;
end;

/
