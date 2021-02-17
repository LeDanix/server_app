import streamlit as st
import time
import numpy as np
import json
#import requests
import urllib.request

try:
    import streamlit.ReportThread as ReportThread
    from streamlit.server import Server
except Exception:
    # Streamlit >= 0.65.0
    import streamlit.report_thread as ReportThread
    from streamlit.server.server import Server

prev_time = 0
track_number = 0
tempos = []
user_tempo_tracks = [0] * 30
final_score = 0
questions = ['I am a musician', 'I play a instrument but I don\'t consider myself a musician ',
             'I have ever played an instrument', 'I have never played an instrument']
track_path = ['music/Atlantic_City.mp3',
              'music/All_Stars.mp3',  
              'music/Atlantic_City1.mp3',
              'music/All_Stars.mp3',
              'music/Atlantic_City2.mp3',
              'music/All_Stars.mp3',
              'music/Atlantic_City3.mp3']
names = ['1º Track', '2º Track', '3º Track', '4º Track', '5º Track', '6º Track', '7º Track', '8º Track', '9º Track',
         '10º Track', '11º Track', '12º Track', '13º Track', '14º Track', '15º Track', '16º Track', '17º Track',
         '18º Track', '19º Track', '20º Track', '21º Track', '22º Track', '23º Track', '24º Track', '25º Track',
         '26º Track', '27º Track', '28º Track', '29º Track', '30º Track (Last Track)']
truth_tempo_tracks = [108] * 30  # TODO poner los tempos de los tracks
user_scores = [0] * 30
confidence_factor = 0.7
filepath = 'db.json'
#filepath = 'https://github.com/LeDanix/server_app/blob/main/db.json'
#filepath = 'db.json'
#headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
first_time = True


@st.cache
def give_a_score(truth_tempo, tempo_user, conf_fact, track_number1):
    score = 0
    percent = (1 - np.abs(truth_tempo - tempo_user) / truth_tempo)
    if percent < 0.7:
        session_state.user_scores[track_number1] = score
    else:
        a = np.log(11) / ((1 - conf_fact) * truth_tempo)
        score = -np.exp(a * np.abs(truth_tempo - tempo_user)) + 11
        session_state.user_scores[track_number1] = score


def control():
    if len(session_state.tempos) > 0:
        session_state.tempos.pop(0)  # TODO Advertir que no se ha realizado ninguna puntuacion
        if len(session_state.tempos) > 0:
            session_state.user_tempo_tracks[session_state.track_number] = \
                60.0 / (sum(session_state.tempos) / len(session_state.tempos))

            give_a_score(truth_tempo_tracks[session_state.track_number],
                         session_state.user_tempo_tracks[session_state.track_number],
                         confidence_factor, session_state.track_number)
            session_state.tempos = []

        else:
            st.write('You haven\'t saved any data here, your score on this track will be 0')


def show_result():
    st.title("Congratulations")
    aux_write = "**Your final score is {:.2f}**".format(session_state.final_score)
    st.write(aux_write)


def update_music():
    track_title = st.subheader(names[session_state.track_number])
    audio_file = open(track_path[session_state.track_number], 'rb')
    audio_bytes = audio_file.read()
    audio_bar = st.audio(audio_bytes, format='audio/mp3')


def add_new_use_to_json(new_user_info):
    #Esto funciona para archivos que tenga en el pc
    with open(filepath) as json_file: 
        data = json.load(json_file) 
        data = data['tempos']
        data.append(new_user_info)

    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4) 
        
    #json_file = urllib.request.urlopen(filepath) 
    #json_file = json_file.read()
    #if json_file == None or json_file == '':
    #    print('I got a null or empty string value for data in a file')
    #else:
    #    old_data = json.loads(json_file)
    #    print(old_data)
    #if type(old_data) is dict:
    #   new_data = [old_data]
    #new_data.append(new_user_info)
    #json.dump(old_data, json_file)
        


