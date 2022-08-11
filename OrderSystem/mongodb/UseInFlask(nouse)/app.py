from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')
    
@app.route("/bucket/done", methods=["POST"])
def bucket_done():
    num_receive = request.form['num_give']
    return jsonify({"msg":"완료!"})
    
    
@app.route("/bucket", methods=["GET"])
def bucket_get():
   return jsonify({'msg': "완료!"})
   
if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)