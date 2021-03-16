from datetime import datetime
from flask import Flask, request
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from flask_jsonpify import jsonify
from flask_cors import CORS

db_connect = create_engine('sqlite:///database/enterprise.db')
app = Flask(__name__)
api = Api(app)
cor_app = CORS(app)


class Employee (Resource):

    @app.route('/employees', methods=['GET'])
    def get_all_employees():
        conn = db_connect.connect()  # connect to database
        query = conn.execute("select * from employees")  # This line performs query and returns json result
        return {'employees': [i[0] for i in query.cursor.fetchall()]}  # Fetches first column that is Employee ID

    @app.route('/employees/<employee_id>', methods=['GET'])
    def get_employee(employee_id):
        try:
            eid = int(employee_id)
        except Exception as e:
            return {"error": "Invalid employee ID: {}".format(e)}
        conn = db_connect.connect()
        query = conn.execute("select * from employees where EmployeeId =%d " % eid)
        result = {'data': [dict(zip(tuple(query.keys()), i)) for i in query.cursor]}
        return jsonify(result)

    @app.route('/employees/create', methods=['POST'])
    def create_employee():
        column_names = {
            "first_name": "FirstName",
            "last_name": "LastName",
            "address": "Address",
            "birth_date": "BirthDate",
            "city": "City",
            "country": "Country",
            "email": "Email",
            "fax": "Fax",
            "hire_date": "HireDate",
            "phone": "Phone",
            "postal_code": "PostalCode",
            "reports_to": "ReportsTo",
            "state": "State",
            "title": "Title"
        }
        first_name = request.args.get('first_name')
        last_name = request.args.get('last_name')
        if first_name is None or last_name is None:
            return {"error": "Field names are required"}
        if len(first_name) == 0 or len(last_name) == 0:
            return {"error": "Field names are empty"}
        columns = ",".join(column_names.get(column) for column in request.args)
        values = "'{}', '{}'".format(first_name, last_name)
        try:
            for column in request.args:
                if column != "first_name" and column != "last_name":
                    value = request.args[column]
                    if column == "hire_date" or column == "birth_date":
                        values = values + ",'{}'".format(datetime.strptime(value, "%Y-%m-%d"))
                    elif column == "reports_to":
                        values = values + ",{}".format(int(value))
                    else:
                        values = values + ",'{}'".format(value)
        except Exception as e:
            return {"error": "Verify your parameters: {}".format(e)}
        conn = db_connect.connect()
        print(columns, values)
        query = conn.execute("INSERT INTO employees (" + columns + ") VALUES ( " + values + " )")
        return {"success": "Employee created, number of rows {}".format(query.rowcount)}

    @app.route('/employees/delete', methods=['POST'])
    def delete_employee():
        employee_id = request.args.get('employee_id')
        if employee_id is None:
            return {"error": "Employee ID not defined"}
        try:
            employee_id = int(employee_id)
        except Exception as e:
            return {"error": "Invalid employee ID: {}".format(e)}
        conn = db_connect.connect()
        query = "DELETE FROM employees where EmployeeId =%d " % employee_id
        query = conn.execute(query)
        if query.rowcount == 0:
            return {"skipped": "No employee was deleted"}
        return {"success": "Number of rows deleted {}".format(query.rowcount)}

    @app.route('/employees/delete/last', methods=['POST'])
    def delete_last_employee():
        conn = db_connect.connect()
        query = conn.execute("DELETE FROM employees where EmployeeId = (SELECT MAX(EmployeeId) FROM employees)")
        if query.rowcount == 0:
            return {"skipped": "No employee was deleted"}
        return {"success": "Number of rows deleted {}".format(query.rowcount)}


api.add_resource(Employee)  # Route_1

if __name__ == '__main__':
    app.run(port='5002')
