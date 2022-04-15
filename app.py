from mijnproject import app, db
from flask import render_template, redirect, request, url_for, flash, send_from_directory
from flask_login import login_user, login_required, logout_user, current_user
from mijnproject.models import User, Bungalow, Boeking
from mijnproject.forms import LoginForm, RegistrationForm, annuleerForm, reserveer_form, aanpassen_form
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

def date_between(start, d, end) -> bool:
    """Kijkt of d tussen start en end zit"""
    if start <= d <= end:
        return True
    else:
        return False


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/aanbod')
@login_required
def aanbod():
    return render_template("aanbod.html")

@app.route("/bungalows/<bungalow_id>")
def bungalows(bungalow_id:str):
    try:
        int(bungalow_id)
    except ValueError:
        return redirect(url_for("bungalows_page"))
    
    
    if int(bungalow_id) > 3:
        return redirect(url_for("bungalows_page"))
    
    return render_template(f"bungalow_{bungalow_id}.html")

@app.route('/boek', methods=['GET', 'POST'])
@login_required
def boek():
    form = reserveer_form()

    bungalow_id = request.args.get("id") # de id van de bungalow die gekozen is
    
    if bungalow_id == "" or bungalow_id == None: # als er geen id is
        return render_template("boek.html", id_wrong="Dit is geen geldige id", bungalow_name="is ongeldig") 

    try: 
        int(bungalow_id) 
    except ValueError: # als het geen int-type is
        return render_template("boek.html", id_wrong="Dit is geen geldige id", bungalow_name="is ongeldig")
    
    
    bungalow_id = int(bungalow_id) 

    if bungalow_id not in [1, 2, 3]:
        return render_template("boek.html", id_wrong="Dit is geen geldige id", bungalow_name="is ongeldig")

    bungalow_namen = {1: "De Kokkel", 2: "De Pieterman", 3: "De Zeemeeuw"} 
    bungalow_name = bungalow_namen[bungalow_id]


    
    date_now = datetime.now().date()
    if form.validate_on_submit():
        datum = form.week.data # de datum uit de form
        groote = bungalow_id # gewenste bungalow
        print("Groote:", groote)   
        # eerdere datums kunnen niet gekozen worden
        if datum < date_now:
            return render_template("boek.html", form=form, w_or_g="Geef een geldige datum alstublieft!")            
        else:
            # een simple dictionary om de groote in mensen om te zetten in id's
            
            
            # De dag dat de gebruiker weer uit de bungalow moet
            end_date = (datum + timedelta(days=6)).strftime("%d-%m-%Y")
            
            

            # alle gehuurde bungalows met het bungalow_id die de gebruiker ook heeft
            alle_gehuurde_bungalows = Boeking.query.filter_by(bungalow_id=bungalow_id).all()
            
            # alle gehuurde datums uit de database
            alle_gehuurde_datums = [gehuurde_bungalow.dagen for gehuurde_bungalow in alle_gehuurde_bungalows]
        

            bungalow_voorraad = {1: 60, 2: 40, 3: 20} # voor bungalow-id 1 zijn er 60 huisjes beschikbaar, voor bungalow-id 2 zijn er 40 huisjes beschikbaar, voor bungalow-id 3 zijn er 20 huisjes beschikbaar
            
            n_gehuurde_datums = 0
            for gehuurde_datum in alle_gehuurde_datums:
                """"""
                print(n_gehuurde_datums)

                if n_gehuurde_datums >= bungalow_voorraad[groote]:
                    return render_template("boek.html", form=form, w_or_g="Sorry, deze bungalow zit vol voor deze periode!")

                datums = gehuurde_datum.split(" | ") # begin- en einddatum in een lijst ...
                start, end = datetime.strptime(datums[0], "%d-%m-%Y").date(), datetime.strptime(datums[1], "%d-%m-%Y").date() # ... en als variabelen

                if date_between(start, datum, end):
                    n_gehuurde_datums += 1
            
                    


            # de id van de gebruiker op dit moment
            user_id = current_user.username
            
            d_list=[]

            start_datum = datum
            for day in range(6): # alle datums die de klant wil gebruiker - de einddatum want er mag wel een nieuwe bungalow op de einddatum geboekt worden.
                d_list += [start_datum+timedelta(days=day)]
            


            user_gehuurde_bungalows_byDate = Boeking.query.filter_by(user_id=user_id, bungalow_id=bungalow_id).all()

            for boeking_data in user_gehuurde_bungalows_byDate:
                week = boeking_data.dagen # de week van elke boeking
                start_datum = datetime.strptime(week.split(" | ")[0], "%d-%m-%Y").date() # de startdatum van elke boeking
                
                dagen_fromWeek = [start_datum+timedelta(days=day) for day in range(6)] # alle dagen van de week van elke boeking van de gebruiker zonder de einddatum want op de eindatum mag er wel een nieuwe bungalow geboekt worden 
                print(dagen_fromWeek, "\n\n\n")  # dagen die ook al geboekt zijn door de gebruiker

                for dag in dagen_fromWeek:
                    print(dag)
                    if dag in d_list:
                        return render_template("boek.html", form=form, w_or_g="U hebt deze bungalow al geboekt voor een dag in deze periode!", bungalow_name=bungalow_name, bungalow_id=bungalow_id)

            
            # de bungalow die de gebruiker wenst
            bungalow = Bungalow.query.filter_by(id=bungalow_id).first()
            
            # de gewenste datums: [begin-datum | eind-datum]
            gewenste_datums = str(datum.strftime("%d-%m-%Y")) + " | " + str(end_date)

            # zet het in de database
            db.session.add(Boeking(user_id, bungalow.id, gewenste_datums))
            db.session.commit()

            # de naam van de bungalow, nodig om de vervolgpagina compleet te maken
            

            return render_template("succes.html", bungalow=bungalow_name, bungalow_id=bungalow_id, datum=gewenste_datums)
    return render_template("boek.html", form=form, bungalow_name=bungalow_name, bungalow_id=bungalow_id)

