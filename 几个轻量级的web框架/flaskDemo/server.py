from flask import Flask, request, render_template
import json

app = Flask(__name__)

# http://localhost:3002/path/1000
@app.route('/path/<id>')
def f1(id):
    return id

# http://localhost:3002/querystring?a=laowang
@app.route('/querystring')
def f2():
    a = request.args.to_dict().get("a")
    return a

@app.route('/form',methods=['post'])  # method 默认只有get
def f3():
    b = request.form.to_dict().get("b")
    return b

@app.route('/json',methods=['post'])
def f4():
    jsonstr = request.data.decode('utf-8')
    c =json.loads(jsonstr).get("c")
    return str(c)

@app.route('/')
def hello():
    print(request.headers.get('a'))
    return {'a':11,'b':'ffffff'},200,{"f":"g"}

@app.route('/post',methods=['post'])
def hello2():
    # return "hello flask"
    # return app.send_static_file("hello.html")  # 这个默认去static里找
    return render_template("test.html")  # 这个默认去templates里找

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0',port=3002)