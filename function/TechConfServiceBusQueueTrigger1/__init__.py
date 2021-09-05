import logging
import azure.functions as func
import psycopg2
import os
from datetime import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def main(msg: func.ServiceBusMessage):

    logging.info(msg.get_body())
    notification_id = int(msg.get_body().decode('UTF-8'))
    logging.info('Python ServiceBus queue trigger processed message: %s',notification_id)

    connection = psycopg2.connect(dbname="techconfdb", user="techconfadmin@techconf-server", password="Admin@12345", host="techconf-server.postgres.database.azure.com")
    cursor = connection.cursor()
    
    try:
        # TODO: Get notification message and subject from database using the notification_id
        notification = cursor.execute("SELECT message, subject FROM notification WHERE id = {};".format(notification_id))

        # TODO: Get attendees email and name
        cursor.execute("SELECT first_name, last_name, email FROM attendee;")

        attendees = cursor.fetchall()
        
        for attendee in attendees:
            Mail('{}, {}, {}'.format({'admin@techconf.com'}, {attendee[2]}, {notification}))
        notificationDate = datetime.utcnow()
        notificationInfo = 'Notified {} attendees'.format(len(attendees))

        # TODO: Update the notification table by setting the completed date and updating the status with the total number of attendees notified
        cursor.execute("UPDATE notification SET status = '{}', completed_date = '{}' WHERE id = {};".format(notificationInfo, notificationDate, notification_id))        
        connection.commit()

    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(error)
    finally:
        # TODO: Close connection
        cursor.close()
        connection.close()