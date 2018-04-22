import requests
import json
import xmltodict
import time
import datetime

interval = 600
API_GET_VIEW_MARKET = "https://live.bullionvault.com/secure/api/v2/view_market_xml.do"
login_page_url = "https://or.bullionvault.fr/secure/login.do"
login_page_url2 = "https://live.bullionvault.com/secure/j_security_check"
payload2 = {'j_username': '', 'j_password': '', 'considerationCurrency': 'GBP', 'securityId': 'AUXLN',  'marketWidth' : 2}
#payload2 = {'j_username': 'uname', 'j_password': 'pwd', 'considerationCurrency': 'GBP', 'securityId': 'AUXLN', 'marketWidth' : 5}####
payload3 = {'confirmed': 'true'}
payload4 = {'simple': 'true'}

def login(session, login_url, sec_check_url, pl2):
        s = session
        a = s.get(login_page_url)
        #print a      
        b = s.post(login_page_url2, data = payload2)


def get(inFno, s):
    #with requests.Session() as s:
    with s:
#        a = s.get(login_page_url)
        #print a      
#        b = s.post(login_page_url2, data = payload2)
        d = s.get("https://live.bullionvault.com/secure/api/v2/view_balance_xml.do", params = payload4)
        c = s.get("https://live.bullionvault.com/secure/api/v2/view_orders_xml.do", params = payload3)
        e = s.get(API_GET_VIEW_MARKET, params=payload2)
        #print e.content
        j = xmltodict.parse(e.content)
        o = (json.dumps(j, indent=4, sort_keys=True))
        fno = 1
        fname = 'bvout.' + str(inFno) + '.out'
        with open(fname, 'w') as f:
            f.truncate()
            #f.write(str(o) for m in e.content)
            f.write(o)
            
    return j

    
print ("getting session")

dl = open('daily_log.log', 'w')
dlcsv = open('daily_csv.csv', 'w')
dlcsv.write(str("date time" + "," + "bid price per kg" + "," + "offer price per kg" + "," + "spread pct" + ","
            + "our_bid" + "," 
            + "our_spct" + "," 
            + "total quantity on offer" + ","
            + "avg offer price per kg" + ","
            + "total quantity on sale" + ","
            + "avg sale price per kg" + ","     
            + "\n" ))

sess = requests.Session()    
login(sess, login_page_url,login_page_url2, payload2) 
print ('Time is now: ' + str(datetime.datetime.now()))

last_buy_price_list = {}
last_sell_price_list = {}

#i = 0
for i in range(100):
    print ('Fetching at: ' + str(datetime.datetime.now()))
    print(i)
    #i+=1
    
    
    d = get(i, sess)
    
    #print (d)
    
    envelope = d['envelope']
    #print (msg)
    message = envelope['message']
    #print (mrkt)
    market = message['market']
    #print (market)
    pitches = market['pitches']
    #print (pitches)
    pitch = pitches['pitch']
    #print(pitch)
    buy_price_list = pitch['buyPrices']
    sell_price_list = pitch['sellPrices']

    diff = 0
    
    if buy_price_list == last_buy_price_list:
        print ('No difference in buys at ' + str(datetime.datetime.now()))
        #work out... ?
        lastbuy_price_list = dict(buy_price_list)
    else:
        diff = 1
        print ('difference in buys at ' + str(datetime.datetime.now()))
        curr_bp_list = list(buy_price_list["price"])
        #bp0 = curr_bp_list[0]
        last_buy_price_list = dict(buy_price_list)
        buy_q_list = []
        buy_limits_list = []
        for i, val in enumerate(list(curr_bp_list)):
            #print("new iteration")
            buy_limits_list.append(float(val["@limit"]))
            buy_q_list.append(float(val["@quantity"]))
        #print (buy_price_list)
        #print (lastbuy_price_list)
#        q = bp0["@quantity"]
        tqoo = sum(buy_q_list)
        avgoffp = sum(buy_limits_list) / len(buy_limits_list)
        #print ("Total quantity on offer: " + str(sum(buy_q_list)))
        q = buy_q_list[0]
#        oppkg = bp0["@limit"]
        oppkg = buy_limits_list[0]
        print("new offer price: " + str(oppkg))
        bdealp = (float(oppkg) * float(q)) 

    if sell_price_list == last_sell_price_list:
        print ('No difference in sells at ' + str(datetime.datetime.now()))
        #work out... ?
        # Changed this to sell_price_list
        #lastbuy_price_list = dict(buy_price_list)
        last_sell_price_list = dict(sell_price_list)
    else:
        diff = 1
        print ('difference in sells at ' + str(datetime.datetime.now()))
        curr_sp_list = sell_price_list["price"]
        last_sell_price_list = dict(sell_price_list)
        sell_q_list = []
        sell_limits_list = []
        for i, val in enumerate(list(curr_sp_list)):
            #print("new iteration")
            sell_limits_list.append(float(val["@limit"]))
            sell_q_list.append(float(val["@quantity"]))
        #print (buy_price_list)
        #print (lastbuy_price_list)
#        q = bp0["@quantity"]
        tqfs = sum(sell_q_list)
        avgsellp = sum(sell_limits_list) / len(sell_limits_list)
        #print ("Total quantity for sale: " + str(sum(sell_q_list)))
        q = sell_q_list[0]
#        oppkg = bp0["@limit"]
        bidppkg = sell_limits_list[0]
        print("new bid price: " + str(bidppkg))
        sdealp = (float(bidppkg) * float(q)) 
        #print(" sell dealprice: " + str(sdealp))
    
    #get spread pct
    #diff = 1
    if diff:
        spct = ((float(bidppkg) - float(oppkg)) / float(bidppkg)) * 100
        print ("spread pct: " +str(spct))
        
        #how much to offer to sell for?
        our_spct = spct - ((spct / 100) * 5)
        print("our spct: " + str(our_spct))
        our_bid = bidppkg - ((bidppkg / 100) * our_spct)
        print("our bid:  " + str(our_bid) + " bid price: " + str(bidppkg) + " offer price: " + str(oppkg))
        
        dl.write(str(datetime.datetime.now()) + " bid price: " + str(bidppkg) + " offer price: " + str(oppkg) + " spread pct: " + str(spct) + "\n" )
        dlcsv.write(str(datetime.datetime.now()) + "," + str(bidppkg) + "," + str(oppkg) + "," + str(spct) + ","
            + str(our_bid) + "," 
            + str(our_spct) + "," 
            + str(tqoo) + ","
            + str(avgoffp) + ","
            + str(tqfs) + ","
            + str(avgsellp) + ","     
            + "\n" )
        #print(str(datetime.datetime.now()) + " bid price: " + str(bidppkg) + " offer price: " + str(oppkg) + " spread pct: " + str(spct) + "\n" )
        #print("high and low: ")
        diff = 0
        
    time.sleep(interval)        

   