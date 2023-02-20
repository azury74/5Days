from flask import Flask,render_template,request, url_for, redirect, render_template,current_app, g,session,flash, send_from_directory,jsonify
import click
import os 
from flask_sqlalchemy import SQLAlchemy
import pandas as pd 
import difflib

app = Flask(__name__)


#---------------------------------------------------------------------------------------
#Page de l'interface : 

@app.route('/')
def accueil():
    return render_template('index.html')

@app.route('/recherche')
def recherche():  
    return render_template('recherche.html',info=get_info_all()[0:100])

@app.route('/recherche_formulaire')
def recherche_formulaire():
    return render_template('recherche_formulaire.html',info=get_info_all()[0:50])

@app.route('/marque', methods=['GET', 'POST'])
def marque():
    if request.method == "POST":
        marque=request.form["Marque"]
        query = db.session.query(Car.brand).distinct().all()
        titles = [row[0] for row in query]
        closest_titles = difflib.get_close_matches(marque, titles)
        
        try :
            cars = Car.query.filter_by(brand=closest_titles[0]).all()
            info=[]
            
            for car in cars:
                info.append([car.brand,car.model,car.price,car.year,car.mileage,car.color,car.vin])
        except IndexError :
            info=[["Pas de résultat"]]
                
        return render_template('marque.html',info=info[0:50])
    else : 
        return render_template('marque.html',info=get_info_all()[0:50])
    
    
@app.route('/modèle', methods=['GET', 'POST'])
def modèle():
    if request.method == "POST":
        marque=request.form["Modèle"]
        query = db.session.query(Car.model).distinct().all()
        titles = [row[0] for row in query]
        closest_titles = difflib.get_close_matches(marque, titles)
        
        try :
            cars = Car.query.filter_by(model=closest_titles[0]).all()
            info=[]
            
            for car in cars:
                info.append([car.brand,car.model,car.price,car.year,car.mileage,car.color,car.vin])
        except IndexError :
            info=[["Pas de résultat"]]
                
        return render_template('modèle.html',info=info[0:50])
    else : 
        return render_template('modèle.html',info=get_info_all()[0:50])

@app.route('/couleur', methods=['GET', 'POST'])
def couleur():
    if request.method == "POST":
        marque=request.form["Couleur"]
        query = db.session.query(Car.color).distinct().all()
        titles = [row[0] for row in query]
        closest_titles = difflib.get_close_matches(marque, titles)
        
        try :
            cars = Car.query.filter_by(color=closest_titles[0]).all()
            info=[]
            
            for car in cars:
                info.append([car.brand,car.model,car.price,car.year,car.mileage,car.color,car.vin])
        except IndexError :
            info=[["Pas de résultat"]]
                
        return render_template('couleur.html',info=info[0:50])
    else : 
        return render_template('couleur.html',info=get_info_all()[0:50])

#---------------------------------------------------------------------------------------
#Fonction de récupération des données 
def get_info_all():
    cars = Car.query.all()
    info=[]
    for car in cars:
        info.append([car.brand,car.model,car.price,car.year,car.mileage,car.color,car.vin])
    return info

def get_info_dict():
    cars = Car.query.all()
    info=[]
    for car in cars:
        info.append({"Marque":car.brand,"Modele":car.model,"Prix":car.price,"Annee":car.year,"Kilometrage":car.mileage,"Couleur":car.color,"VIN":car.vin})
    return info
#---------------------------------------------------------------------------------------
#API : 
@app.route('/API/cars',methods=['GET'])
def get_cars():
    
    return jsonify({
        "status":"ok",
        "data":get_info_dict()[0:50]})

@app.route('/API/cars/<ids>',methods=['GET'])
def get_cars_by_id(ids):
    car = Car.query.filter_by(id=int(ids)).all()
    if(len(car)==0):
        return jsonify({
            "message":"Cette voiture n'existe pas !"}),410
    return jsonify({
        "status":"ok",
        "data":[car[0].brand,car[0].model,car[0].price,car[0].year,car[0].mileage,car[0].color,car[0].vin]})

