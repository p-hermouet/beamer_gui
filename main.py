from bottle import Bottle, run, view, request, static_file


app = Bottle()


@app.route('/')
@view('templates/home.tpl')
def home():
    context = {'title': 'TITLE bla', 'filename': 'page.png'}
    return context


@app.get('/<filename:re:.*.css>')
def css(filename):
    return static_file(filename, root='static/')



@app.get('/<filename:re:.*.png>')
def png(filename):
    return static_file(filename, root='static/')


if __name__ == "__main__":
    run(app, host='localhost', port=8080, reloader=True)
