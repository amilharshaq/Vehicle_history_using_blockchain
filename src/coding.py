from flask import *
from src.dbconnection import *
import functools



from web3 import Web3, HTTPProvider

# truffle development blockchain address
blockchain_address = 'http://127.0.0.1:7545'
# Client instance to interact with the blockchain
web3 = Web3(HTTPProvider(blockchain_address,{"timeout": 800}))
# Set the default account (so we don't need to set the "from" for every transaction call)
web3.eth.defaultAccount = web3.eth.accounts[0]
compiled_contract_path = r"D:\blockchain\node_modules\.bin\build\contracts\VehicleHistory.json"
# Deployed contract address (see `migrate` command output: `contract address`)
deployed_contract_address = '0x32184435B76004211EA806A324945C2aC39Da478'



app = Flask(__name__)

app.secret_key = "87497823"


@app.route('/')
def login():
    return render_template("login_index.html")

def login_required(func):
    @functools.wraps(func)
    def secure_function():
        if "lid" not in session:
            return render_template('login_index.html')
        return func()

    return secure_function


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route('/login_code', methods=['post'])
def login_code():
    uname = request.form['textfield']
    pswd = request.form['textfield2']
    qry = "select * from login where username=%s and password=%s"
    val = (uname,pswd)
    res = selectone(qry, val)

    if res is None:
        return '''<script>alert("Invalid username or password");window.location="/"</script>'''
    elif res['type'] == "admin":
        session['lid'] = res['id']
        return '''<script>alert("Welcome admin");window.location="/admin_home"</script>'''
    elif res['type'] == "service":
        session['lid'] = res['id']
        return '''<script>alert("Welcome");window.location="/service_home"</script>'''
    elif res['type'] == "user":
        session['lid'] = res['id']
        return '''<script>alert("Welcome");window.location="/user_home"</script>'''
    else:
        return '''<script>alert("Invalid username or password");window.location="/"</script>'''


@app.route('/service_center_register')
def service_center_register():
    return render_template("service_center_register.html")


@app.route('/service_center_register_code', methods=['post'])
def service_center_register_code():

    try:

        print(request.form)

        name = request.form['textfield']
        address = request.form['textfield2']
        email = request.form['textfield5']
        contact = request.form['textfield6']
        uname = request.form['textfield7']
        pswd = request.form['textfield8']

        qry = "select * from service_center where email=%s"
        res = selectone(qry,email)

        if res is not None:
            return '''<script>alert("Email already exist");window.location="/#about"</script>'''
        else:
            qry = "insert into login values(null,%s,%s,'pending')"
            val = (uname,pswd)
            id = iud(qry,val)
            qry = "INSERT INTO `service_center` VALUES(NULL,%s,%s,%s,%s,%s)"
            val = (id,name,address,email,contact)
            iud(qry,val)

            return '''<script>alert("Registration success");window.location="/#about"</script>'''
    except Exception as e:
        print(e)
        return '''<script>alert("Username already exist");window.location="/#about"</script>'''


@app.route('/user_register')
def user_register():
    return render_template("user_register.html")


@app.route('/user_register_code', methods=['post'])
def user_register_code():

    try:

        print(request.form)

        name = request.form['textfield']
        address = request.form['textfield2']

        email = request.form['textfield5']
        contact = request.form['textfield6']

        uname = request.form['textfield7']
        pswd = request.form['textfield8']

        qry = "select * from user where email=%s"
        res = selectone(qry, email)

        if res is not None:
            return '''<script>alert("Email already exist");window.location="/#about"</script>'''
        else:
            qry = "insert into login values(null,%s,%s,'user')"
            val = (uname,pswd)
            id = iud(qry,val)
            qry = "INSERT INTO `user` VALUES(NULL,%s,%s,%s,%s,%s)"
            val = (id, name, address, email, contact)
            iud(qry,val)

            return '''<script>alert("Registration success");window.location="/#about"</script>'''
    except Exception as e:
        print(e)
        return '''<script>alert("Username already exist");window.location="/#about"</script>'''


@app.route('/admin_home')
@login_required
def admin_home():
    return render_template("admin/admin_index.html")


