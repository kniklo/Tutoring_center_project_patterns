from quart import Quart, render_template, request, session, redirect, url_for, jsonify, current_app
from dao import MySQLDAOFactory, SingletonDatabaseConnection
from builder_classes import UserBuilder, RepetitorBuilder

rolesstr = ('Гость', 'Репетитор', 'Клиент')
roles = ('', 'tutor', 'client')
selectedQueryId = -1

app = Quart(__name__)
app.secret_key = 'abcdef'

# Инициализация подключения к базе данных и фабрики DAO при запуске приложения
@app.before_serving
async def before_serving():
    connection = SingletonDatabaseConnection()
    await connection.connect()
    app.config['database_connection'] = connection

    dao_factory = MySQLDAOFactory()
    app.config['dao_factory'] = dao_factory

# Закрытие подключения к базе данных при завершении работы приложения
@app.after_serving
async def after_serving():
    connection = app.config.get('database_connection')
    if connection:
        await connection.close()

@app.route('/')
async def index():
    dao_factory = current_app.config.get('dao_factory')
    dao = dao_factory.create_dao()
    data = {}
    if 'login' in session:
        authorized = True
        usertypestr = rolesstr[session['login'][2]]
        usertype = roles[session['login'][2]]
        name = session['login'][3]
        if usertype == 'client':
            data['head'] = {'authorized': authorized, 'usertypestr': usertypestr, 'usertype': usertype, 'name': name}
        elif usertype == 'tutor':
            data['head'] = {'authorized': authorized, 'usertypestr': usertypestr, 'usertype': usertype, 'name': name}
    else:
        authorized = False
        usertypestr = rolesstr[0]
        usertype = roles[0]
        name = ''
        data['head'] = {'authorized': authorized, 'usertypestr': usertypestr, 'usertype': usertype, 'name': name}
        repetitors = await dao.get_repetitors()
        data['repetitors'] = repetitors

    return await render_template('index.html', data=data)

@app.route('/add_query', methods=['GET', 'POST'])
async def add_query():
    dao_factory = current_app.config.get('dao_factory')
    dao = dao_factory.create_dao()
    a = await request.form
    user_id = session['login'][0]
    subject_id = int(a['subject_id'])
    theme = a['theme']
    qtext = a['qtext']
    await dao.add_query(user_id, subject_id, theme, qtext)
    return redirect(url_for('index'))

@app.route('/accept_request', methods=['GET', 'POST'])
async def accept_request():
    dao_factory = current_app.config.get('dao_factory')
    dao = dao_factory.create_dao()
    a = await request.form
    user_id = session['login'][0]
    request_id = int(a['request_id'])
    await dao.accept_request(user_id, request_id)
    return redirect(url_for('index'))

@app.route('/confirm_request', methods=['GET', 'POST'])
async def confirm_request():
    dao_factory = current_app.config.get('dao_factory')
    dao = dao_factory.create_dao()
    a = await request.form
    user_id = session['login'][0]
    request_id = int(a['request_id'])
    await dao.confirm_request(user_id, request_id)
    return redirect(url_for('index'))

@app.route('/finish_request', methods=['GET', 'POST'])
async def finish_request():
    dao_factory = current_app.config.get('dao_factory')
    dao = dao_factory.create_dao()
    a = await request.form
    request_id = int(a['request_id'])
    await dao.finish_request(request_id)
    return redirect(url_for('index'))

@app.route('/restore_status', methods=['GET', 'POST'])
async def restore_status():
    dao_factory = current_app.config.get('dao_factory')
    dao = dao_factory.create_dao()
    a = await request.form
    request_id = int(a['request_id'])
    await dao.restore_status(request_id)
    return redirect(url_for('index'))

@app.route('/get_tutorrequestlist')
async def get_tutorrequestlist():
    dao_factory = current_app.config.get('dao_factory')
    dao = dao_factory.create_dao()
    status_id = 0
    user_id = session['login'][0]
    querylist1, querylist2 = await dao.get_tutorrequestlist(status_id, user_id)
    return jsonify({'requestlist': {'t1': querylist1, 't2': querylist2}})

@app.route('/get_clientrequestlist')
async def get_clientrequestlist():
    dao_factory = current_app.config.get('dao_factory')
    dao = dao_factory.create_dao()
    user_id = session['login'][0]
    querylist = await dao.get_clientrequestlist(user_id)
    return jsonify({'requestlist': querylist})

@app.route('/get_request_details/<int:request_id>', methods=['GET'])
async def get_request_details(request_id):
    dao_factory = current_app.config.get('dao_factory')
    dao = dao_factory.create_dao()
    query = await dao.get_request_details(request_id)
    return jsonify({'query': query})

@app.route('/register')
async def register():
    return await render_template('register.html')

