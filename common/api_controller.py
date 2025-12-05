"""
API Controller Module

This module provides API endpoints for managing products, roles, suppliers, retailers, and inventory.
It handles various operations including CRUD operations for products, user role management,
inventory tracking, and supplier/retailer management.

Routes:
    /api/products - Manage product inventory
    /api/roles - Handle user role management
    /api/suppliers - Manage supplier information
    /api/retailers - Manage retailer information
    /api/inventory - Handle inventory operations

Dependencies:
    - Flask for web framework
    - MongoDB for data storage
    - Custom modules: MongoConnection, login_manager, config
"""

from flask import Blueprint,g,jsonify,request
from common.MongoConnection import *
from common.login_manager import check_login
from common.config import *
from datetime import datetime

def findABC(_int)->str:
    abcRulesset = {
    '1':'A',
    '2':'B',
    '3':'C'
    }
    return abcRulesset[_int]

def rulesetProductCategory(ans)->str:
    rulset = {
        '1':'Electronics',
        '2':'Apparels',
        '3':'Furnitures',
        '4':'Healths',
        '5':'Seasonals',
        '6':'Consumables'
    }
    return rulset[ans]

def findMaxId():
    try:
        result = productCollection.collection.find_one(sort=[("_id", -1)])
        if result:
            result = result['_id']
            resultSplit = result.split('PRD')
            resultSplit = int(resultSplit[1])
            return resultSplit
        else:
            return 0
    except Exception as e:
        print(e)
        return 0

def sanitizeForWebix(i):
    result = {}
    for key,value in i.items():
        result[key]=str(value)
    return result

def dashboardDataFetch():
    _dict = {}
    _dict['suppliers'] = str(supplierCollection.collection.count_documents({}))
    _dict['retails'] = str(retailCollection.collection.count_documents({}))
    _dict['items'] = str(productCollection.collection.count_documents({}))
    totalPrice = inventoryCountCollection.collection.find_one(sort=[('_id',-1)])['totalPrice']
    _dict['totalPrice'] = str(0 if totalPrice == [] else totalPrice)
    return _dict

def totalCountUpdater(value):
    updating = False
    logData = {}
    current_date = datetime.now()
    formatted_string = current_date.strftime("%d-%m-%Y")
    logIdGetter = inventoryCountCollection.collection.find_one(sort=[('_id',-1)])
    if logIdGetter:
        result = int(logIdGetter['_id'].split('ITMCHRT')[1])
        result = f"ITMCHRT{result+1:010}"
        totalPrice = list(productInventoryCollection.collection.find({},{"latestStoredPrice": 1,"_id":0}))
        if totalPrice:
            totalPrice = float(sum([x.get("latestStoredPrice") for x in totalPrice]))
        if logIdGetter['date'] == formatted_string:
            updating=True
    else:
        result = "ITMCHRT000000001"
    if not updating:
        if logIdGetter:
                if int(logIdGetter['totalItems'])<value:
                    return False
                logData = {
                    "_id":result,
                    "totalItems":int(logIdGetter['totalItems'])-value,
                    "date": formatted_string,
                    'totalPrice':totalPrice
                }
        else:
                if 0<value:
                    return False
                logData = {
                    "_id":result,
                    "totalItems":-value,
                    "date": formatted_string,
                    "totalPrice":totalPrice
                }
        itemLog = inventoryCountCollection.collection.insert_one(logData)
    else:
        itemLog = inventoryCountCollection.collection.update_one({'_id':logIdGetter['_id']},{'$inc':{'totalItems':value},'$set':{'totalPrice':totalPrice}})
    if itemLog:
        return True
    return False

API_BP = Blueprint('api',__name__,url_prefix='/api/')

@API_BP.route('/products',methods=['GET'])
def stock():
    auth_check = check_login()
    if auth_check:
        print('tidak ada session aktif')
        return auth_check
    items = list(productCollection.collection.find())
    return jsonify(items)
    
