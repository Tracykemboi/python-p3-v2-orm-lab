from __init__ import CURSOR, CONN

class Review:
    all = {}

    def __init__(self, year, summary, employee, id=None):
        self.year = year
        self.summary = summary
        self.employee = employee
        self.id = id

    def __repr__(self):
        return f"<Review {self.id}: {self.year} - {self.employee.name}>"

    @classmethod
    def create_table(cls):
        sql = """
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY,
                year INTEGER,
                summary TEXT,
                employee_id INTEGER,
                FOREIGN KEY (employee_id) REFERENCES employees(id)
            )
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        sql = """
            DROP TABLE IF EXISTS reviews
        """
        CURSOR.execute(sql)
        CONN.commit()

    def save(self):
        sql = """
            INSERT INTO reviews (year, summary, employee_id)
            VALUES (?, ?, ?)
        """
        CURSOR.execute(sql, (self.year, self.summary, self.employee.id))
        CONN.commit()

        self.id = CURSOR.lastrowid
        type(self).all[self.id] = self

    @classmethod
    def create(cls, year, summary, employee):
        review = cls(year, summary, employee)
        review.save()
        return review

    @classmethod
    def instance_from_db(cls, row):
        review = cls.all.get(row[0])
        if review:
            review.year = row[1]
            review.summary = row[2]
            review.employee_id = row[3]
        else:
            from employee import Employee
            employee = Employee.find_by_id(row[3])
            review = cls(row[1], row[2], employee)
            review.id = row[0]
            cls.all[review.id] = review
        return review

    @classmethod
    def find_by_id(cls, id):
        sql = "SELECT * FROM reviews WHERE id = ?"
        CURSOR.execute(sql, (id,))
        row = CURSOR.fetchone()
        return cls.instance_from_db(row) if row else None

    def update(self):
        sql = """
            UPDATE reviews
            SET year = ?, summary = ?, employee_id = ?
            WHERE id = ?
        """
        CURSOR.execute(sql, (self.year, self.summary, self.employee.id, self.id))
        CONN.commit()

    def delete(self):
        sql = "DELETE FROM reviews WHERE id = ?"
        CURSOR.execute(sql, (self.id,))
        CONN.commit()

        del type(self).all[self.id]
        self.id = None

    @classmethod
    def get_all(cls):
        sql = "SELECT * FROM reviews"
        CURSOR.execute(sql)
        return [cls.instance_from_db(row) for row in CURSOR.fetchall()]

    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, value):
        if not isinstance(value, int) or value < 2000:
            raise ValueError("Year must be an integer greater than or equal to 2000")
        self._year = value

    @property
    def summary(self):
        return self._summary

    @summary.setter
    def summary(self, value):
        if not value or not isinstance(value, str):
            raise ValueError("Summary must be a non-empty string")
        self._summary = value

    @property
    def employee(self):
        return self._employee

    @employee.setter
    def employee(self, value):
        from employee import Employee
        if isinstance(value, Employee):
            self._employee = value
            self._employee_id = value.id
        elif isinstance(value, int):
            employee = Employee.find_by_id(value)
            if not employee:
                raise ValueError("Employee with given id does not exist")
            self._employee = employee
            self._employee_id = value
        else:
            raise ValueError("Employee must be an instance of Employee class or an employee_id")

    @property
    def employee_id(self):
        return self._employee_id

    @employee_id.setter
    def employee_id(self, value):
        from employee import Employee
        employee = Employee.find_by_id(value)
        if not employee:
            raise ValueError("Employee with given id does not exist")
        self._employee_id = value
        self._employee = employee