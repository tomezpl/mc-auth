from os import getcwd
import os.path
from flask import Flask

app = Flask(__name__)

wwwroot = os.path.join(getcwd(), 'wwwroot')

@app.route('/')
def home():
    viewFile = open(os.path.join(wwwroot, 'index.html'))
    viewHtml = ''.join(viewFile.readlines())
    viewFile.close()
    return viewHtml

@app.route('/main.js')
def js():
    jsFile = open(os.path.join(wwwroot, 'main.js'))
    jsCode = ''.join(jsFile.readlines())
    jsFile.close()
    return jsCode