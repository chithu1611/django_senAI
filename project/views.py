from django.shortcuts import render,redirect
from django.http import HttpResponse
from bs4 import BeautifulSoup
import requests
from textblob import TextBlob
from torch import logit
from transformers import pipeline
from .forms import MyForm
from .form2 import CustomUserForm
from django.contrib import messages
from django.contrib.auth import authenticate, login as user_login, logout

import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt

import io
import base64

# from selenium import webdriver
# from amazoncaptcha import AmazonCaptcha
# from selenium.webdriver.common.by import By


# driver = webdriver.Chrome(executable_path="driver/chromedriver")

# web_unblocker = {
#     "http": "http://chithurvt016@gmail.com:Gowri@2502@unblock.oxylabs.io:60000",
#     "https": "http://chithurvt016@gmail.com:Gowri@2502@unblock.oxylabs.io:60000",
# }



def login(request):
    if request.method == "POST":
        name = request.POST.get('username')
        pwd = request.POST.get('password')
        user = authenticate(request, username=name, password=pwd)
        print(user)
        if user is not None:
            user_login(request, user)
            messages.success(request, "Login Successful")
            return redirect('sentinel/') 
        else:
            messages.error(request, "Invalid User Name or Password")
    return render(request, "login.html")

def register(request):
    form=CustomUserForm()
    if request.method=="POST":
        form=CustomUserForm(request.POST)
        print(form)
        if form.is_valid():
            print(form)
            form.save()
            messages.success(request,"Registration Success")
            return redirect('/')
    return render(request,"register.html",{'form':form})

def home(request):
    return render(request,"index.html")


def logout_page(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request,"Logged out successfully")
    return redirect("/")

def senAI(request):
    if request.method == 'POST':
        form = MyForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['text']
            customer_header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36'}
            try:
                response = requests.get(url, verify=False, headers=customer_header)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "html.parser")
                review_element = soup.select("div.review")

                product_title = soup.select("div.product-title")

                # for rv_name in product_title:
                #     if rv_name.select_one("a.a-link-normal"):
                #         product_name = rv_name.select_one("a.a-link-normal").text.strip()
                product_name = [review.select_one("a.a-link-normal").text.strip() for review in product_title]

                if len(product_name) != 0:
                    product_n = product_name[0]
                else:
                    product_n = "No Name For this Product"

                # print(product_name)
                # print("Request URL:", response.request.url)
                # print("Request headers:", response.request.headers)
                # print("Response status code:", response.status_code)
                # print("Response content:", response.text)

                scapped_review_name = [review.select_one("span.a-profile-name").text.strip() for review in review_element]
                scapped_review = [review.select_one("span.review-text").text.strip() for review in review_element]

                sentiment_analysis = pipeline("text-classification", model="RashidNLP/Amazon-Deberta-Base-Sentiment")
                analysis_result = sentiment_analysis(scapped_review)

                average_result = calculate_average(analysis_result)
                
                pie_chart_image = generate_pie_chart(analysis_result)

                # return render(request, 'result.html', {'analysis_result': analysis_result})
                zipped_data = zip(scapped_review_name,scapped_review,analysis_result)
                # return render(request, 'senAI.html', {'form': form,'result':analysis_result , 'review_name' : scapped_review_name , 'review' : scapped_review})
                return render(request, 'senAI.html', {'form': form,'zipped_data': zipped_data, 'avg_result':average_result, 'pie_chart': pie_chart_image, 'product_name': product_n})
            
            except requests.exceptions.RequestException as e:
                return HttpResponse("Error fetching URL: " + str(e))
            except Exception as e:
                return HttpResponse("An error occurred: " + str(e))
    else:
        form = MyForm()
        return render(request, 'senAI.html',{'form':form})
    

def calculate_average(datas):
    sentiment_scores = {"positive": 1, "negative": -1, "neutral": 0}

    total_score = 0

    for result_item in datas:
        sentiment_label = result_item['label'].lower()
        if sentiment_label in sentiment_scores:
            total_score += sentiment_scores[sentiment_label]

    if total_score>=0:
        return "This product is recommended for you to buy"

    return "This product is not recommended to buy, you can look for some other product"


def generate_pie_chart(datas):
    sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}

    for result_item in datas:
        sentiment_label = result_item['label'].lower()
        if sentiment_label in sentiment_counts:
            sentiment_counts[sentiment_label] += 1

    labels = sentiment_counts.keys()
    sizes = sentiment_counts.values()

    fig, ax = plt.subplots(figsize=(4, 3))
    wedges, texts, autotexts = ax.pie(sizes, autopct='%1.1f%%', startangle=140)

    # Manually create a legend with color patches and corresponding labels
    legend_labels = []
    for label, wedge in zip(labels, wedges):
        legend_labels.append(label)
        ax.legend(wedges, legend_labels, loc="center left", bbox_to_anchor=(1, 0.5))


    # plt.figure(figsize=(4, 3))
    # plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)

    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.title('Sentiment Analysis Results')

    plt.subplots_adjust(left=0.25)

    # Convert plot to image
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    plt.close()

    return image_base64