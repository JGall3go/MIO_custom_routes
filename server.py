from flask import Flask
from flask import render_template

app = Flask(__name__)

@app.route('/1')
def mapa_version_1():
    return render_template('mapa_con_marcador.html')

@app.route('/2')
def mapa_version_2():
    return render_template('gmaps.html')

if __name__ == '__main__':
    app.run(debug=True)