def get(**kwargs):
    """
    Gets a SessionState object for the current session.
    Creates a new object if necessary.
    Parameters
    ----------
    **kwargs : any
        Default values you want to add to the session state, if we're creating a
        new one.
    """
    # Hack to get the session object from Streamlit.

    ctx = ReportThread.get_report_ctx()

    this_session = None

    current_server = Server.get_current()
    if hasattr(current_server, '_session_infos'):
        # Streamlit < 0.56
        session_infos = Server.get_current()._session_infos.values()
    else:
        session_infos = Server.get_current()._session_info_by_id.values()

    for session_info in session_infos:
        s = session_info.session
        if (
                # Streamlit < 0.54.0
                (hasattr(s, '_main_dg') and s._main_dg == ctx.main_dg)
                or
                # Streamlit >= 0.54.0
                (not hasattr(s, '_main_dg') and s.enqueue == ctx.enqueue)
                or
                # Streamlit >= 0.65.2
                (not hasattr(s, '_main_dg') and s._uploaded_file_mgr == ctx.uploaded_file_mgr)
        ):
            this_session = s

    if this_session is None:
        raise RuntimeError(
            "Oh noes. Couldn't get your Streamlit Session object. "
            'Are you doing something fancy with threads?')

    # Got the session object! Now let's attach some state into it.

    if not hasattr(this_session, '_custom_session_state'):
        this_session._custom_session_state = SessionState(**kwargs)

    return this_session._custom_session_state


class SessionState(object):
    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)


session_state = get(prev_time=prev_time, track_number=track_number,
                    tempos=tempos, user_tempo_tracks=user_tempo_tracks, user_scores=user_scores,
                    final_score=final_score, first_time=first_time)
# session_state = get(prev_time=0, track_number=0, tempos=[], user_tempo_tracks=[0]*30,
#                       user_scores=user_scores)


st.title('BeatTracking Quest')
st.title('')
spanish_column, english_column = st.beta_columns(2)
spanish_column.write('**¿Cuanto ritmo tienes?**')
english_column.write('**How many rhythm do you have?**')
spanish_column.write('Hola, Soy Daniel Saiz Azor. Soy un estudiante de Ingenieria Electronica y Automatica '
                     'que esta realizando su TFG sobre algoritmos de Beat-Tracking. '
                     'El BeatTracking es, como su nombre indica, la obtencion en el tiempo '
                     'de los pulsos musicales que contiene una pista de audio. '
                     'Mi objetivo es comparar distintos algoritmos de BeatTracking, y ver '
                     'cual de ellos es mas eficaz en diferentes disciplinas. La que nos acontece '
                     'es la comparativa entre estos algoritmos y la capacidad musical '
                     'de los seres humanos y, es por ello, que necesito vuestra ayuda para poder demostrar '
                     ' de lo que somos capaces. '
                     'He desarrollado esta pequeña web, donde deberas marcar el '
                     'pulso de las canciones y conseguir la mejor puntuacion.')

english_column.write('Hi, I\'m Daniel Saiz Azor. I\'m a student of Electronic and Automatic Engineering '
                     'who is doing his TFG on Beat-Tracking algorithms. The BeatTracking is, as its '
                     ' name suggests, the obtaining in time of the musical beats that an audio track '
                     ' contains. My goal is to compare different BeatTracking algorithms, and see '
                     'which of them is more effective in different disciplines. What happens to us is '
                     ' the comparison between these algorithms and the muscial capacity of human beings, '
                     ' that is why I need your help to be able to demonstrate what we are capable of. '
                     'To do this, I have developed this small website, where you should mark the pulse of '
                     'the songs and get the best score.')
st.title('')
st.title('')

musical_exp = st.selectbox(
    'Select the option that best suits you',
    questions)

st.title('')
st.title('')

spanish_column1, english_column1 = st.beta_columns(2)
english_column1.title('Instructions')
spanish_column1.title('Instrucciones')

spanish_column1.write('A lo largo de la web, te vas a encontrar con 30 pistas musicales '
                      'de 30 segundos cada una.')
spanish_column1.write('Lo que debes hacer es clicar en el boton de inicio de la cancion para empezar a oirla, y '
                      'en cuanto comiences a visualizar el pulso de la cancion, deberas clicar en el boton "BEAT" '
                      'que hay debajo del reproductor, al ritmo de la musica.')
spanish_column1.write(
    '**No pares hasta que acabe la musica ni vuelvas hacia atras en la cancion, porfavor. Si lo haces, la prueba '
    'no sera valida y tu puntuacion disminuira**')
spanish_column1.write(
    'Si te ocurre lo anterior, siempre puedes repetir dicha cancion con el boton "REPEAT". Esto borrara '
    ' tu puntuación de dicha cancion. **Deberas ponerla desde el principio y cliclar play de nuevo** ')