@API_BP.route('/roles',methods=['GET','POST'])
def rolesGetter():
    auth_check = check_login()
    if auth_check:
        print("tidak ada session aktif")
        return auth_check
    AuthRole = roleCollection.collection.find_one({'_id':g.user['role']})['permission']['account management']
    if not AuthRole:
        return jsonify({'status':'error','status':'No Access'}),401
    if request.method == 'POST':
        try:
            data = request.get_json()
            for i in data['permission']:
                data['permission'][i] = bool(data['permission'][i])
            print(data)
            uniqueRoleChecker = roleCollection.collection.find_one({
                '$or': [
                    {'permission': data['permission']},
                    {'role-name': data['role-name']}
                ]
            })
            if uniqueRoleChecker:
                return jsonify({
                    'error','roles with the same permission and name already exist'
                }),403
            latestRoleId = roleCollection.collection.find_one(sort=[("_id", -1)])

            if latestRoleId and latestRoleId.get('_id', '').startswith('R'):
                max_id = int(latestRoleId['_id'][1:])
            else:
                max_id = 0
            new_id = f"R{max_id + 1:03d}"
            data['_id'] = new_id
            createRole = roleCollection.collection.insert_one(data)
            if createRole:
                return jsonify({'status':'success','message':'successfuly create data'})
        except Exception as e:
            return jsonify({'status':'error','text':f'Error at adding roles {e}'}),500
    return list(roleCollection.collection.find())

@API_BP.route('/roles/update',methods=['PATCH'])
def updateRole():
    auth_check  = check_login()
    if auth_check:
        print("tidak ada session aktif")
        return auth_check
    AuthRole = roleCollection.collection.find_one({'_id':g.user['role']})['permission']['account management']
    if not AuthRole:
        return jsonify({'error':'No Access'}),401
    try:
        formData = request.get_json()
        del formData['id']
        for i in formData['permission']:
            formData['permission'][i] = bool(formData['permission'][i])
        uniqueRoleChecker = roleCollection.collection.find_one({'role-name':formData['role-name']})
        uniqueRoleCheckerPerm = roleCollection.collection.find_one({'permission':formData['permission']})
        if uniqueRoleChecker and uniqueRoleChecker['_id'] != formData['_id']:
            return jsonify({'message':'roles with the same name already exist','status':'error'}),403
        if uniqueRoleCheckerPerm and uniqueRoleCheckerPerm['_id']!= formData['_id']:
            return jsonify({'message':'roles with the same rules already exist','status':'error'}),403
        if float(formData['role-salary'])<0:
            return jsonify({'message':'salary cannot go below 0!','status':'error'}),403
        dataId =  formData.get('_id')
        roleUpdater = roleCollection.collection.update_one({'_id':dataId},{'$set':formData})
        if roleUpdater:
            return jsonify({"message": "updated successfully","status": "ok"}),202
        return jsonify({"message":'Error at editing roles',"status":"error"}),500
    except Exception as e:
        print(e)
        return jsonify({"message":f'error editing: {e}',"status":"error"}),500

@API_BP.route('/roles/delete',methods=['DELETE'])
def rolesDelete():
    auth_check = check_login()
    if auth_check:
        print("Tidak ada session aktif")
        return auth_check
    AuthRole = roleCollection.collection.find_one({'_id':g.user['role']})['permission']['account management']
    if not AuthRole:
        return jsonify({'error':'No Access'}),401
    try:
        data = request.get_json()
        verifier = userCollection.collection.count_documents({'role':data['_id']})
        if verifier>0:
            return jsonify({'error':'deleting role that still in use'}),403
        deleteRole =  roleCollection.collection.delete_one({'_id':data['_id']})
        if deleteRole:
            return jsonify({'message':"Role deleted successfully"}),202
    except Exception as e:
        return jsonify({'error':f'Error: {e}'}),500

@API_BP.route('/product',methods=['GET'])
def productGetter():
    auth_check = check_login()
    if auth_check:
        print("Tidak ada session aktif")
        return auth_check
    allStock = productCollection.collection.find()
    if allStock:
        return list(allStock)
    return jsonify({
        'message':'error at fetching data',
        'status':"error"
    })

@API_BP.route('/product/detail', methods=['GET'])
def get_product_detail():
    product_id = request.args.get('id')
    if not product_id:
        return jsonify({"error": "Missing ID"}), 400
    product = productCollection.collection.find_one({"_id": product_id})
    if product:
        return jsonify(product)
    else:
        return jsonify({"error": "Product not found"}), 404

