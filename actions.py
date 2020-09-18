from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from rasa_sdk import Action
from rasa_sdk.events import SlotSet
import zomatopy
import json
import pandas as pd
import smtplib
from email.message import EmailMessage

restaurant_data = [] 

class ActionSearchRestaurants(Action):
    def name(self):
        return 'action_search_restaurants'

    def run(self, dispatcher, tracker, domain):
        config={ "user_key":"a4189acedfdfc4d49198308978e2dab5"}
        zomato = zomatopy.initialize_app(config)  
        loc = tracker.get_slot('location')        
        cuisine = tracker.get_slot('cuisine')
        price = tracker.get_slot('price')
        location_detail=zomato.get_location(loc, 1)
        d1 = json.loads(location_detail)
        lat=d1["location_suggestions"][0]["latitude"]
        lon=d1["location_suggestions"][0]["longitude"]
        cuisines_dict={'american': 1,'chinese': 25, 'north indian': 50, 'italian': 55, 'mexican': 73, 'south indian': 85}
        price_dict={'Lesser than Rs. 300': 1,'Rs. 300 to 700': 2, 'More than 700':3} 
        p = int(price_dict.get(price))
        if p==1:
            max_price = 299
            min_price = 0
        elif p==2:
            min_price = 300
            max_price = 700
        else:
            min_price = 701
            max_price = 10000
        
        results = zomato.restaurant_search("", lat, lon, str(cuisines_dict.get(cuisine)),10000)
        i = 0
        d = json.loads(results)
        response=""
        global restaurant_data
        if d['results_found'] == 0:
            response= "no results"
        else:
            
            data = sorted(d['restaurants'], key = lambda k: k['restaurant']['user_rating']['aggregate_rating'],reverse = True)                       
            for restaurant in  data:                 
                if ((restaurant['restaurant']['average_cost_for_two']>= min_price) and (restaurant['restaurant']['average_cost_for_two']<= max_price)):
                    restaurant_data.append(restaurant)
                    i = i+1
            if(i == 0):
                response = "Sorry, No results found for your criteria."
            else:
                i = 1
                for restaurant in restaurant_data[:5]:
                    response = "\n"+ response + str(i)+" : "+restaurant['restaurant']['name']+ " in "+ restaurant['restaurant']['location']['address'] + " has been rated " +restaurant['restaurant']['user_rating']['aggregate_rating']+"\n"           
                    i=i+1
                      
        dispatcher.utter_message(response)
        return [SlotSet('location',loc)]

class ActionSendEmail(Action):
    def name(self):
        return 'action_send_email'
    def run(self, dispatcher, tracker, domain):
        i = 1
        response = ""
        loc =  tracker.get_slot('location')
        cuisine =  tracker.get_slot('cuisine')
        email = tracker.get_slot('email')
        msg = EmailMessage() 
        msg['Subject'] =  "Top "+cuisine.upper()+" Restaurants in "+loc.upper()+"!!!!!"
        msg['From'] = "upgrad.foodiebot@gmail.com"
        msg['To'] = email
        global restaurant_data
        
        for restaurant in  restaurant_data[:10]:               
                                        
             response = "\n"+ response+ str(i)+" : "+ " Name: "+restaurant['restaurant']['name']+ "\n"+ "Address: "+ restaurant['restaurant']['location']['address'] + "\n"+"Average cost for two: " + str(restaurant['restaurant']['average_cost_for_two'])+ "\n"+ "Rating: "+restaurant['restaurant']['user_rating']['aggregate_rating']+"\n"           
             i=i+1
        msg_body = " Greetings from Chatbot!.\n Here are top restaurants for you.\n\n"+response

        msg.set_content(msg_body)
        
        try: 
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login("upgrad.foodiebot@gmail.com", "upgrad123")
            server.send_message(msg)
            server.quit()
        except:
            print ('Something went wrong...')
class ActionCheckLocation(Action):

    def name(self):
        return 'action_check_location'

    def run(self, dispatcher, tracker, domain):
        loc = tracker.get_slot('location')      
        location_list=['Ahmedabad', 'Bangalore', 'Chennai', 'Delhi', 'Hyderabad', 'Kolkata', 'Mumbai', 'Pune',
        'Agra', 'Ajmer', 'Aligarh', 'Amravati', 'Amritsar', 'Asansol', 'Aurangabad', 'Bareilly',
        'Belgaum', 'Bhavnagar', 'Bhiwandi', 'Bhopal', 'Bhubaneswar', 'Bikaner', 'Bokaro Steel City',
        'Chandigarh', 'Coimbatore', 'Cuttack', 'Dehradun', 'Dhanbad', 'Durg-Bhilai Nagar', 'Durgapur',
        'Erode', 'Faridabad', 'Firozabad',    'Ghaziabad', 'Gorakhpur', 'Gulbarga', 'Guntur', 'Gurgaon',
        'Guwahati', 'Gwalior', 'Hubli-Dharwad', 'Indore', 'Jabalpur', 'Jaipur', 'Jalandhar', 'Jammu', 'Jamnagar',
        'Jamshedpur', 'Jhansi', 'Jodhpur', 'Kannur', 'Kanpur', 'Kakinada', 'Kochi', 'Kottayam', 'Kolhapur', 'Kollam',
        'Kota', 'Kozhikode', 'Kurnool', 'Lucknow', 'Ludhiana', 'Madurai', 'Malappuram', 'Mathura', 'Goa', 'Mangalore',
        'Meerut', 'Moradabad', 'Mysore', 'Nagpur', 'Nanded', 'Nashik', 'Nellore', 'Noida', 'Palakkad', 'Patna',
        'Pondicherry', 'Prayagraj', 'Raipur', 'Rajkot', 'Rajahmundry', 'Ranchi', 'Rourkela', 'Salem', 'Sangli',
        'Siliguri', 'Solapur', 'Srinagar', 'Sultanpur', 'Surat', 'Thiruvananthapuram', 'Thrissur', 'Tiruchirappalli',
        'Tirunelveli', 'Tiruppur', 'Ujjain', 'Bijapur', 'Vadodara', 'Varanasi', 'Vasai-Virar City', 'Vijayawada']
        
        location_list = [x.lower() for x in location_list]
        
        if loc.lower() not in location_list:
            dispatcher.utter_message("We do not operate in that area yet. Can you specify some other location?")
        return


     