spanish_column1.write('Usa los botones "NEXT" y "PREVIOUS" para moverte entre canciones')
spanish_column1.write('La puntuacion se mostrara automaticamente una vez pases de la ultima cancion y no habra '
                      'vuelta atras.')
english_column1.write('Throughout the web, you will find 30 music tracks of 30 seconds each.')
english_column1.write('What you should do is click on the start button of the song to start listening to it, and as '
                      'soon as you begin to visualize the beat of the song, you must click on the "BEAT" button that '
                      'is under the player, to the rhythm of the music.')
english_column1.write(
    '**Don\'t stop until the music ends or turn back on the track, please. If you do, the test will be valid and your '
    'score will decrease**')
english_column1.write('If the above happens to you, you can always repeat that song with the "REPEAT" button, this '
                      'will erase your score for that song. ** You should put it from the beginning and click '
                      'play again **')
english_column1.write('Use the "NEXT" and "PREVIOUS" buttons to move between songs')
english_column1.write('The score will be displayed automatically once you pass the last song and there will be no '
                      ' going back.')

spanish_column2, english_column2 = st.beta_columns(2)
spanish_column2.title('Permisos')
english_column2.title('Permits')

spanish_column2.write('Al entrar a esta aplicacion web, usted esta permitiendo que tanto el administrador de la web '
                      'Daniel Saiz, como la Universidad a la que pertenece, registren los datos '
                      'de su experiencia musical y su capacidad de induccion de pulso musical. Ningun otro dato personal sera'
                      ' recogido')
english_column2.write('By entering this web application, you are allowing both the web administrator Daniel Saiz, '
                      'and the University to which he belongs, to record the data of his musical experience and his '
                      'capacity to induce musical pulse. No other personal data will be collected')

st.title('')
st.title('')

st.title('The game')
st.title('')
st.title('')

left_column2, right_column2 = st.beta_columns(2)
pressed3 = right_column2.button('NEXT  ➡')
pressed4 = left_column2.button('⬅  PREVIOUS')

# Cabe la posibilidad de que en algun momento, algun participante deje alguna cancion
# sin rellenar, o saque un resultado muy malo porque ha hecho mal el proceso. Esos
# habra que eliminarlos de la estadistica en MatLab


if pressed3:
    if session_state.track_number >= len(track_path) - 1:  # TODO acordarse de cambiar esto
        control()
        session_state.final_score = sum(session_state.user_scores) / float(
            len(session_state.user_scores))  # Suma puntuaciones
        show_result()
        if session_state.first_time:
            session_state.first_time = False
            #json_data = {'tempos': [{'musical_exp': musical_exp, 'tempos_data': session_state.user_tempo_tracks}]}
            #json.dump(json_data, open(filepath, 'a'), indent=4, sort_key=True)
            json_data = {'musical_exp': musical_exp, 'tempos_data': session_state.user_tempo_tracks}
            #requests.post(filepath, data=json.dumps(json_data), headers=headers)
            add_new_use_to_json(json_data)
        if session_state.track_number == len(track_path) - 1:
            session_state.track_number += 1
    else:
        control()
        session_state.track_number += 1
        session_state.prev_time = 0

if pressed4:
    if session_state.track_number != 0 and session_state.track_number < len(track_path):
        control()
        session_state.track_number -= 1


    elif session_state.track_number == 0:
        error = st.write('There is no a previous one')

    elif session_state.track_number >= len(track_path):
        show_result()

if session_state.track_number < len(track_path):
    update_music()

st.write('')
st.write('')
left_column, right_column = st.beta_columns(2)
pressed1 = left_column.button('BEAT   🔽')
pressed2 = right_column.button('REPEAT   🔄')

if pressed1 and session_state.track_number < len(track_path):
    act_time = time.time()
    aux_tempo = act_time - session_state.prev_time  # TODO Arreglar esto, no cambia el prev_time
    session_state.tempos.append(aux_tempo)
    session_state.prev_time = act_time

if pressed2 and session_state.track_number < len(track_path):
    session_state.tempos = []

print('')
print("track_number: {}".format(session_state.track_number))
print(session_state.tempos)
print(session_state.user_tempo_tracks)
print(session_state.user_scores)
print('')