@API_BP.route('/product/log', methods=['GET'])
def productLog():
    res = list(productLogCollection.collection.find())
    for i in res:
        i['_id']=str(i['_id'])
    return jsonify(res)

@API_BP.route('/product/create',methods=['POST'])
def productCreator():
    auth_check = check_login()
    if auth_check:
        print("Tidak ada session aktif")
        return auth_check
    AuthRole = roleCollection.collection.find_one({'_id':g.user['role']})['permission']['stock management']
    if not AuthRole:
        return jsonify({'error':'No Access'}),401
    try:
        formData = request.get_json()
        format = {}
        abc = findABC(formData['klasifikasi.analisisABC'])
        newId = findMaxId()
        newId+=1
        newId = f"PRD{newId:04}"
        formData['_id']=newId
        newIdInv = productInventoryCollection.collection.find_one(sort=[("_id", -1)])
        if newIdInv:
            newIdInv = f"INV{int(newIdInv['_id'].split('INV')[1])+1:04}"
        else:
            newIdInv = "INV0001"
        klasifikasi = {
            'namaKategori':rulesetProductCategory(formData['klasifikasi.namaKategori']),
            'analisisABC':abc,
        }
        satuan = {
            'unitJual':formData['satuan.unitJual'],
            'unitSimpan':formData['satuan.unitSimpan'],
        }
        logistik = {
            'referensiDimensiUnitSimpanCM_PLT':formData['logistik.referensiDimensiUnitSimpanCM_PLT'],
            'buyPrice':formData['logistik.buyPrice'],
            'sellPrice':formData['logistik.sellPrice']
        }
        statusKontrol = {
            'status':'Aktif',
            'tglDibuat':datetime.now()
        }

        format = {
            '_id':formData['_id'],
            'barcodeEAN':formData['barcodeEAN'],
            'namaProduk':formData['namaProduk'],
            'deskripsi':formData['deskripsi'],
            'merk':formData['merk'],
            'klasifikasi':klasifikasi,
            'satuan':satuan,
            'logistik':logistik,
            'statusKontrol':statusKontrol
        }
        input = productCollection.collection.insert_one(format)
        log = productLogCollection.collection.insert_one({
            'by':g.user['id'],
            'action':'create',
            'for':formData['_id'],
            'at':datetime.now()
        })
        firstInv = productInventoryCollection.collection.insert_one({
            "_id":newIdInv,
            "productID":formData['_id'],
            "quantityNow":0,
            "primaryLocation":"-",
            "latestAcceptedDate":"-",
            'latestStoredPrice':0
        })
        print(format,log,firstInv)
        if input and log and firstInv:
            return jsonify({'message':'berhasil','status':'success'}),200
        else:
            return jsonify({'message':'there is a problem when inserting data','status':'error'}),500

    except Exception as e:
        print(e)
        return jsonify({'message':'gagal','status':'error'}),500
    
@API_BP.route('/product/update',methods=['POST'])
def updateProduct():
    auth_check = check_login()
    if auth_check:
        print("Tidak ada session aktif")
        return auth_check
    
    AuthRole = roleCollection.collection.find_one({'_id':g.user['role']})['permission']['stock management']
    if not AuthRole:
        return jsonify({'error':'No Access'}),401
    try:
        data = request.get_json()
        if "" in list(data.values()):
            return jsonify({'status':'error'}),400
        abc = findABC(data['klasifikasi.analisisABC'])
        klasifikasi = {
            'namaKategori':rulesetProductCategory(data['klasifikasi.namaKategori']),
            'analisisABC':abc,
        }
        satuan = {
            'unitJual':data['satuan.unitJual'],
            'unitSimpan':data['satuan.unitSimpan'],
        }
        logistik = {
            'referensiDimensiUnitSimpanCM_PLT':data['logistik.referensiDimensiUnitSimpanCM_PLT'],
            'buyPrice':data['logistik.buyPrice'],
            'sellPrice':data['logistik.sellPrice']
        }
        statusKontrol = {
            'status': "Aktif" if data['statusKontrol.status'] == "1" else "Non-Aktif",
            'tglDibuat':datetime.now()
        }
        format = {
            '_id':data['_id'],
            'barcodeEAN':data['barcodeEAN'],
            'namaProduk':data['namaProduk'],
            'deskripsi':data['deskripsi'],
            'merk':data['merk'],
            'klasifikasi':klasifikasi,
            'satuan':satuan,
            'logistik':logistik,
            'statusKontrol':statusKontrol
        }
        result = productCollection.collection.update_one({'_id':data['_id']},{'$set':format})
        log = productLogCollection.collection.insert_one({
            'by':g.user['id'],
            'action':'update',
            'for':data['_id'],
            'at':datetime.now()
        })
        productInStock = productInventoryCollection.collection.find_one({'productID':data['_id']})
        newPrice = float(data['logistik.buyPrice'])*productInStock['quantityNow']
        productInventoryCollection.collection.update_one({'productID':data['_id']},{'$set':{'latestStoredPrice':newPrice}})
        totalCountUpdater(0)
        if result and log:
            print("kok ndak kesini?")
            return jsonify({'status':'success','message':'successfuly updating data'}),201
        else:
            return jsonify({'status':'error','message':'Error at updating data'}),500
    except Exception as e:
        print(e)
        return jsonify({'status':'error','message':f'Error: {e}'}),500
    