@app.route('/API/cars',methods=['POST'])
def add_cars():
    import json
    try :
        if request.method == "POST":
            cars_data_dict = json.loads(request.data.decode("utf8"))
           
            car = Car(
                id = cars_data_dict["id"],
                price = cars_data_dict["price"],
                brand =cars_data_dict["brand"], 
                model = cars_data_dict["model"],
                year = cars_data_dict["year"],
                title_status = cars_data_dict["title_status"],
                mileage = cars_data_dict["mileage"],
                color = cars_data_dict["color"],
                vin = cars_data_dict["vin"],
                lot = cars_data_dict["lot"]
            )
           
            db.session.add(car)
            db.session.commit()
        return jsonify({
            "status":"ok",
            "message":"La voiture a été ajouté !"})
    except  : 
        return jsonify({
            "status":"NOK",
            "message":"Problème lors de l'ajout !"})

@app.route('/API/cars',methods=['PUT'])
def put_cars():
    import json
    
    if request.method == "PUT":
        cars_data_dict = json.loads(request.data.decode("utf8"))
        
        try :
            cars = Car.query.filter_by(id=cars_data_dict["id"]).all()
            if(len(cars)==0):
                return jsonify({
                    "message":"Cette voiture n'existe pas !"}),410
        except :
            return jsonify({
                    "message":"Cette voiture n'existe pas !",
                    "status":201}),410
        
        Car.query.filter_by(id=cars_data_dict["id"]).delete()
        db.session.commit()
        
        car = Car(
            id = cars_data_dict["id"],
            price = cars_data_dict["price"],
            brand =cars_data_dict["brand"], 
            model = cars_data_dict["model"],
            year = cars_data_dict["year"],
            title_status = cars_data_dict["title_status"],
            mileage = cars_data_dict["mileage"],
            color = cars_data_dict["color"],
            vin = cars_data_dict["vin"],
            lot = cars_data_dict["lot"]
        )
       
        db.session.add(car)
        db.session.commit()
    return jsonify({
        "status":"ok",
        "message":"La voiture a été remplacé !"})


@app.route('/API/cars',methods=['PATCH'])
def patch_cars():
    import json
    
    if request.method == "PATCH":
        cars_data_dict = json.loads(request.data.decode("utf8"))
        
        try :
            cars = Car.query.filter_by(id=cars_data_dict["id"]).all()
            if(len(cars)==0):
                return jsonify({
                    "message":"Cette voiture n'existe pas !"}),410
        except :
            return jsonify({
                    "message":"Cette voiture n'existe pas !",
                    "status":201}),410
        
        carFind = Car.query.filter_by(id=cars_data_dict["id"]).first()
        
        if("price" in cars_data_dict):
            carFind.price=cars_data_dict["price"]
        if("brand" in cars_data_dict):
            carFind.brand=cars_data_dict["brand"]
        if("model" in cars_data_dict):
            carFind.model=cars_data_dict["model"]
        if("year" in cars_data_dict):
            carFind.year=cars_data_dict["year"]
        if("title_status" in cars_data_dict):
            carFind.title_status=cars_data_dict["title_status"]
        if("mileage" in cars_data_dict):
            carFind.mileage=cars_data_dict["mileage"]
        if("color" in cars_data_dict):
            carFind.color=cars_data_dict["color"]
        if("vin" in cars_data_dict):
            carFind.vin=cars_data_dict["vin"]
        if("lot" in cars_data_dict):
            carFind.lot=cars_data_dict["lot"]
            
        db.session.commit()
    return jsonify({
        "status":"ok",
            "message":"La voiture a été modifié !"})

@app.route('/API/cars',methods=['DELETE'])
def delete_cars():
    import json
    
    if request.method == "DELETE":
        cars_data_dict = json.loads(request.data.decode("utf8"))
        
        try :
            cars = Car.query.filter_by(id=cars_data_dict["id"]).all()
            if(len(cars)==0):
                return jsonify({
                    "message":"Cette voiture n'existe pas"}),410
        except :
            return jsonify({
                    "message":"Cette voiture n'existe pas !",
                    "status":201}),410
        Car.query.filter_by(id=cars_data_dict["id"]).delete()
        db.session.commit()
    return jsonify({
        "status":"ok",
            "message":"La voiture a été supprimé !"})
#---------------------------------------------------------------------------------------
#REST
if __name__ == '__main__':
    app.run()

    
