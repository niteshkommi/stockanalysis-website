from django.shortcuts import render,redirect
import pandas as pd
import numpy as np
from bfxhfindicators import Stochastic
from django.contrib.auth.decorators import login_required
from django.conf import settings
from accounts.forms import UserProfileUpdate

import csv
import datetime
import requests
from .models import endOfDay

entryTargets = []
params = {
    'access_key': '56f867af559034d445cf6e5447ee0e54'
}

def isDoji(out):
    wicks = abs(out[1] - out[2])
    body = abs(out[0] - out[3])
    percentage = 100 / (wicks/body)
    if (percentage <= 33):
        return out


def stochastic(candles):
    stochValues = []
    iStoch = Stochastic(5, 3, 3)
    for candle in candles:
        iStoch.add(candle)
        stochValues.append(iStoch.v())
    return (stochValues)


def HEIKIN(O, H, L, C, oldO, oldC):
    HA_Open = (oldO + oldC)/2
    HA_Close = (O + H + L + C)/4
    elements = np.array([H, L, HA_Open, HA_Close])
    HA_High = elements.max(0)
    HA_Low = elements.min(0)
    out = [HA_Open, HA_High, HA_Low, HA_Close]
    return out


def maxMin(fiboRange):
    rangeMax = max(max(x) if isinstance(x, list) else x for x in fiboRange)
    rangeMin = min(min(x) if isinstance(x, list) else x for x in fiboRange)
    return (rangeMax, rangeMin)


def fibonacciDown(price_max, price_min):
    tempList = []

    diff = price_max - price_min
    level0 = price_max
    level1 = price_max - 0.236 * diff
    level2 = price_max - 0.382 * diff
    level3 = price_max - 0.50 * diff
    level4 = price_max - 0.618 * diff
    level5 = price_max - 0.786 * diff

    tempList = [level1, level2, level3, level4, level5, level0]
    entryTargets.append(tempList)

    return entryTargets


def fibonacciUp(price_max, price_min):
    tempList = []

    diff = price_max - price_min
    level0 = price_max - 1.0 * diff
    level1 = price_max - 0.786 * diff
    level2 = price_max - 0.618 * diff
    level3 = price_max - 0.50 * diff
    level4 = price_max - 0.366 * diff
    level5 = price_max - 0.236 * diff

    tempList = [level1, level2, level3, level4, level5, level0]
    entryTargets.append(tempList)

    return entryTargets

