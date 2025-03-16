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


@app.route("/login", methods=['post'])
def login():
    uname = request.form['uname']
    pswd = request.form['pswd']
    qry = "select * from login where username=%s and password=%s"
    val = (uname, pswd)
    res = selectone(qry, val)

    if res is None:
        return jsonify({"task":"failed"})
    else:
        return jsonify({"task":"valid", "id":res['id']} )




@app.route('/user_register', methods=['post'])
def user_register():

    try:

        print(request.form)

        name = request.form['name']
        address = request.form['address']

        email = request.form['email']
        contact = request.form['contact']

        uname = request.form['uname']
        pswd = request.form['pswd']

        qry = "select * from user where email=%s"
        res = selectone(qry, email)

        if res is not None:
            return jsonify({"task":"failed"})
        else:
            qry = "insert into login values(null,%s,%s,'user')"
            val = (uname,pswd)
            id = iud(qry,val)
            qry = "INSERT INTO `user` VALUES(NULL,%s,%s,%s,%s,%s)"
            val = (id, name, address, email, contact)
            iud(qry,val)

            return jsonify({"task":"success"})

    except Exception as e:
        print(e)
        return jsonify({"task": "failed"})


def view_history(reg_no):


    try:
        print("Loading contract ABI...")
        with open(r"D:\blockchain\node_modules\.bin\build\contracts\VehicleHistory.json") as file:
            contract_json = json.load(file)
            contract_abi = contract_json['abi']

        contract = web3.eth.contract(address='0x32184435B76004211EA806A324945C2aC39Da478', abi=contract_abi)
        blocknumber = web3.eth.get_block_number()
        mdata = []

        print("Current Block Number:", blocknumber)

        for i in range(blocknumber, 3, -1):
            print(f"Processing Block {i}...")

            try:
                a = web3.eth.get_transaction_by_block(i, 0)
                decoded_input = contract.decode_function_input(a['input'])

                # if decoded_input[1]['bid'].split("#")[1] == event_name:

                if decoded_input[1]['reg_no'] == reg_no:
                    data = {
                        'details': str(decoded_input[1]['details']),
                        'cost': str(decoded_input[1]['cost']),
                        'date': str(decoded_input[1]['date']),
                    }
                    mdata.append(data)
                    print(f"Updated data list: {mdata}")

            except Exception as e:
                print(f"Error Processing Block {i}: {e}")
                pass

    except Exception as e:
        print(f"Error with contract ABI or interaction: {e}")

    print("Final Collected Data:", mdata)

    return mdata  # Return data as a normal list, not as JSON


@app.route("/user_view_history", methods=['post'])
def user_view_history():
    reg_no = request.form['regno']
    print(reg_no)
    res = view_history(reg_no)

    return jsonify(res)


@app.route("/view_nearest_service_center", methods=['post'])
def view_nearest_service_center():
    lati = request.form['lati']
    longi = request.form['longi']
    print(request.form)

    qry = "SELECT `service_center`.*, (3959 * ACOS ( COS ( RADIANS(%s) ) * COS( RADIANS( `service_center`.lati) ) * COS( RADIANS( `service_center`.longi ) - RADIANS(%s) ) + SIN ( RADIANS(%s) ) * SIN( RADIANS( `service_center`.lati ) ))) AS user_distance FROM `service_center` HAVING user_distance < 31.068"
    res = selectall2(qry, (lati, longi, lati))
    print(res)

    return jsonify(res)

@app.route("/book_service_center", methods=['post'])
def book_service_center():
    regno = request.form['regno']
    details = request.form['details']
    date = request.form['date']
    vehicle_type = request.form['vehicle_type']
    service_type = request.form['service_type']
    lid = request.form['lid']
    sid = request.form['sid']

    qry = "INSERT INTO `booking` VALUES(NULL, %s, %s, %s, %s, %s, %s, %s, 'pending')"
    iud(qry, (lid, sid, regno, service_type, details, vehicle_type, date))

    return jsonify({"task":"valid"})


@app.route("/view_bookings", methods=['post'])
def view_bookings():
    lid = request.form['lid']
    qry = 'SELECT `service_center`.name, `booking`.* FROM `booking` JOIN `service_center` ON `booking`.sid=`service_center`.lid WHERE `booking`.lid=%s'
    res = selectall2(qry, lid)

    return jsonify(res)


app.run(host="0.0.0.0", port="5000")
