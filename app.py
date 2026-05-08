from flask import Flask, redirect, render_template, url_for, session , request,jsonify
from flask_cors import CORS
from bson import ObjectId
from pymongo import MongoClient
from flask import make_response
from reportlab.platypus import SimpleDocTemplate, Table
from reportlab.platypus.tables import TableStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
import io

app = Flask(__name__)
CORS(app)

MyClient = MongoClient("mongodb+srv://muralispc117:Murali1234@cluster0.v9gz99u.mongodb.net/")
db = MyClient['electiondatabase-104']
votersdata = db['votersdetails']

@app.route('/')
def home():

    totalvoters = votersdata.count_documents({})

    malevoters = votersdata.count_documents({
        'gender': 'male'
    })

    femalevoters = votersdata.count_documents({
        'gender': 'female'
    })

    return render_template(
        'home.html',
        totalvoters=totalvoters,
        malevoters=malevoters,
        femalevoters=femalevoters
    )
   

@app.route('/allvoterspage')
def allvoters():
    data = votersdata.find({})
    return render_template('index.html', data=data)

@app.route('/tofilter', methods = ['GET'])
def tofilter():
    querry = {}
    name = request.args.get('name')
    boothno = request.args.get('boothno')
    gender = request.args.get('gender')
    if name :
        querry['name'] ={'$regex': name, '$options': 'i'}
    if boothno :
        querry['boothno'] = int(boothno)
    if  gender != 'select'  :
        querry['gender'] = gender
    
    data = list(votersdata.find(querry))
    return render_template('index.html', data=data)

@app.route('/staticspage')
def staticspage():
    return render_template('statictics.html')

@app.route('/pollingstatuspage')
def pollingstatus():
    data = votersdata.find({})
    totalvotes = votersdata.count_documents({})
    voteddata = votersdata.count_documents({'votestatus':'voted'})
    notvoteddata = votersdata.count_documents({'votestatus' : 'not voted'})
    return render_template('polling.html', data=data, voteddata = voteddata, notvoteddata = notvoteddata, totalvotes=totalvotes)

@app.route('/votingstatus', methods=['POST'])
def getvoters():
    changevotestatus = request.get_json()
    print(changevotestatus)
    vote=  changevotestatus['votestatus']
    print(vote)
    voterobjid = changevotestatus['voterid']
    votersdata.update({'_id': ObjectId(voterobjid)})

    return jsonify({'total' : 'Murali'})


@app.route('/duplicatevoterspage')
def duplicatevoters():
    return render_template('duplicate.html')

@app.route('/pdfexportpage')
def pdfexport():
    data = votersdata.distinct('boothno')
    return render_template('pdfexport.html' ,data = data)

@app.route('/meetingpage')
def meeting():
    return render_template('meeting.html')

@app.route('/notificationpage')
def notification():
    return render_template('notification.html')

@app.route('/exportpdf',methods = ['GET'])
def exportpdf():
    
    boothnumber = request.args.get('boothno')
    querry = {}
    if boothnumber != 'Select Booth No':
        querry['boothno'] = int(boothnumber)
        data = list(votersdata.find(querry))
    
    pdf_buffer = io.BytesIO()

    pdf = SimpleDocTemplate(
        pdf_buffer,
        pagesize=letter
    )

    table_data = []

    # Table Heading
    table_data.append([
        'Serial No',
        'EPIC no',
        'Name',
        'Relation Name',
        'Age',
        'Booth No'
    ])

    # MongoDB Data
    for i in data:
        table_data.append([
            i.get('serialno'),
            i.get('epicid'),
            i.get('name'),
             i.get('relationname'),
            i.get('age'),
             i.get('boothno')
        ])

    table = Table(table_data)

    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),

        ('GRID', (0,0), (-1,-1), 1, colors.black),

        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold')
    ]))

    elements = [table]

    pdf.build(elements)

    response = make_response(pdf_buffer.getvalue())

    response.headers['Content-Type'] = 'application/pdf'
    pdfname = "Voters - " + str(boothnumber)

    response.headers['Content-Disposition'] = f'attachment; filename={pdfname}.pdf'

    return response

if __name__ == "__main__":
    app.run(debug = True)