import psycopg2 as pg
import smtplib
from email.message import EmailMessage
import email_text.emails_x as emails_x

#Connects to our postgres SQL table
ENV = 'DEV'

if ENV == 'DEV':
    con = pg.connect(
            host = 'localhost',
            database = 'heroku_email',
            user = 'postgres',
            password = '@Jakc1324'
            )
else:
    con = pg.connect(
            host = 'ec2-54-236-156-167.compute-1.amazonaws.com',
            database = 'd2hbi00jt18m86',
            user = 'zyzkwvmnmkixyu',
            password = '53a3283cb5aa384f064f2486de811a2a9528ea854c4f3cb52558d6a82fde2dfc'
            )

#Imports a dictionary with all the emails we want to send
email_dict = emails_x.emails

#Not 100% what the curser does
cur = con.cursor()

for email_key, email_body in email_dict.items():
    #ignores the first day because we will send the first day at the 
    #initial registration
    if email_key == 0:
        continue
    #Queries all the emails for each day
    cur.execute(f'''SELECT DISTINCT email FROM emails
                WHERE email_xyz_num = {email_key}''')
    
    #collects the emails and gets them into a formatted list
    rows = cur.fetchall()
    email_list = [x[0] for x in rows]
    
    #if the list isn't empty, send an email from playlistcapsule
    if email_list:
        msg = EmailMessage()
        msg['Subject'] = 'test subject'
        msg['From'] = 'playlistcapsule@gmail.com'
        msg['Bcc'] = email_list
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

#Increments the email number
cur.execute('''UPDATE emails SET email_xyz_num = email_xyz_num + 1''')      
con.commit()

#Delete emails that have finished their capsule
cur.execute(f'''DELETE FROM emails WHERE email_xyz_num >= {len(email_dict)}''')
con.commit()

#close the cursor and the connection
cur.close()

con.close()
