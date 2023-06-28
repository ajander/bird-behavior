import streamlit as st
import altair as alt
import requests
import json 
import time
import pandas as pd
import random
from collections import deque
from datetime import datetime
import os

#%% Select data source ###

with st.form(key='data_source_form'):

    poc = st.radio(
        label="Data Source",
        options=['Random walk', 'Arduino device'],
        index=0,
        help='Random walk allows the app to run even if the Arduino device is unavailable')
    submit_button = st.form_submit_button(label='Submit')

if submit_button:
    
    st.title("Weather App")

    #%% Display live data ###

    if poc:

        st.subheader("Experimenting with Displaying Live Data")

    else:
    
        st.subheader("Exploring Arduino IoT Cloud Endpoints")

        # Set up for Arduino device data
        import iot_api_client as iot
        from oauthlib.oauth2 import BackendApplicationClient
        from requests_oauthlib import OAuth2Session

        CLIENT_ID = os.getenv("CLIENT_ID")
        CLIENT_SECRET = os.getenv("CLIENT_SECRET")
        THING_ID = 'e12224f1-8238-4060-bcbf-7c3d5f672576'  # Pixel 6a
        PROPERTY_ID = 'a304b73f-b234-4683-a4c6-612e11cc771a'  # Linear accelerometer

        oauth_client = BackendApplicationClient(client_id=CLIENT_ID)
        token_url = "https://api2.arduino.cc/iot/v1/clients/token"
        oauth = OAuth2Session(client=oauth_client)

        token = oauth.fetch_token(
            token_url=token_url,
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            include_client_id=True,
            audience="https://api2.arduino.cc/iot",
        )

        client_config = iot.Configuration(host="https://api2.arduino.cc/iot")
        client_config.access_token = token.get("access_token")
        client = iot.ApiClient(client_config)

        # Read values from a property of a device
        properties = iot.PropertiesV2Api(client)

    #%% Set up session state variables to hold the data ###
    
    # Delete all the items in session state
    for key in st.session_state.keys():
        del st.session_state[key]
    
    if 'my_values' not in st.session_state:
        st.session_state.my_values = deque(maxlen=30)
        st.session_state.my_labels = deque(maxlen=30)

    if not st.session_state.my_values:
        now = round(time.time() % 1000)
        st.session_state.my_values.append(0)
        st.session_state.my_labels.append(now)

    placeholder = st.empty()


    #%% Weather API ###

    st.subheader("Exploring RapidAPI's Weather Endpoints")

    url = "https://weatherapi-com.p.rapidapi.com/current.json"

    headers = {
        "X-RapidAPI-Key": os.getenv("WEATHER_API_KEY"),
        "X-RapidAPI-Host": "weatherapi-com.p.rapidapi.com"
    }

    location = st.text_input("Enter the location", "Kansas City")
    querystring = {"q":{location}}

    response = requests.get(url, headers=headers, params=querystring)

    if(response.status_code == 400):

        st.error("No location found matching parameter 'q', try searching for a different location.")

    else:

        result = response.text
        weather_data = json.loads(result)

        col1, col2 = st.columns(2)

        with col1:

            st.write(f'Name: {weather_data["location"]["name"]}')
            st.write(f'Region: {weather_data["location"]["region"]}')
            st.write(f'Country: {weather_data["location"]["country"]}')
            st.write(f'Local Time: {weather_data["location"]["localtime"]}')
            st.metric(label="wind_kph", value= f'{weather_data["current"]["wind_kph"]}')
            st.write(f'Feels like: {weather_data["current"]["feelslike_c"]} ℃')

        with col2: 

            st.write(f'Temp in Celcius: {weather_data["current"]["temp_c"]}')
            st.write(f'Temp in Farenheit: {weather_data["current"]["temp_f"]}')
            st.write(f'Condition: {weather_data["current"]["condition"]["text"]}')
            st.image(f'http:{weather_data["current"]["condition"]["icon"]}')
            st.metric(label = "Humidity", value = f'{weather_data["current"]["humidity"]}')

        st.info('⛅ Current weather or realtime weather API method allows a user to get up-to-date current weather information in json and xml. The data is returned as a Current Object.')

        weatherapi_image_link = 'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wCEAAkGBxMQEhUSExISFRUXERUVFxMVFxUXFRgVFxYWFhgWFxoYHSggGBolHxgWITEhJSkrLi4uFx8zODMtNygtLisBCgoKDg0OGxAQGjIlICUtLS8tKystLS8tMi0rLS0tKzAtLS0wLS0tLTIvLS0tLS0tLy0tLS0uLS0tLS0tLS0tLf/AABEIAJkBSQMBIgACEQEDEQH/xAAcAAEAAgIDAQAAAAAAAAAAAAAABgcDBQIECAH/xABMEAABAwIDAwYKBggCCgMAAAABAAIDBBEFEiEGBzETIkFRYZEUMjRxcnOBobGyNVN0ksHRFjNCUmKis9IVgiVDVGOTo8LD4fAkRIP/xAAaAQEAAgMBAAAAAAAAAAAAAAAAAwQBAgUG/8QANBEAAgECAwUFBwQDAQAAAAAAAAECAxEEITESE0FRcQVhgbHwFDORocHR4TI0UvFCkrIi/9oADAMBAAIRAxEAPwC8UREAREQBabaDEeSbkaee73Dr9vDvWxrKkRML3cAO89AUGqKgyPL3cTr+QXN7Rxe6W7i//T+S/OiMS0JJs/inKDk3nnDxT1jq84W9VeRPLSCDYg3B7VNcKrxMy/7Q0cO3r8xWvZ+L3i3c3mtO9fdeQid5ERdQyEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBEWqx2v5GOwPPdoOwdJUdWrGlBzlovX9d4NLtJiHKPyNPNYe89J9nDvWnC+r4F4qpXlVrOpPV+reH51bMM5tXbw+rMLw8eYjr7F1WrkplNxneLzRhaE9ilD2hzTcEXCyKL7PV+Q8m480nTsP5FSherwuIVempLXj1NgiIrACIiAIiIAiIgCIiAIiIAiIgCIiAIiIAi4k21K4tmadA5pPUCEBkRFUe+jFZ4J6cQzSxgwvJDHuaCQ4amx1QFuIobupq5JsOY+V75HGSUFz3FzrCQgalTJAEREAREQBERAEREAREQGN7w0Ek2ABJPUBxKg2J1pmkL+jg0dQHD8/at3tTXWAhadXau83QPafh2qMrzfbGK2pqjHRZvry8F8zDOV18QBfbLiNoHIBclxidZZSFsqtnmbKORxaVLMFr+Vblcee0a9o4A/morlWBte6GZr2nVuhHWOkFdHBY1Up7XDiu7n4GkrxLGRYKWpbIxr2m4cLj/wB61nXq001dGwREWQEVVb2Mer6GoiNPUujhki0aGQuAkY45tXsJ1DmdPWpPuyx59dQtfK/PKyR8cjrNBJBzNJDQAOa5vAICXItVtFjkVBCZ5s2QOa3mi7iXGwsP/eC0mCbxaKsnZTxmUSPLg3OywOVpedb6aNKAmCIqH2r3hV3hk7aapcyJspjYwRwuvk5hILmEnM4E8ekIC+EXRwiORkEQmfnlETOUeQ0Zn5RmNmgAa34Kp9rt68pkdHQ5GxNJHLludzz+8wHmtb1XBJ0OiAuZF52bvKxMHyq/YY4be5isTd5vENc/wapaxk9iWOZcMkA1IsScrwNeNjrwtZAWKixzGzSR0A/BeeTvKxP/AGr/AJcP9iA9FIvPEO83E2m/hDXdjo4rfytB96tHd3tuMTa6ORrWTxgFwbfI9p0ztB1GuhFza411QG623+j6v7LL8hVNbnR/pOP1UvyqW758dqKcxQRSZY5oZhI3K05hdg4kXGhPC3FVVhGKzUkomgfkkAIDrNdoRY6OBCA9UqmN+/lFN6mT52rabqNrKuuqZY6iblGtgzAZI22dnaL81o6CtXv38opvUyfO1ATDc59GR+tm/qOU3XmnCNta2kibBBMI42lxAyRuN3HMblzT0rcYZvTxCJwMj45231Y9jW6djmAWPab+ZAX8i1OzeNxV9OyoivldoWnxmuHjMd2j8j0rT7fbZswyNoDQ+eQHk4yeaAOL321yjq6ezUgCXIvPE+83E3G/hDWfwtjjyjzZgT71scD3r1kTx4RknjvzhlayQDraW2F+wjXs4oC9kXUw6uZURMmidmY9oc09h+B7FT23G8KuirZoYJGxRxPyABjHE2Au5xeD034W0sgLsRedDvKxP/a/+XD/AGKYfphWfX/yR/2oC21iqJhG0vdwaCSsqjm1VbwiHnd+A/HuVbGYhYejKpy06vT1yBG6qZ0j3SO4uN/yHcuAcOlcisbgvE7bm7vU1eRk5XsXwyLGvoKzsobTMmZZg4rAxHyKOSbdjeLtmZJZrcO9apxvquzUO0t1rrqxRgoor1pNuxI9jsTyP5Fx5rzdvY7q9vxHapsqlBtqDY9BHG6sfAsR8IhD9Mw5rx/EPwPH2r0fZeJ2oulLhp05eHl0M0pcDZoiLrkxAt8uF8tQcqBd0EjX6ccjjkf7OcD/AJVFdxmJ5Z56YnR8YlaP4mHK7vDh91W3ilE2ohlhd4skb2HzOaRf3rzrshWOocRhc/QsqOSk7A4mF9/Ncn2ICwN+1faOmpwfGkdKR2MbkF/vnuVZbNV3g9XTzfuTxk+jmAd/KSpDvexDlsSkYNRDGyIdptyht7X29i6G3uA+Azxx2sHUkDjb98MyPI87mk/5kBfW1eKiko56jpZES3teeawfeIVDbucL8KxGBh1axxmffXSPna+d2Qe1SvePtHy2GUEYdzp2Mlkt1RsAIP8AnP8AIu7uLwmzJ6sjVxELD/C3nP7yWfdQE/2xmMdBVvabFtJMQe0RuVEbt8MiqcQhilaHss9xYeBysJAPWL20V57dfRtb9jn/AKbl5xwyKZ8gbTiUyWNhDm5S1tbZNeCA9JVezFHKxzHUsFnAg2jY0jtBAuD2heetlXmOvpcpNxWQtv2GVrT3gke1d3/DMX+rxPuqVz2c2brW1lM51HVNa2qgc5zoZAABK0kkkaADW6A9GkLVyYJRt1dT0w7THGPiFw2rxfwKkmqLAljLtB4F5IawHsLiF52mkq8Tn15Woldc5Rc2HYODGj2BAXPt5g1C6gqHNipg9kTnscwMa8OaLixbr7OlVzufkIxOMD9qKVp82XN8WhaWr2KroWOlko3sYxpc5x5OwA4nR11t90P0pF6uX+mUBbm39BFJQ1Ej4o3PZTSlj3NBc05SeaTqOA4dSp7dXSRzYixkrGPaY5TleA5tw3TQq7Nt/o+r+yy/IVTW576Tj9VL8qAvKiwingJdDBFGSLEsY1pI42JA4Kp9+/lFN6mT52q51TG/fyim9TJ87UBu90Wz9M+hE8kMckj5ZAXPaHWDHFoaL8Bpf2rX76MEp4YYJooWRvM3JksaGhzSxztQOJBboe0qS7nPoyP1s39Ry1e/TySD7V/23oDBuIeeQqW30E7CB2llj8B3KK75Xk4kbnhTxAdg57rd5PepTuG/U1XrY/kKim+T6Td6iL4OQFkbv9mqQUFO808T3yQske97GucXPGY6kcBewHUFA98+Dw008DoY2x8rHJnDAGtJYWAGw0Bs7XzBRqjoMTdG0xR4gYy0FhjE+Qttply6Wt1L5UYBiUluUpq99uGeOZ1r8bZgbIC3dzMhOGtB4NnlA8xdm+Liqi2/+kav7Q78FcW6ShlgoMk0ckbuXkOWRpa6xy2NjrZU7t/9I1f2h34ID0BS7P0mRv8A8Wn8Rv8AqmdQ7F2/8Kg+oh+438lnpfEb6DfgFmQGOWQMBcdAAST2DVQCqq+Ve554uN/N1BSXayryRCMcXn3NsT+AUQC8121V25xpJ5LN9Xp8F5mHKxkuvjlxC+SnQri7Jq2cbjrXKyzYVhj6l1m6AeM88B+Z7FK6XZmBg5wc89ZJHcG2XQw/Z9autqOS5v6WuaxuyHgr4ptLs9TkaMLe0Od+Jso9jOCOgBe052dfS3z9natsR2ZXox2smu6/k0jZqxoZnXK4L45wHErC+pHRqq8FfJFWUlfMzLb7K4mIZw0nmyWaex37J7zb2qOulJXBWqN6c1Naoj3tndF0ItVs7iHhFOx5POHNf6TdD36H2rar1MZKUVJaM6CaaugvPG9XDPB8SlI0bKGzN/zDK7+Zrj7V6HVZ76cCfPFBPFG+R7HmNzY2ue7I8XBs0E2BaPvLYyVns7G6vxKASHM6Wpa956w08o/+VpVg79qHmU1Rbg98JPpNzi/3Hd61O57AJm1zppoJoxHC7KZI3sGd5DdMwFzlz8OtWBvPw11Th0zWNc97ckjWtBc4ljgSABqTlzaBAefJ6p72sa4kiNhYwdTS9zyO9xXpLYjCvBKGnhIs4RBzx/vH89/n1cR7FSGx+y1RNWwMlpqhkfKhz3PikY3KznkEuaBrbL7V6NQGj23YXYdWAC5NHOAP/wA3Kk91dQ1mJwFzg0ESNBOgzOYQB5ydF6EkjDgWuFwQQQeBB0IVA7W7uqqjkcYIpJ4LksdGC97R0Ne0c4kfvAWPYgL9mlaxpc4hrWgkuJsABqST0BVphW9sVE8UIoyOVmZGHcre2d4bmtk6L3VYOwqvfzTT1zgdLGKoIPsLVYu7Ld/LFK2sq25Cy5ihNi7MRbO+3CwOg431NragSXe/f/CpvTgv5uWj/Gygm46RorJQSAXUxyg8TZ7SbexW/j2FtrKeWneSGyMLbji09Dh2g2PsXn3F9i6+jkINPM8A82WBr5GkdDgWAlvmNkBeu3n0dV/ZpPlKprdD9KRerl/plaN2G15FjBXkHiDFUEHz6KT7qsLqI8SidJT1DGhkt3PikY0XYQLlzQEBbm24vh9X9ll+Qql90kzW4nFmIGZkrRfpcWEgefQq/wCeFr2uY4Xa5paR1gixC8+7U7AVdFKeSilmhzXjkia57gOgPDbua4ddrfBAeh1TG/fyim9TJ87VJ9zcMzKSUTsma7wkkCZr2uy8nHqM+tr3960G+zD5pp6YxQzSAQyAmON7wDmboS0GyAlG5z6Mj9bN/UctXv08kg+1f9t62+6WnfFhsbZGPjdys3Ne1zHayOto4ArXb6qOSWlhEUUkhFTciNjnkDk36kNBsO1AdHcN+pqvWx/IVFN8o/0m71EX/UpluTopYYqkSxSxkyssJGPYSMp1GYC67u8/Yl2INbPBbwiNuXKSAJI7lwbc6BwJJF9OcboDd7u52vw2kyuBy07GG3Q5gDXNPaCFrduNv2YZLHEIuWc5hc4B4aWC4DbjKeOvcqXdgdfCSzwatab6hsU1j23aLO84XewXYivrZLchLGCedNO1zAB18+zn+YX9iAvLY3aD/EaYVHJcnd72hubN4pte9h03VC7f/SNX9od+C9DbP4Syip46aPxY22ueJJJc5x7S4k+1UPtxg9S/EKpzKWpc0zuIc2GVzSNNQQ2xHmQHoSl8RvoN+AWZYqYcxvoj4LKgILtVU56gjoYAPbxPx9y1IK51sueR7utxPfdYgvGYmW8qyk+Lfw4fIgvmZguMjS6zRxLgAO06BdrDcOkqDZg0HFx0A/8APYtzBs5JHJG/MHBrwSNQdCDcX42Shg61W0oxezfX7cXbu6G9rokGG0bYI2xt6Bqet3SV20ReyjFRWzHREgXCRoIIIuCLEdi5osg6NPhUMYs2JvnIzHvNyuriOz1POCDGGu6HsAa4d2h9q3CLR04OOzZW5WNXGLVrFR4vhr6aQxv16Wu6HN6CPyXTCne8GnBhjk6WyZb9jhr72hQQLg4mjuqjitOBzasNiViW7v6zLI+InRzQ4ek3j3g/yqdqqtm58lVCR0vy+x/N/FWqun2fK9K3J/nzbLmGleFuQREV4sBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAXwr6qtxiSXwh+cuz8obcbgX5tuy1rWVXF4pYeKk1e76fcjqVNhXLSRdTDi/kmZ/HyNzX43trftXbVlO6uSFXTtyucOo27iQvgXY2hZydTK3rNx5nc78Vqp6kjQcV46pRkqjj3v5ZFSU1HUsfZZrRTNt0lxPnuR8AFuFWGzm0TqUkOBfG43IHjA8Mzb8dLadgUxi2tpHD9aR2Fkl/c2y9HhcRSjRjGUkrJLPLTqS068JLWxvkWl/Smk+u/kk/tXz9K6X6w/cf+Sse1Uf5x/wBl9zfeR5m7RaP9K6X6x33H/kvn6V0v1jvuP/JPaaP818UN5Dmb1FoP0upf3n/cd+S+O2upgL5nHsDTf32Cx7VQ/mvihvIczhtyR4OB1yN+BVfujBW1x3GHVTwSMrW3ys6r8SesrWLh4usqtVyjpp8CnVkpyujtYHEfCYfWMPc4E/BWuq62Op89U09DGuJ7so+KsVdPsxPdNvi/oifDRtFhERdEsBERAEREAREQBERAEREAREQBERAF1a6ujhaHSODQTa5vxsTbTzFdpaXajDn1ETWR5biQO5xsLAOH4hR1ZSjBuKu+CNZNpNoyfpJS/XN7nfks9Ji0MpsyVpPVex7ioaNj6j/d/eK1uJYXLTOAkAFxdpabg2427RoudLGYmmtqdPLxIHVmtYlprVz47TxuLHygOBsRZ2h7lj2XrjPTtc43cCWk9drWJ7bEKD7TeVTen+AU+JxexSjUgtefS5vUq7MVJE6/SSl+ub3O/JdukxCKb9XI13YDr7RxUJZshUEAgx6gHxj0/wCVayoglpJbHmvbYgg9HWOsKvLG16dnUp5eu9mm9ms5RLUWqqMbpmPLXyNDmmxuDcHz2Xawur5aFkn7zQSO3gffdVxtD5TN6wqzjMU6NJThnfn0uSVajik0WgDcXC5LHB4rfRHwWRXSUh+3lD4k4HDmu+LT8R7QoO43Vv11K2aN0bxzXCx/Mdo4qqMRonU8jon8Wnj0EdDh2FcXH0NmpvFx8/z9yjiotO/BnUIWSDivhSLiqL0ZVWpnC+EoSihSJWwvoXErE+paOm/mWyTehhtLUzr6ui+u6h3rrvnceJPs0UiozepG6sVobN8rRxIXXfWjoBPuXRWxwHCXVczYhcN4vd+6zpPn6B2qaOHTdtWa7yUnaKJ3u+pCIXTOFjI6zfQb0+037gpasUMTWNDGgBrQAAOAA0AWVd6lTVOCguB14R2YpBERSG4REQBERAEREAREQBERAEREAREQBdPEa+OnZnkNhwA4knqA613FBdv5SZY2dAjcbdpNj8Aq+KrOlTc0aVJ7MbnaftuL82A2/icAfcCtNtBjfheTmZMmb9q982XsFvF962WAbMxzQtle513E2DSAAASOkanRdTanB46Xk8hcc+e+Yg+Lktaw7SuVX9qlRc6jWy7cuatouditLeON3ob/AGE8nd653ytUS2m8qm9MfKFLNhPJ3eud8rVE9pvKpvTHyhbYr9nT8PJip7qJZVJ4jPQHwChO3X69vqh8zlNqTxGegPgFCduv17fVD5nK72h7h+Hmiat+gkuyXkkXmd87lBNofKZvWFTvZLySLzO+dygm0PlM3rCqWN/Z0+i/4I63u4+uBZ0Hit9EfBZFjg8Vvoj4LIu2WgtJtHgbatmlhI0HI7/pPYfct2i1nCM4uMtDEoqSsylqt3IvMclmPabFp4j/AMdqxNqmXHPb3q09otm4K5tpBZ4HNkb47fzHYVVuO7IVNGSSzlIx/rYxcW/ibxb8O1cqpgNnRuxza1GVPNZo+vr2dBv7visL6xx4WHvXQADgsb4SOGqgjRp/2VXUkzuueTxJK4roh56ysglPWpNgjO0i6wmKlOA7IVNTZz28jH+88c4j+FvHvt7UjTlLJI2hCU3aKuajDqCSokEcTczj3Adbj0BW1s9gjKOLI3VxsXv6XO/ADoCy4PhEVIzJG21/GcdXOPW4/hwC2S6NDDqnm9Tq4fDKnm9fWgREVktBERAEREAREQBERAEREAREQBERAEREAUG2/iIljf0FhbftBvb3qcrq11EydhZI27T3g9YPQVXxNF1abgvVjSpDbjYiGA7UMhiET2POUmxbbUEk63I611Np8aZV8nka5uTPfNb9rLa1if3StzJsTHfmyOA6i1p9+i4/oS36533R+a5s6OMdPdNK2XLha3kQONVx2eB2dhPJ3eud8rVEtpvKpvT/AACn+CYWKaMsDi67i65FuIAt7lAdpvKpvTHwCzjIuGFpxlwt5MxVVqaTJDQ7YsbG1r2OzBoBLbEGwtfUiyj+OYl4TLymXKMoa0cTYXOvbclSBmxbHAOEzhdoNi0HiFscN2XhhcHnM9w1BdwB6wB0+e6zOhi60VCbVueRs4VZK0ju4DTGKnjY7iGkkdRcS63vVfbQ+UzesKtJRiv2RbNI+QyuGck2yjS/tU+Ow0p0VCmtPtY2q024pR4Ejg8Vvoj4LIuEbbADqAC5rok4REQBERAafENmqWe5fC3Mf2m3Y6/WS21/atJUbvID4kkjew5XD4A+9TNFHKjCWqIpUacs3FFfv3aMP/2D/wAMf3LtU27enb48kr+y4aPcL+9TZFhUKa4Gqw1Jf4mqwzZ+mptYoGNcP2zzn/edc+9bVEUiSWhMoqKslYIiLJkIiIAiIgCIiAIiIAiIgCIiAIiIAiIgCIiAIiIAiIgCq/abyqb0x8oVoKr9p/KpvTHyhcztX3S6/RlbE/pRZVJ4jPQHwCzLDSeIz0R8Asy6SLIREWQEREB//9k='
        st.image(weatherapi_image_link)

    #%% footer ###

    footer = '''
        <style>
        a:link , a:visited{
            color: blue;
            background-color: transparent;
            text-decoration: underline;
        }

        a:hover,  a:active {
            color: red;
            background-color: transparent;
            text-decoration: underline;
        }

        .footer {
            position: fixed;
            left: 0;
            bottom: 0;
            width: 100%;
            background-color: white;
            color: black;
            text-align: center;
        }
        </style>

        <div class="footer">
            <p>This version of the weather API code copied from <a href="https://dev.to/dotaadarsh/lets-create-a-simple-weather-app-part-1-5147" target="_blank">Aadarsh Kannan</a></p>
        </div>
        '''

    st.markdown(footer, unsafe_allow_html=True)

    #%% Update live data

    while True:
        # It is important to exit the context of the placeholder in each step of the loop
        with placeholder.container():

            if poc:
                
                # Generate new value at random, for POC
                new_value = st.session_state.my_values[-1] + random.randrange(-100, 100) / 100
                st.session_state.my_values.append(new_value)

            else:
                
                # Get new value from Arduino IoT API
                try:
                    resp = properties.properties_v2_show(THING_ID, PROPERTY_ID)
                    st.session_state.my_values.append(resp.last_value)
                except Exception as e:
                    print("Exception when calling PropertiesV2Api->propertiesV2Show: %s\n" % e)
                    st.session_state.my_values.append(0)

            now = round(time.time() % 1000)
            st.session_state.my_labels.append(now)
            
            device_data = pd.DataFrame({
                'Time': list(st.session_state.my_labels), 
                'Value': list(st.session_state.my_values),
            })
            chart = alt.Chart(device_data).mark_line().encode(
                x = alt.X('Time', scale=alt.Scale(domain=[device_data['Time'].min(), device_data['Time'].max()])),
                y = alt.Y('Value'),
            )

            st.altair_chart(chart, theme="streamlit", use_container_width=True)

            time.sleep(1)

