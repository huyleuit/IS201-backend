--Trigger
--1. Viết trigger tạo Payment khi có hóa đơn mới
CREATE OR REPLACE TRIGGER trg_create_payment
AFTER INSERT ON "Bill"
FOR EACH ROW
BEGIN
  INSERT INTO "Payment" (bill_id, payment_status, total, last_modified_date, last_modified_by, create_date, create_by)
  VALUES (:NEW.bill_id, 'Processing', 0, sysdate, 'admin', sysdate, 'admin');
END;

--2. Viết trigger cập nhật tổng tiền của Payment khi có thay đổi về hóa đơn
CREATE OR REPLACE TRIGGER trg_bill_detail_add
before INSERT ON "BillDetails"
FOR EACH ROW
BEGIN
   update "Payment"
    set "Payment".total = "Payment".TOTAL + :NEW.total
    where bill_id = :NEW.bill_id;

   update "Shipment"
    set "Shipment".quantity = "Shipment".quantity - :NEW.quantity
    where good_id = :NEW.goods_id and shipment_id = :NEW.shipment_id;
END;







--3. Viết trigger cập nhật điểm thành viên, số hàng sau khi hoàn tất thanh toán
CREATE OR REPLACE TRIGGER update_membership_card_point
AFTER UPDATE OF PAYMENT_STATUS ON "Payment"
FOR EACH ROW
BEGIN
	IF :NEW.payment_status = 'Success' THEN
		IF :NEW.card_id IS NOT NULL THEN
  		UPDATE "MembershipCard"
  		SET card_point = card_point + floor(:NEW.total/1000000)
  		WHERE card_id = :NEW.card_id;
		END IF;
	END IF;
END;


--4. Viết trigger cập nhật kpi nhân viên khi đăng kí thẻ thành viên mới
CREATE OR REPLACE TRIGGER update_employee_kpi
AFTER INSERT ON "MembershipCard"
FOR EACH ROW
BEGIN
  UPDATE  "Employee"
  SET kpi = kpi + 1
  WHERE emp_id = :NEW.emp_id;
END;

--Procedure
--3. Procedure cập nhật hàng hóa khi nhập hàng, thêm trường hợp nếu lô hàng đó mới, cập nhật bảng goods shipment như thế nào
CREATE OR REPLACE PROCEDURE import_goods (
    p_goods_id INT,
    p_shipment_id INT,
    p_quantity INT
)
AS
BEGIN
  IF NOT EXISTS (SELECT * FROM "Shipment" WHERE good_id = p_goods_id AND shipment_id = p_shipment_id) THEN
    INSERT INTO "Shipment" (good_id, shipment_id, quantity, price, create_date, create_by)
    VALUES (p_goods_id, p_shipment_id, p_quantity, 0, sysdate, 'admin');
  ELSE
    UPDATE "Shipment"
    SET quantity = quantity + p_quantity
    WHERE good_id = p_goods_id AND shipment_id = p_shipment_id;
  END IF;
END;

-- SELECT * FROM user_errors;


--4. Procedure cập nhật hàng hóa khi xuất hàng
CREATE OR REPLACE PROCEDURE export_goods (
	p_goods_id INT,
	p_shipment_id INT,
	p_quantity INT
)
AS
BEGIN
  UPDATE "Shipment"
  SET quantity = quantity - p_quantity
  WHERE good_id = p_goods_id AND shipment_id = p_shipment_id;
END;
/



-- BEGIN
-- top_selling_goods('21-MAY-2024', '22-MAY-2024');
-- END;
--
-- SELECT *
--   FROM USER_ERRORS