@app.route('/register_client', methods=['GET', 'POST'])
async def register_client():
    dao_factory = current_app.config.get('dao_factory')
    dao = dao_factory.create_dao()
    if request.method == 'POST':
        form = await request.form
        login = form['login']
        password = form['password']
        name = form['name']
        email = form['email']
        userbuilder = UserBuilder(login, password)
        user = userbuilder.set_name(name).set_email(email).build()
        try:
            await dao.register_client(user)
            footer = 'Клиент зарегистрирован в базе данных. Можете авторизоваться.'
            return await render_template('register_client.html', footer=footer)
        except Exception as error:
            cod = error.args[0]
            if cod == 1062:
                footer = 'Логин уже существует!'
            else:
                footer = error.args[1]
            return await render_template('register_client.html', footer=footer)

    footer = ''
    return await render_template('register_client.html', footer=footer)

@app.route('/register_tutor', methods=['GET', 'POST'])
async def register_tutor():
    dao_factory = current_app.config.get('dao_factory')
    dao = dao_factory.create_dao()
    if request.method == 'POST':
        form = await request.form
        login = form['login']
        password = form['password']
        name = form['name']
        email = form['email']
        userbuilder = UserBuilder(login, password)
        user = userbuilder.set_name(name).set_email(email).build()
        try:
            await dao.register_tutor(user)
            footer = 'Репетитор зарегистрирован в базе данных. Можете авторизоваться.'
            return await render_template('register_tutor.html', footer=footer)
        except Exception as error:
            cod = error.args[0]
            if cod == 1062:
                footer = 'Логин уже существует!'
            else:
                footer = error.args[1]
            return await render_template('register_client.html', footer=footer)

    footer = ''
    return await render_template('register_tutor.html', footer=footer)

@app.route('/login', methods=['GET', 'POST'])
async def login():
    dao_factory = current_app.config.get('dao_factory')
    dao = dao_factory.create_dao()
    if request.method == 'POST':
        form = await request.form
        login = form['login']
        password = form['password']
        user = await dao.login(login, password)
        if user:
            session['login'] = user
            return redirect(url_for('index'))
        else:
            footer = 'Не верное имя пользователя или пароль'
            return await render_template('login.html', footer=footer)

    footer = ''
    return await render_template('login.html', footer=footer)

@app.route('/logout')
async def logout():
    session.pop('login', None)
    return redirect(url_for('index'))

@app.route('/personal_client')
async def personal_client():
    return await render_template('personal_client.html')

@app.route('/personal_tutor', methods=['GET', 'POST'])
async def personal_tutor():
    dao_factory = current_app.config.get('dao_factory')
    dao = dao_factory.create_dao()
    if request.method == 'GET':
        user_id = session['login'][0]
        userdata, subjects, allsubjects = await dao.personal_tutor_get(user_id)
        data = {'userdata': userdata, 'subjects': subjects, 'allsubjects': allsubjects}
        return await render_template('personal_tutor.html', data=data)
    elif request.method == 'POST':
        form = await request.form
        repbuilder = RepetitorBuilder(login, '')
        repetitor = repbuilder.set_name(form['name']).set_email(form['email']).set_hourly_rate(form['hourly_rate']).set_indeal(1).build()
        await dao.personal_tutor_post(repetitor, session['login'][0])
        return redirect(url_for('personal_tutor'))

@app.route('/get_allsubjects', methods=['GET', 'POST'])
async def get_allsubjects():
    dao_factory = current_app.config.get('dao_factory')
    dao = dao_factory.create_dao()
    subjects = await dao.get_allsubjects()
    print("-----------", subjects)
    return jsonify({'subjects': subjects})

@app.route('/add_subject', methods=['GET', 'POST'])
async def add_subject():
    dao_factory = current_app.config.get('dao_factory')
    dao = dao_factory.create_dao()
    a = await request.form
    subject_id = int(a['subject'])
    user_id = session['login'][0]
    await dao.add_subject(subject_id, user_id)
    return redirect(url_for('personal_tutor'))

@app.route('/remove_subject', methods=['GET', 'POST'])
async def remove_subject():
    dao_factory = current_app.config.get('dao_factory')
    dao = dao_factory.create_dao()
    a = await request.form
    subject_id = int(a['subject'])
    user_id = session['login'][0]
    await dao.remove_subject(subject_id, user_id)
    return redirect(url_for('personal_tutor'))

@app.route("/sql_request", methods=['GET', 'POST'])
async def sql_request():
    dao_factory = current_app.config.get('dao_factory')
    dao = dao_factory.create_dao()
    result = await dao.sql_request()
    data = {}
    data['result'] = result
    return await render_template('sql_request.html', data=data)

if __name__ == '__main__':
    app.run(host="0.0.0.0")
