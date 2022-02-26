from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import email_text.emails_x as emails_x
import smtplib
from email.message import EmailMessage

app = Flask(__name__)

#Connects to either our local postgres sql table or our Heroku pg table
ENV = 'DEV'

if ENV == 'DEV':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:@Jakc1324@localhost/heroku_email'
else:
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://zyzkwvmnmkixyu:53a3283cb5aa384f064f2486de811a2a9528ea854c4f3cb52558d6a82fde2dfc@ec2-54-236-156-167.compute-1.amazonaws.com:5432/d2hbi00jt18m86'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

#initializes the data model with the schema we need
class email_table(db.Model):
    __tablename__ = 'emails'
    id = db.Column(db.Integer, primary_key=True)
    customer = db.Column(db.String(200))
    email = db.Column(db.String(200))
    email_xyz_num = db.Column(db.Integer)

    def __init__(self, customer, email, email_xyz_num):
        self.customer = customer
        self.email = email
        self.email_xyz_num = email_xyz_num

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/capsule_1')
def capsule_1():
    return render_template('capsule_1.html')

@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        customer = request.form['customer']
        email = request.form['email']
        #makes sure there is a name and email filled out
        if customer == '' or email == '':
            return render_template('index.html', message='Please enter required fields')
        #makes sure the email doesn't already exist in our table
        #may want to take this out if user wants to receive multiple emails
        #may also want to keep this and delete records that have finished the capsule
        if db.session.query(email_table).filter(email_table.email == email).count() == 0:
            data = email_table(customer, email, email_xyz_num = 1)
            db.session.add(data)
            db.session.commit()
            
            #Send them the first email
            ######################################
            email_body = emails_x.emails[0]
            
            msg = EmailMessage()
            msg['Subject'] = 'test subject'
            msg['From'] = 'playlistcapsule@gmail.com'
            msg['To'] = email
            msg.set_content('test body 2')
            
            #email in html format
            msg.add_alternative(f'''
            <!DOCTYPE html>
            <html>
              <head>
                <meta charset="utf-8" />
                <meta name="viewport" content="width=device-width, initial-scale=1" />
                <link
                  rel="stylesheet"
                  href="https://cdn.jsdelivr.net/npm/bulma@0.9.1/css/bulma.min.css"
                />
              </head>
              <body>
                <section class="section">
                  <div class="columns">
                    <div class="column">
                      <p class="subtitle">
                        {email_body}
                      </p>
                      <a href="https://wavecapsules.herokuapp.com/">https://wavecapsules.herokuapp.com/</a>
                    </div>
                  </div>
                </section>
              </body>
            </html>
            ''', subtype = 'html'
            )
            
            #not 100% sure how smtp works, but it sends the message
            with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
                smtp.ehlo()
                smtp.starttls()
                smtp.ehlo()
                
                smtp.login('playlistcapsule@gmail.com','playcap3178')
                
                smtp.send_message(msg)
            ######################################
            return render_template('success.html')
        return render_template('index.html', message='You have already signed up with this email')
        


if __name__ == '__main__':
    app.run()