def Computation():
    symbols = ['SBIN', 'BAJFINANCE', 'ULTRACEMCO', 'RELIANCE', 'MARUTI', 'TCS', 'PEL', 'INFY', 'TATASTEEL',
               'ASIANPAINT', 'DIVISLAB', 'BAJAJ_AUTO', 'GAIL', 'ADANIPORTS', 'BPCL', 'SHREECEM', 'ICICIBANK', 'HDFCBANK', 'ONGC', 'UPL',
               'LT', 'TATAMOTORS', 'KOTAKBANK', 'AXISBANK', 'DRREDDY', 'BHARTIARTL', 'NTPC', 'ITC', 'JSWSTEEL',
               'COALINDIA', 'HDFC', 'NMDC', 'INDUSINDBK', 'HEROMOTOCO', 'EICHERMOT', 'SUNPHARMA', 'WIPRO', 'HUL',
               'M&M', 'TECHM',
    ]


    for symbol in symbols:
        n = 48
        j = 0
        openPrice = []
        highPrice = []
        lowPrice = []
        closePrice = []
        dates = []
        last_closedPrice = 0
        hikenCandle = []
        doji = []
        swing = []
        dateTime = []
        closedPrice = []
        

        try:
            api_result = requests.get(
                'http://api.marketstack.com/v1/tickers/'+symbol+'.XNSE/eod', params)

            api_response = api_result.json()
            
            for stock_data in api_response['data']['eod']:  
                openPrice.append(stock_data['open'])
                highPrice.append(stock_data['high'])
                lowPrice.append(stock_data['low'])
                closePrice.append(stock_data['close'])
                dates.append(stock_data['date'])
            curr_date = api_response['data']['eod'][0]['date']
            today_closePrice = api_response['data']['eod'][0]['close']

            candle = HEIKIN(openPrice[n], highPrice[n],
                            lowPrice[n], closePrice[n], openPrice[n+1],
                            closePrice[n+1])

            hikenCandle.append(candle)

            for i in range(n-1, -1, -1):
                candle = HEIKIN(openPrice[i], highPrice[i], lowPrice[i],
                                closePrice[i], hikenCandle[j][0], hikenCandle[j][3])

                hikenCandle.append(candle)
                dateTime.append(dates[i])
                closedPrice.append(closePrice[i])
                j += 1

            stochasticHiken = stochastic(hikenCandle)
            del stochasticHiken[:4]

            for i in hikenCandle:
                doji.append(isDoji(i))

            del doji[:4]
            del dateTime[:3]
            del closedPrice[:3]

            for i in range(1, len(stochasticHiken)):
                if ((stochasticHiken[i]['k'] < stochasticHiken[i]['d']) and stochasticHiken[i-1]['k'] > stochasticHiken[i-1]['d']) or ((stochasticHiken[i]['k'] > stochasticHiken[i]['d']) and stochasticHiken[i-1]['k'] < stochasticHiken[i-1]['d']):
                    swing.append(i)

            for i in range(len(stochasticHiken)):
                if (stochasticHiken[i]['k'] < stochasticHiken[i]['d'] and stochasticHiken[i-1]['k'] > stochasticHiken[i-1]['d']):
                    try:
                        if doji[i]:
                            if i != 0:
                                swingIndex = swing.index(i)
                                if swingIndex != 0:
                                    temp = maxMin(
                                        hikenCandle[swing[swingIndex-1] + 4: swing[swingIndex] + 4])
                                    testList = fibonacciDown(
                                        temp[0], temp[1])
                                    lastCandle = i
                                    callTime = dateTime[i]
                                    hiken_closedPrice = hikenCandle[i+4][3]
                                    last_closedPrice = closedPrice[i]
                        elif doji[i-1] or doji[i+1] or doji[i+2]:
                            if i != 0:
                                swingIndex = swing.index(i)
                                if swingIndex != 0:
                                    temp = maxMin(
                                        hikenCandle[swing[swingIndex-1] + 4: swing[swingIndex] + 4])
                                    testList = fibonacciDown(
                                        temp[0], temp[1])
                                    lastCandle = i
                                    callTime = dateTime[i]
                                    hiken_closedPrice = hikenCandle[i+4][3]
                                    last_closedPrice = closedPrice[i]
                    except (IndexError):
                        pass
                elif (stochasticHiken[i]['k'] > stochasticHiken[i]['d'] and stochasticHiken[i-1]['k'] < stochasticHiken[i-1]['d']):
                    try:
                        if doji[i]:
                            if i != 0:
                                swingIndex = swing.index(i)
                                if swingIndex > 0:
                                    temp = maxMin(
                                        hikenCandle[swing[swingIndex-1] + 4: swing[swingIndex] + 4])
                                    testList = fibonacciUp(
                                        temp[0], temp[1])
                                    lastCandle = i
                                    callTime = dateTime[i]
                                    hiken_closedPrice = hikenCandle[i+4][3]
                                    last_closedPrice = closedPrice[i]
                        elif doji[i-1] or doji[i+1] or doji[i+2]:
                            if i != 0:
                                swingIndex = swing.index(i)
                                if swingIndex > 0:
                                    temp = maxMin(
                                        hikenCandle[swing[swingIndex-1] + 4: swing[swingIndex] + 4])
                                    testList = fibonacciUp(
                                        temp[0], temp[1])
                                    lastCandle = i
                                    callTime = dateTime[i]
                                    hiken_closedPrice = hikenCandle[i+4][3]
                                    last_closedPrice = closedPrice[i]
                    except (IndexError):
                        pass
            
            try:
                h_l = maxMin(hikenCandle[lastCandle + 5:])
            except(ValueError):
                h_l = [0,0]

        except (KeyError):
            keyerror = "Please provide a correct ticker"
        


        # for i in range(len(testList[-1])):
        #     testList[-1][i] = round(testList[-1][i],2)

        testList[-1].append(symbol)
        last_closedPrice = round(last_closedPrice,2)

        # Adjusting the difference
        diff = round(hiken_closedPrice - testList[-1][0], 2)
        for i in range(6):
            testList[-1][i] = round(testList[-1][i] + diff, 2)


        call = testList[-1][0]
        stopLoss = testList[-1][5]
        high = h_l[0]
        low = h_l[1]
        Target1 = testList[-1][1]
        Target2 = testList[-1][2]
        Target3 = testList[-1][3]
        Target4 = testList[-1][4]

        if(high == 0 and low == 0):
            status = "Awaiting Targets"
            context = {
                "stock_data": stock_data,
                "status": status
            }

        else:
            if (call > stopLoss):
                if(high >= Target1 and high < Target2):
                    status = "Target 1 Reached"
                elif(high >= Target2 and high < Target3):
                    status = "Target 2 Reached"
                elif(high >= Target3 and high < Target4):
                    status = "Target 3 Reached"
                elif(high >= Target4):
                    status = "Final Target Reached"
                elif(low <= stopLoss):
                    status = "Stop Loss has occured"
                else:
                    status = "Awaiting Targets"

            else:
                if(low <= Target1 and low > Target2):
                    status = "Target 1 Reached"
                elif(low <= Target2 and low > Target3):
                    status = "Target 2 Reached"
                elif(low <= Target3 and low > Target4):
                    status = "Target 3 Reached"
                elif(low <= Target4):
                    status = "Final Target Reached"
                elif(high >= stopLoss):
                    status = "Stop Loss has occured"
                else:
                    status = "Awaiting Targets"

        filename = settings.MEDIA_ROOT+'/'+symbol+'_report.csv'

        if endOfDay.objects.filter(symbol=symbol).exists():

            with open(filename, 'a+', newline='') as f:
                fieldnames = ['Date', 'Close_Price', 'Signal_Date', 'Call',
                              'Stop_Loss', 'Target_1', 'Target_2', 'Target_3', 'Target_4', 'Status']
                thewriter = csv.DictWriter(f, fieldnames=fieldnames)

                thewriter.writerow(
                    {'Date': curr_date[:10], 'Close_Price': today_closePrice, 'Signal_Date': callTime[:10],
                     'Call': call, 'Stop_Loss': stopLoss, 'Target_1': Target1,
                     'Target_2': Target2, 'Target_3': Target3, 'Target_4': Target4,
                     'Status': status
                     })

            data = endOfDay.objects.get(symbol=symbol)
            data.date = callTime[:10] 
            data.currDate = curr_date[:10]
            data.closePrice = today_closePrice
            data.call = call
            data.stopLoss = stopLoss
            data.Target1 = Target1
            data.Target2 = Target2
            data.Target3 = Target3
            data.Target4 = Target4  
            data.high = high
            data.low = low
            data.status = status
            data.report = symbol + '_report.csv'
        
        else:

            with open(filename, 'w', newline='') as f:
                fieldnames = ['Date', 'Close_Price', 'Signal_Date','Call','Stop_Loss','Target_1','Target_2','Target_3','Target_4','Status']
                thewriter = csv.DictWriter(f,fieldnames=fieldnames)

                thewriter.writeheader()

                thewriter.writerow(
                    {'Date': curr_date[:10], 'Close_Price': today_closePrice, 'Signal_Date': callTime[:10],
                     'Call': call, 'Stop_Loss': stopLoss, 'Target_1': Target1,
                     'Target_2': Target2, 'Target_3': Target3, 'Target_4': Target4,
                     'Status': status
                    })
                

            data = endOfDay(symbol=symbol, date=callTime[:10], currDate=curr_date[:10], closePrice=today_closePrice,
                                call=call, stopLoss=stopLoss, Target1=Target1, Target2=Target2, Target3=Target3, Target4=Target4,
                            high=high, low=low,status = status, report=symbol +
                            '_report.csv'
                                )

        data.save()