@API_BP.route('product/delete',methods=['DELETE'])
def deleteProduct():
    auth_check = check_login()
    if auth_check:
        print("Tidak ada session aktif")
        return auth_check
    AuthRole = roleCollection.collection.find_one({'_id':g.user['role']})['permission']['stock management']
    if not AuthRole:
        return jsonify({'error':'No Access'}),401
    try:
        deletionData = request.get_json()
        deletionData = deletionData['_id']
        itemsQty = int(productInventoryCollection.collection.find_one({'productID':deletionData})['quantityNow'])
        result = productCollection.collection.delete_one({'_id':deletionData})
        log = productLogCollection.collection.insert_one({
            'by':g.user['id'],
            'action':'delete',
            'for':deletionData,
            'at':datetime.now()
        })
        delInv = productInventoryCollection.collection.delete_one({"productID":deletionData})
        print('372')
        reduceTotal = totalCountUpdater(-itemsQty)
        if result and log and delInv and reduceTotal:
            return jsonify({'status':'success','message':'successfuly delete data'}),201
        else:
            return jsonify({'status':'error','message':'fail at deleting product'}),500
    except Exception as e:
        print(e)
        return jsonify({'status':'error','message':f"error: {e}"}),500
    
@API_BP.route('product/inventory',methods=['GET'])
def inventoryGetter():
    auth_check = check_login()
    if auth_check:
        print("Tidak ada session aktif")
        return auth_check
    data = list(productInventoryCollection.collection.find())
    dataClean = [sanitizeForWebix(i) for i in data]
    return jsonify(dataClean)

@API_BP.route('/retailSupply/suppliersGetter',methods=['GET'])
def supplierGetter():
    auth_check = check_login()
    if auth_check:
        print("Tidak ada session aktif")
        return auth_check
    AuthRole = roleCollection.collection.find_one({'_id':g.user['role']})['permission']['retail and shipment']
    if not AuthRole:
        return jsonify({'error':'No Access'}),401
    data = list(supplierCollection.collection.find())
    dataClean = [sanitizeForWebix(i) for i in data]
    return jsonify(dataClean)

@API_BP.route('/retailSupply/retailGetter',methods=['GET'])
def retailGetter():
    auth_check = check_login()
    if auth_check:
        print("Tidak ada session aktif")
        return auth_check
    AuthRole = roleCollection.collection.find_one({'_id':g.user['role']})['permission']['retail and shipment']
    if not AuthRole:
        return jsonify({'error':'No Access'}),401
    data = list(retailCollection.collection.find())
    dataClean = [sanitizeForWebix(i) for i in data]
    return jsonify(dataClean)

@API_BP.route('/suppliers/options')
def supplierOptions():
    data = list(supplierCollection.collection.find())
    out = [{'id':str(r['_id']),'value':str(r['supplierName'])} for r in data]
    print(out)
    return jsonify(out)

@API_BP.route('/product/options',methods=['GET'])
def productOptions():
    data = list(productCollection.collection.find({'statusKontrol.status':{"$ne":'Non-Aktif'}}))
    out = [{'id':str(r['_id']),'value':str(r['_id'])} for r in data]
    print(out)
    return jsonify(out)


