from app import app

if __name__ == '__main__':
    #app.run(ssl_context=('cert.pem', 'key.pem'), port=80, debug=True) #dev only
    #app.run(ssl_context='adhoc') # dev only
    app.run(debug=True)