@login_required(login_url='login')
def dashboard(request):

    if request.method == 'POST':
        status = ""

        symbol = request.POST.get('ticker').upper()

        stock_data = endOfDay.objects.all().filter(pk=symbol)

        if stock_data:
            call = endOfDay.objects.filter(pk=symbol).values('call')[0]['call']
            stopLoss = endOfDay.objects.filter(
                pk=symbol).values('stopLoss')[0]['stopLoss']
            Target1 = endOfDay.objects.filter(
                pk=symbol).values('Target1')[0]['Target1']
            Target2 = endOfDay.objects.filter(
                pk=symbol).values('Target2')[0]['Target2']
            Target3 = endOfDay.objects.filter(
                pk=symbol).values('Target3')[0]['Target3']
            Target4 = endOfDay.objects.filter(
                pk=symbol).values('Target4')[0]['Target4']
            high = endOfDay.objects.filter(pk=symbol).values('high')[0]['high']
            low = endOfDay.objects.filter(pk=symbol).values('low')[0]['low']

            if(high == 0 and low == 0):
                status = "Awaiting Targets"
                context = {
                    "stock_data": stock_data,
                    "status": status
                }

            else:
                if (call > stopLoss):
                    if(high >= Target1 and high < Target2):
                        status = "Target 1 Reached"
                    elif(high >= Target2 and high < Target3):
                        status = "Target 2 Reached"
                    elif(high >= Target3 and high < Target4):
                        status = "Target 3 Reached"
                    elif(high >= Target4):
                        status = "Final Target Reached"
                    elif(low <= stopLoss):
                        status = "Stop Loss has occured"
                    else:
                        status = "Awaiting Targets"

                else:
                    if(low <= Target1 and low > Target2):
                        status = "Target 1 Reached"
                    elif(low <= Target2 and low > Target3):
                        status = "Target 2 Reached"
                    elif(low <= Target3 and low > Target4):
                        status = "Target 3 Reached"
                    elif(low <= Target4):
                        status = "Final Target Reached"
                    elif(high >= stopLoss):
                        status = "Stop Loss has occured"
                    else:
                        status = "Awaiting Targets"

                context = {
                    "stock_data": stock_data,
                    "status": status
                }
                return render(request, 'main/search.html', context)
        else:
            error = "This ticker is not supported"
            context = {
                "error": error
            }
            return render(request, 'main/search.html', context)

    else:
        context = {"none": None}



    # Computation()
    currDate = endOfDay.objects.filter(pk='SBIN').values('currDate')[0]['currDate']
    stock_data = endOfDay.objects.all().filter(date=currDate)
    context = {
        'stock_data': stock_data
    }

    return render(request, 'main/dashboard.html', context)