@API_BP.route('/arrival/report/create',methods=['POST'])
def arrivalReportCreator():
    auth_check = check_login()
    if auth_check:
        print("Tidak ada session aktif")
        return auth_check
    AuthRole = roleCollection.collection.find_one({'_id':g.user['role']})['permission']['report data']
    if not AuthRole:
        return jsonify({'error':'No Access'}),401
    try:
        now = datetime.now()
        newId = arrivalCollection.collection.find_one(sort=[("_id", -1)])
        if newId:
            newId = int(newId['_id'].split('ARIV')[1])+1
            newId = f"ARIV{newId:05}"
        else:
            newId = "ARIV00001"
        data = request.get_json()
        data['_id']=newId
        data['receivedBy'] = g.user['id']
        data['arrivalDate'] = now
        counter = 0
        totalCount = 0
        for i in data['product']:
            i['id']=newId+i['id']
            i['buyPrice'] = productCollection.collection.find_one({'_id':i['productId']})
            if i['buyPrice']:
                i['buyPrice']=i['buyPrice']['logistik']['buyPrice']
            if int(i['receivedQuantity'])>0:
                counter+=int(i['receivedQuantity'])
                i['subtotalPrice'] = float(i['buyPrice'])*int(i['receivedQuantity'])
                totalCount+=i['subtotalPrice']
                productInventoryCollection.collection.update_one({'productID':i['productId']},{'$inc':{'quantityNow':int(i['receivedQuantity']),'latestStoredPrice':float(i['subtotalPrice'])},'$set':{'latestAcceptedDate':now}})
            else:
                return jsonify({'status':'error'}),400
        data['totalPrice'] = totalCount
        totalCountUpdater(counter)
        result = arrivalCollection.collection.insert_one(data)
        if result:
            return jsonify({'status':'success'}),200
        return jsonify({'status':'error'}),400
    except Exception as e:
        print(e)
        return jsonify({'status':"error"}),400

@API_BP.route('/arrival/report',methods=['GET'])
def arrivalReportGetter():
    reportList = list(arrivalCollection.collection.find())
    return jsonify(reportList)

@API_BP.route('/arrival/detail',methods=['GET'])
def arrivalDetailGetter():
    arrivalId = request.args.get('id')
    if not arrivalId:
        return jsonify({'status':'error'}),400
    itemList = []
    data = arrivalCollection.collection.find_one({'_id':arrivalId})
    for i in data['product']:
        itemList.append(i)
    print(itemList[0])
    return itemList

@API_BP.route('/retail/options',methods=['GET'])
def shipmentOptionsGetter():
    retailList = list(retailCollection.collection.find())
    out = [{'id':str(r['_id']),'value':str(r['_id'])} for r in retailList]
    print(out)
    return jsonify(out)

@API_BP.route('/retail/name',methods=['GET'])
def shipmentRetailName():
    searchId = request.args.get('id')
    name = retailCollection.collection.find_one({'_id':searchId})
    return jsonify(name['retailName']),201