def user_boekingen() -> list:
        # de gebruiker die op dit moment is ingelogd
        user_id = current_user.username

        # de boekingen van de gebruiker die op dit moment is ingelogd
        bungalow_ids=[i.bungalow_id for i in Boeking.query.filter_by(user_id=user_id).all()]

        boekingen_ids=[i.id for i in Boeking.query.filter_by(user_id=user_id).all()]


        # bungalow ids voor de ids die de gebruiker heeft
        bungalow_boekingen = [Bungalow.query.filter_by(id=i).all() for i in bungalow_ids]

        bungalow_namen = [i[0].name for i in bungalow_boekingen]
        boeking_week = [i.dagen.replace(" | ", " tot en met ") for i in Boeking.query.filter_by(user_id=user_id).all()]


        boeking_lst = []
        for i in range(1, len(bungalow_namen)+1):
            base_str = f"U heeft bungalow-type '{bungalow_namen[i-1]}' geboekt voor {boeking_week[i-1]}"
            boeking_lst += [[base_str, boekingen_ids[i-1]]]

        return boeking_lst

@app.route("/uw-boekingen")
@login_required
def boekingen():
    return render_template("boekingen.html", boekingen=user_boekingen())

@app.route("/annuleren", methods=["GET", "POST"])
def annuleer():
    """"""
    form = annuleerForm()
    id_ = request.args["id"]

    # valideer of id een int is (kan zijn) 
    try:
        id_ = int(id_)
    except ValueError:
        return render_template("annuleren.html", form=form, w_or_g="Voer een geldige id in!")
    
    if form.validate_on_submit():
        print(id_)
        user_boeking = Boeking.query.filter_by(id=id_).first()
        print(user_boeking)

        db.session.delete(user_boeking)
        db.session.commit()

        return render_template("complete.html", info=f"Boeking {id_} is succesvol geannuleerd!")
    return render_template("annuleren.html", form=form)
    
