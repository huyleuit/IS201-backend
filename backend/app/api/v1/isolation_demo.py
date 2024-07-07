from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.tables import EmpTable
from sqlalchemy import text

isolation_router = APIRouter()
from db.session import getSession, getSessionSerializableMode


@isolation_router.get('/Unrepeatable-Read-Problem', summary='Unrepeatable-Read-Problem demo', status_code=200)
def demo(
        s1: Session = Depends(getSessionSerializableMode),
        s2: Session = Depends(getSession)):
    # mô tả tình huống
    # Một nhân viên trong công ty (có emp_id = 1)
    # đang kiểm tra lương hiện tại của mình thông qua một hệ thống (đại diện bởi phiên s1).
    # Lương hiện tại của nhân viên này được lưu vào salary1

    salary1 = s1.execute(text('select salary from "Employee" where emp_id = 1')).fetchone()[0]
    print(f"first read {salary1}")

    # Trong khi nhân viên đang kiểm tra lương của mình, một quản lý khác (đại diện bởi phiên s2)
    # quyết định tăng lương của nhân viên này lên 200.
    s2.execute(text('update "Employee" set salary = 200 where emp_id = 1'))
    s2.commit()

    # Khi nhân viên kiểm tra lại lương của mình trong cùng một phiên (s1),
    # Họ thấy rằng lương của họ đã được tăng lên 200, mặc dù không thông báo nào về việc tăng lương này.
    # gây ra sự khó hiểu cho nhân viên.
    salary2 = s1.execute(text('select salary from "Employee" where emp_id = 1')).fetchone()[0]
    print(f"second read {salary2}")

    return {
        'first_read': salary1,
        'second_read': salary2
    }


@isolation_router.get("/lost-update-problem", summary="lost-udpate-problem demo", status_code=200)
def demo(s1: Session = Depends(getSession), s2: Session = Depends(getSession)):
    #Có hai phiên làm việc (s1 và s2), đại diện cho hai người dùng hoặc hai hệ thống khác nhau
    # đang cố gắng cập nhật cùng một dữ liệu - trong trường hợp này, đó là lương của một nhân viên có emp_id là 1.

    # Phiên s1 thực hiện cập nhật đầu tiên, tăng lương của nhân viên lên thêm 100 đơn vị.
    s1.execute(text(f'update "Employee" set salary = SALARY + 100 where emp_id = 1'))
    #Trong khi phiên s1 vẫn chưa kết thúc, phiên s2 thực hiện cập nhật thứ hai, đặt lương của nhân viên thành 200 đơn vị.
    s2.execute(text('update "Employee" set salary = 200 where emp_id = 1'))

    #Cả hai phiên đều thực hiện commit để lưu thay đổi của mình vào cơ sở dữ liệu.
    s1.commit()
    s2.commit()
    #Kết quả là, thay đổi của phiên s1 (tăng lương thêm 100 đơn vị) bị mất, vì nó bị ghi đè bởi thay đổi của phiên s2
    # (đặt lương thành 200 đơn vị). Đây chính là tình huống "lost update".
    salary = s1.execute(text('select salary from "Employee" where emp_id = 1')).fetchone()[0]
    print(salary)
    return {'salary': salary}


@isolation_router.get('/phantom-read-problem', summary='phantom-read-problem demo', status_code=200)
def demo(s1: Session = Depends(getSession), s2: Session = Depends(getSession)):
    #Giả sử có một hệ thống quản lý nhân sự đang chạy (đại diện bởi phiên s1).
    # Hệ thống này đang thực hiện một truy vấn để đếm số lượng nhân viên hiện tại trong công ty và lưu kết quả vào biến count1.
    count1 = s1.execute(text('select count(*) from "Employee"')).fetchone()[0]
    print(f"First count: {count1}")

    # Trong khi hệ thống đang thực hiện truy vấn trên, một quản lý khác (đại diện bởi phiên s2) quyết định thêm một nhân viên mới vào công ty.
    #
    insert_emp: EmpTable = EmpTable(
        emp_id=100,
        username='new_username',
        emp_name="new emp",
        salary=100,
        address="new address",
        phone='987654321',
        gender='Nam')
    s2.add(insert_emp)
    s2.commit()

    # hệ thống kiểm tra lại vả thấy số lương nhân vien đã bị thay đổi, gây khó hiểu cho hệ thống quản lý nhân sự.
    # đây là hiện tượng phantom read
    count2 = s1.execute(text('select count(*) from "Employee"')).fetchone()[0]
    print(f"Second count: {count2}")

    return {
        'first_count': count1,
        'second_count': count2
    }