@login_required(login_url='login')
def search(request):

    if request.method == 'POST':
        status = ""

        symbol = request.POST.get('ticker').upper()

        stock_data = endOfDay.objects.all().filter(pk=symbol)

        if stock_data:
            call        = endOfDay.objects.filter(pk=symbol).values('call')[0]['call']
            stopLoss    = endOfDay.objects.filter(pk=symbol).values('stopLoss')[0]['stopLoss']
            Target1     = endOfDay.objects.filter(pk=symbol).values('Target1')[0]['Target1']
            Target2     = endOfDay.objects.filter(pk=symbol).values('Target2')[0]['Target2']
            Target3     = endOfDay.objects.filter(pk=symbol).values('Target3')[0]['Target3']
            Target4     = endOfDay.objects.filter(pk=symbol).values('Target4')[0]['Target4']
            high        = endOfDay.objects.filter(pk=symbol).values('high')[0]['high']
            low         = endOfDay.objects.filter(pk=symbol).values('low')[0]['low']

            if(high == 0 and low == 0):
                status = "Awaiting Targets"
                context = {
                    "stock_data": stock_data,
                    "status": status
                }
            
            else:
                if (call > stopLoss):
                    if(high >= Target1 and high < Target2):
                        status = "Target 1 Reached"
                    elif(high >= Target2 and high < Target3):
                        status = "Target 2 Reached"
                    elif(high >= Target3 and high < Target4):
                        status = "Target 3 Reached"
                    elif(high >= Target4):
                        status = "Final Target Reached"
                    elif(low <= stopLoss):
                        status = "Stop Loss has occured"
                    else:
                        status = "Awaiting Targets"
                
                else:
                    if(low <= Target1 and low > Target2):
                        status = "Target 1 Reached"
                    elif(low <= Target2 and low > Target3):
                        status = "Target 2 Reached"
                    elif(low <= Target3 and low > Target4):
                        status = "Target 3 Reached"
                    elif(low <= Target4):
                        status = "Final Target Reached"
                    elif(high >= stopLoss):
                        status = "Stop Loss has occured"
                    else:
                        status = "Awaiting Targets"

                context = {
                    "stock_data": stock_data,
                    "status": status
                    }
        else:
            error = "This ticker is not supported"
            context = {
                "error": error
            }

        
    else:
        context = { "none": None }
    return render(request, 'main/search.html',context)


@login_required(login_url='login')
def reports(request):

    if request.method == 'POST':
        status = ""

        symbol = request.POST.get('ticker').upper()

        stock_data = endOfDay.objects.all().filter(pk=symbol)

        if stock_data:
            return render(request, 'main/search.html', {'stock_data': stock_data})

        else:
            return render(request, 'main/search.html', {'error': "This ticker is not supported"})


    stock_data = endOfDay.objects.all()

    return render(request, 'main/reports.html',{'stock_data':stock_data})


@login_required(login_url='login')
def profile(request):

    if request.POST:
        form = UserProfileUpdate(request.POST, instance=request.user)
        if form.is_valid():
            form.save()

            return redirect('profile')
    else:
        form = UserProfileUpdate(
            initial={
                "username": request.user.username,
                "email": request.user.email,
            }
        )

    context = {
        'form': form,
    }

    return render(request, 'main/profile.html', context)