@app.route("/boekingen/aanpassen", methods=["GET", "POST"])
@login_required
def aanpassen():
    id_ = request.args["id"]
    form = aanpassen_form()

    # valideer of id een int is (kan zijn) 
    try:
        id_ = int(id_)
    except ValueError:
        return render_template("aanpassen.html", w_or_g="Voer een geldige id in!")
    
    user_id = current_user.username # de gebruiker die is ingelogd
    # de boekingen van de gebruiker die op dit moment is ingelogd
    bungalow_ids=[i.id for i in Boeking.query.filter_by(user_id=user_id).all()]
    # als de gebruiker deze id niet in zijn bezitting heeft:
    if id_ not in bungalow_ids:
        return render_template("aanpassen.html", w_or_g="U hebt geen rechten om deze boeking aan te passen!")



    user_boeking = Boeking.query.filter_by(id=id_).first()

    user_boeking_date = user_boeking.dagen.split(" | ")
    


    datum_string = user_boeking_date[0] + " tot en met " + user_boeking_date[1] # dit is voor de website om te laten zien in welke boeking de gebruiker zich bevindt


    
    if form.validate_on_submit():
        print(form.nieuwe_week.data)
        start_datum = form.nieuwe_week.data
        # nieuwe datums: [begin-datum | eind-datum]

        eind_datum = (form.nieuwe_week.data + timedelta(days=6)).strftime("%d-%m-%Y")
        print(eind_datum)
        nieuwe_datums = str(form.nieuwe_week.data.strftime("%d-%m-%Y")) + " | " + (form.nieuwe_week.data + timedelta(days=6)).strftime("%d-%m-%Y")

        d_list=[]
        for day in range(6): # alle datums die de klant wil gebruiker - de einddatum want er mag wel een nieuwe bungalow op de einddatum geboekt worden.
            d_list += [start_datum+timedelta(days=day)]
        
        all_user_boekingen = Boeking.query.filter_by(user_id=user_id).all()
        print(all_user_boekingen)
        
        for boeking in all_user_boekingen:
            
            print("Boeking:", boeking.dagen)
            boeking_start_date = datetime.strptime(boeking.dagen.split(" | ")[0], "%d-%m-%Y").date()
            boeking_end_date = datetime.strptime(boeking.dagen.split(" | ")[1], "%d-%m-%Y").date()
            for day in d_list:
                if date_between(boeking_start_date, day, boeking_end_date): 
                    return render_template("aanpassen.html", wrong_date="U hebt al een andere boeking in deze periode! Kies een andere datum.", form=form, id=id_, datums=datum_string)

        Boeking.query.filter_by(id=id_).update(dict(dagen=nieuwe_datums))    
        db.session.commit()
        print("Aangepast")   
        return render_template("complete.html", info=f"Uw boeking met id {id_} is succesvol aangepast!", datums=f"Uw boeking is nu geboekt voor {boeking_start_date} tot en met {boeking_end_date}")



    return render_template("aanpassen.html", form=form, boeking_id=id_, datums=datum_string)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Je bent nu uitgelogd!')
    return redirect(url_for('home'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Grab the user from our User Models table
        user = User.query.filter_by(email=form.email.data).first()

        # Check that the user was supplied and the password is right
        # The verify_password method comes from the User object
        # https://stackoverflow.com/questions/2209755/python-operation-vs-is-not

        if user.check_password(form.password.data) and user is not None:
            # Log in the user

            login_user(user)
            flash('Logged in successfully.')

            # If a user was trying to visit a page that requires a login
            # flask saves that URL as 'next'.
            next = request.args.get('next')

            # So let's now check if that next exists, otherwise we'll go to
            # the welcome page.
            if next == None or not next[0] == '/':
                next = url_for('home')

            return redirect(next)
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)

        db.session.add(user)
        db.session.commit()
        flash('Dank voor de registratie. Er kan nu ingelogd worden! ')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)



if __name__ == '__main__':
    app.run(debug=True)
