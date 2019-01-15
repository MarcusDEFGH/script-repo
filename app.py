from flask import Flask, request, render_template, send_from_directory, Response
from wtforms import Form, StringField
from os import listdir
from os.path import isfile, join
import subprocess
import collections


app = Flask(__name__)


class Script:

    def __init__(self, name, description, arguments):
        self.name = name
        self.description = description
        self.arguments = arguments
    
    def __repr__(self):
        arguments = ["Name: {}\nHelper: {}".format(*argument) for argument in self.arguments]
        return "Script: {}\n".format(self.name) + '\n'.join(arguments)


def identify_arguments(script_name):
    Argument = collections.namedtuple('Argument', ['name', 'helper'])
    bashCommand = "python ./scripts/{} -h".format(script_name)
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()

    output = str(output.decode('utf-8')).split('\n')

    args_start = output.index('positional arguments:') + 1
    args_end = output.index('optional arguments:')
    args_raw = output[args_start:args_end]
    args_raw = [arg.split('  ') for arg in args_raw]
    clean_args = [arg.strip() for args in args_raw for arg in args if arg.strip()]
    description = output[2]

    return ([Argument(name, helper)
            for name, helper in zip(clean_args[0::2],
                                    clean_args[1::2])],
            description)


@app.route('/')
def index():
    folder = "./scripts"
    files = [f for f in listdir(folder) if isfile(join(folder, f))]
    scripts = []
    for f in files:
        arguments,description = identify_arguments(f)
        scripts.append(Script(f, description, arguments))
    return render_template('index.html', arguments=arguments, scripts=scripts)


@app.route('/<script_name>/', methods=['GET', 'POST'])
def script(script_name):

    class ScriptForm(Form):
        pass
    
    arguments = identify_arguments(script_name)[0]
    for argument in arguments:
        setattr(ScriptForm, argument.name, StringField(description=argument.helper))
    form = ScriptForm(request.form)
    if request.method == 'POST' and form.validate():
        bashCommand = "python ./scripts/{} ".format(script_name)
        for key in form:
            bashCommand += ' {}'.format(key.data)
        process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()
        return Response(output,
                       mimetype="text/plain",
                       headers={"Content-Disposition":
                                    "attachment;filename=output.txt"})

    return render_template('script.html', form=form, script=script)


@app.route('/favicon.ico') 
def favicon(): 
    return send_from_directory(join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')


if __name__ == '__main__':
    app.run(debug=True)