@API_BP.route('/shipments/createShipment', methods=['POST'])
def createShipment():
    auth_check = check_login()
    if auth_check:
        print("Tidak ada session aktif")
        return auth_check
    AuthRole = roleCollection.collection.find_one({'_id':g.user['role']})['permission']['stock management']
    if not AuthRole:
        return jsonify({'error':'No Access'}), 401
    try:
        
        data = request.get_json()
        reqProductId = [x['productId'] for x in data['product']]
        inventoryNow = list(productInventoryCollection.collection.find(
            {'productID': {'$in': reqProductId}}
        ))
        inventoryChecker = {item['productID']: item.get('quantityNow', 0) for item in inventoryNow}
        
        for item in data['product']:
            prodId = item['productId']
            ReqQty = int(item['shippedQuantity'])
            availableQty = inventoryChecker.get(prodId, 0)
            
            if availableQty < ReqQty:
                return jsonify({
                    'status': 'error',
                    'message': f'Insufficient stock for Product {prodId}. Available: {availableQty}, Requested: {ReqQty}'
                }), 400
        
        newId_doc = shipmentCollection.collection.find_one(sort=[("_id", -1)])
        if newId_doc:
            current_num = int(newId_doc['_id'].split('SHP')[1]) + 1
            newId = f"SHP{current_num:05}"
        else:
            newId = "SHP00001"
        data['_id'] = newId
        data['shippedAt'] = datetime.now()
        data['createdBy'] = g.user['id']
        retailLocation = retailCollection.collection.find_one({'_id': data['retailId']})['retailAddress']
        data['address'] = retailLocation

        counter = 0
        for _ in data['product']:
            counter+=int(_['shippedQuantity'])
        totalCount=0
        totalBuyCount=0 
        for i in data['product']:
            if 'id' in i: 
                i['id'] = newId + i['id']
                fetchDataLogistik = productCollection.collection.find_one({'_id':i['productId']})['logistik']
                i['sellPrice'] = fetchDataLogistik['sellPrice']
                i['subtotalPrice'] = float(i['sellPrice'])*int(i['shippedQuantity'])
                totalBuyCount+= float(fetchDataLogistik['buyPrice'])*int(i['shippedQuantity'])
                print(float(i['subtotalPrice']))
                productInventoryCollection.collection.update_one({'productID': i['productId']},{'$inc': {'quantityNow': -int(i['shippedQuantity']),'latestStoredPrice':-float(totalBuyCount)}})
                totalCount+=i['subtotalPrice']
        data['totalPrice'] = totalCount
        send = shipmentCollection.collection.insert_one(data)
        itemLog = totalCountUpdater(-counter)
        if send and itemLog:
            return jsonify({'status': 'success', 'shipmentId': newId}), 201
        return jsonify({'status': 'error'}), 400
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 400
    
@API_BP.route('shipments/log',methods=['GET'])
def shipmentLogGetter():
    return list(shipmentCollection.collection.find())

@API_BP.route('shipments/detail',methods=['GET'])
def shipmentItemGetter():
    shipmentId = request.args.get('id')
    print(shipmentId)
    items = shipmentCollection.collection.find_one({'_id':shipmentId})
    items = items['product']
    print(items)
    return jsonify(items)


@API_BP.route('/retailSupply/supplierCreator',methods=['POST'])
def supplyCreator():
    auth_check = check_login()
    if auth_check:
        print("Tidak ada session aktif")
        return auth_check
    AuthRole = roleCollection.collection.find_one({'_id':g.user['role']})['permission']['retail and shipment']
    if not AuthRole:
        return jsonify({'error':'No Access'}), 401
    try:
        data = request.get_json()
        if data:
            newId = supplierCollection.collection.find_one(sort=[('_id',-1)])
            if newId:
                newId = int(newId['_id'].split("SUPP")[1])
                newId = f"SUPP{newId+1:04}"
            else:
                newId = "SUPP0001"
            data['_id'] = newId
            data['createdAt'] = datetime.now()
            supplierCollection.collection.insert_one(data)
            return jsonify({
                'status':'success',
                'message':'success'
            }),201
    except Exception as e:
        print(e)
        return jsonify({
            'status':'error',
            'text':e
        }),400
    
@API_BP.route('/retailSupply/retailCreator',methods=['POST'])
def retailCreator():
    auth_check = check_login()
    if auth_check:
        print("Tidak ada session aktif")
        return auth_check
    AuthRole = roleCollection.collection.find_one({'_id':g.user['role']})['permission']['retail and shipment']
    if not AuthRole:
        return jsonify({'error':'No Access'}), 401
    try:
        data = request.get_json()
        if data:
            newId = retailCollection.collection.find_one(sort=[('_id',-1)])
            if newId:
                newId = int(newId['_id'].split("RET")[1])
                newId = f"RET{newId+1:03}"
            else:
                newId = "RET0001"
            data['_id'] = newId
            data['createdAt'] = datetime.now()
            retailCollection.collection.insert_one(data)
            return jsonify({
                'status':'success',
                'message':'success'
            }),201
    except Exception as e:
        print(e)
        return jsonify({
            'status':'error',
            'message':e
        }),400
    