@app.route('/verify_service_center')
@login_required
def verify_service_center():
    qry = 'SELECT * FROM `service_center` JOIN `login` ON `service_center`.`lid`=`login`.id WHERE `login`.type = "pending"'
    res = selectall(qry)
    return render_template("admin/verify_service_center.html", val=res)


@app.route("/accept_center")
@login_required
def accept_center():
    id = request.args.get('id')
    qry = "update login set type = 'service' where id = %s"
    iud(qry, id)

    return '''<script>alert("Accepted");window.location="verify_service_center"</script>'''


@app.route("/reject_center")
@login_required
def reject_center():
    id = request.args.get('id')
    qry = "update login set type = 'rejected' where id = %s"
    iud(qry, id)

    return '''<script>alert("Rejected");window.location="verify_service_center"</script>'''


@app.route("/view_service_history")
def view_service_history():
    return render_template("admin/view_history.html")


@app.route("/view_history2", methods=['post'])
def view_history2():
    reg_no = request.form['textfield']
    qry = "SELECT `user`.name, `booking`.`vehicle_reg_no`,`service_type`,`vehicle_type`, `service_history`.* FROM `service_history` JOIN `booking` ON `service_history`.bid=`booking`.id JOIN `user`ON `booking`.lid=`user`.lid WHERE `booking`.`vehicle_reg_no`=%s"
    res = selectone(qry, reg_no)
    return render_template("admin/view_history.html", val=res)


@app.route("/service_home")
def service_home():
    return render_template("service_center/service_center_index.html")


@app.route("/view_bookings")
def view_bookings():
    qry = "SELECT `user`.name,phone,email, `booking`.* FROM `booking` JOIN `user` ON `booking`.lid = `user`.lid WHERE `booking`.sid=%s and booking.status='pending'"
    res = selectall2(qry, session['lid'])
    return render_template("service_center/view_booking.html", val=res)


@app.route("/accept_booking")
@login_required
def accept_booking():
    id = request.args.get('id')
    qry = "update booking set status = 'accepted' where id = %s"
    iud(qry, id)

    # Redirecting with the 'status' query parameter
    return redirect(url_for('view_bookings', status='accepted'))

@app.route("/reject_booking")
@login_required
def reject_booking():
    id = request.args.get('id')
    qry = "update booking set status = 'rejected' where id = %s"
    iud(qry, id)

    # Redirecting with the 'status' query parameter
    return redirect(url_for('view_bookings', status='rejected'))


@app.route("/add_service_history", methods=["GET", "POST"])
def add_service_history():
    if request.method == "POST":
        # Retrieve data from the form
        booking_id = request.form['booking_id']
        details = request.form['details']
        cost = request.form['cost']

        # Insert service history into the database
        qry = "INSERT INTO service_history VALUES(null, %s, %s, %s, curdate())"
        iud(qry, (booking_id, details, cost))

        flash("Service history added successfully!", "success")
        return redirect("/add_service_history")

    # Fetch booking details for the logged-in service center
    qry = "SELECT `user`.name, `booking`.* FROM `booking` JOIN `user` ON `booking`.lid=`user`.lid WHERE booking.sid=%s"
    bookings = selectall2(qry, session['lid'])

    return render_template("service_center/add_service_history.html", bookings=bookings)


@app.route("/view_service_history3")
def view_service_history3():
    return render_template("service_center/view_history.html")


@app.route("/view_history4", methods=['post'])
def view_history4():
    reg_no = request.form['textfield']
    qry = "SELECT `user`.name, `booking`.`vehicle_reg_no`,`service_type`,`vehicle_type`, `service_history`.* FROM `service_history` JOIN `booking` ON `service_history`.bid=`booking`.id JOIN `user`ON `booking`.lid=`user`.lid WHERE `booking`.`vehicle_reg_no`=%s"
    res = selectone(qry, reg_no)
    return render_template("service_center/view_history.html", val=res)


@app.route("/user_home")
def user_home():
    return render_template("user/user_index.html")


@app.route("/add_blockchain")
def add_blockchain():
    return "ok"


app.run(debug=True)