@API_BP.route('/retailSupply/supplierUpdater',methods=['POST'])
def supplierUpdater():
    auth_check = check_login()
    if auth_check:
        print("Tidak ada session aktif")
        return auth_check
    AuthRole = roleCollection.collection.find_one({'_id':g.user['role']})['permission']['retail and shipment']
    if not AuthRole:
        return jsonify({'error':'No Access'}), 401
    try:
        data = request.form
        dataId = data.get('_id')
        if data.get('webix_operation') == 'update':
            updateData = {}
            for key,value in data.items():
                if key not in ['id','webix_operation','targetId']:
                    updateData[key] = value
            result = supplierCollection.collection.update_one(
                {'_id':dataId},
                {'$set':updateData}
            )
            if result:
                return jsonify({'status':'success'}),200
        return jsonify({'status':'error'}),500
    except Exception as e:
        print(f"Error update: {e}")
        return jsonify({"status":"error"}),500
    
@API_BP.route('/retailSupply/retailUpdater',methods=['POST'])
def retailUpdater():
    auth_check = check_login()
    if auth_check:
        print("Tidak ada session aktif")
        return auth_check
    AuthRole = roleCollection.collection.find_one({'_id':g.user['role']})['permission']['retail and shipment']
    if not AuthRole:
        return jsonify({'error':'No Access'}), 401
    try:
        data = request.form
        dataId = data.get('_id')
        if data.get('webix_operation') == 'update':
            updateData = {}
            for key,value in data.items():
                if key not in ['id','webix_operation','targetId']:
                    updateData[key] = value
            result = retailCollection.collection.update_one(
                {'_id':dataId},
                {'$set':updateData}
            )
            if result:
                return jsonify({'status':'success'}),200
        return jsonify({'status':'error'}),500
    except Exception as e:
        print(f"Error update: {e}")
        return jsonify({"status":"error"}),500
    
@API_BP.route('/retailSupply/supplierDeleter',methods=['DELETE'])
def supplierDelete():
    auth_check = check_login()
    if auth_check:
        print("Tidak ada session aktif")
        return auth_check
    AuthRole = roleCollection.collection.find_one({'_id':g.user['role']})['permission']['retail and shipment']
    if not AuthRole:
        return jsonify({'error':'No Access'}), 401
    try:
        data = request.get_json()
        result = supplierCollection.collection.delete_one({'_id':data['_id']})
        if result:
            return jsonify({'status':'success','message':'data deleted'}),200
        return jsonify({'status':'error','message':'unknown error'}),500
    except Exception as e:
        print(f"Error delete: {e}")
        return jsonify({"status":"error","message":str(e)}),500
    
@API_BP.route('/retailSupply/retailDeleter',methods=['DELETE'])
def retailDelete():
    auth_check = check_login()
    if auth_check:
        print("Tidak ada session aktif")
        return auth_check
    AuthRole = roleCollection.collection.find_one({'_id':g.user['role']})['permission']['retail and shipment']
    if not AuthRole:
        return jsonify({'error':'No Access'}), 401
    try:
        data = request.get_json()
        result = retailCollection.collection.delete_one({'_id':data['_id']})
        if result:
            return jsonify({'status':'success','message':'data deleted'}),200
        return jsonify({'status':'error','message':'unknown error'}),500
    except Exception as e:
        print(f"Error delete: {e}")
        return jsonify({"status":"error","message":str(e)}),500
    
@API_BP.route('/locationSetter',methods=['POST'])
def locationSetter():
    auth_check = check_login()
    if auth_check:
        print("tidak")
        return auth_check
    AuthRole = roleCollection.collection.find_one({'_id':g.user['role']})['permission']['report data']
    if not AuthRole:
        return jsonify({'error':'No Access'}), 401
    try:
        data = request.form
        dataId = data.get('_id')
        if data.get('webix_operation') == 'update':
            updateData = {}
            for key,value in data.items():
                if key not in ['id','webix_operation','targetId','_id','productID','quantityNow','latestAcceptedDate','latestStoredPrice']:
                    updateData[key] = value
            result = productInventoryCollection.collection.update_one(
                {'_id':dataId},
                {'$set':updateData}
            )
            if result:
                return jsonify({'status':'success'}),200
        return jsonify({'status':'error'}),500
    except Exception as e:
        print(f"Error update: {e}")
        return jsonify({"status":"error"}),500
    
@API_BP.route('/dashboard-counter',methods=['GET'])
def itemCounterGetter():
    auth_check = check_login()
    if auth_check:
        print("tidak")
        return auth_check
    try:
        return list(inventoryCountCollection.collection.find())
    except Exception as e:
        print(e)
        jsonify({'status':'error'}),500