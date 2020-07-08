import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import *
from collections import defaultdict
from tkinter import messagebox
from textblob import TextBlob
import re
import pandas as pd
import tweepy
from PIL import Image, ImageTk

root=Tk()
root.geometry('1400x700')
root.title('Movie Review Analysis')


reviews=defaultdict(list)
class Review(Canvas):
    def __init__(self, **kw):
        super().__init__(width=1400, height=700, highlightthickness=0, background='black', **kw)

        self.heading='Welcome to Twitter Sentiments Analysis'
        self.create_text(700, 50, text='', fill='cyan', font='Abc 20 bold italic', tag='head')
        self.head_move()
        self.get_user()

        self.logo= Image.open('twitter.png')
        self.logo_tk=ImageTk.PhotoImage(self.logo)
        self.create_image(1150, 80, image=self.logo_tk)

    def head_move(self):
        s=self.itemcget(self.find_withtag('head'),'text')
        ns=len(s)
        c=self.itemcget(self.find_withtag('head'),'fill')

        if s=='Welcome to Twitter Sentiments Analysis':
            s=''
        else:
            s=self.heading[:ns+2]

        if c=='cyan':
            c='light green'
        else:
            c='cyan'
        self.itemconfigure(self.find_withtag('head'), fill=c)
        self.itemconfigure(self.find_withtag('head'), text=s)

        self.after(400,self.head_move)

    def get_user(self):
        self.create_text(300, 100, text='Please Enter User Name :', fill='white', font='abc 15 underline')
        self.e1 = Entry(root, bd=1, fg='midnight blue', bg='white', font='abc 15 bold')
        self.e1.focus_set()
        self.create_window(600, 100, window=self.e1, tag='movie_entry')

        self.bind_all('<Key>', self.on_enter_press)

    def on_enter_press(self, e):
        entered = e.keysym
        if (entered == 'Return' or entered == 'KP_Enter'):
            if (self.e1.get() == ''):
                messagebox.showerror('Error','Please Enter a valid user name !!', default='ok')
                return
            elif ( ' ' in self.e1.get() ):
                messagebox.showerror('Error', f'The Twitter handle must not contain any white spaces !\nTry { self.e1.get().replace(" ", "")}', default='ok')
                return
            else:
                self.delete(self.find_withtag('btrpr'), self.find_withtag('bttpr'), self.find_withtag('btrnr'), self.find_withtag('bttnr'))
                self.start_review(self.e1.get())

    @staticmethod
    def showp(self):
        pr = Tk()
        pr.title('Positive Tweets')
        frame = Frame(pr)
        scroll = Scrollbar(frame)
        scroll.pack(side=RIGHT, fill=Y)

        scroll2=Scrollbar(frame, orient=HORIZONTAL)
        scroll2.pack(side=BOTTOM, fill=X)

        listbox = Listbox(frame, yscrollcommand=scroll.set, xscrollcommand=scroll2.set)
        j = 1
        l=reviews['Positive']
        for i in l:
            try:
                listbox.insert(END, str(j) + '. ' + str(i))
                listbox.insert(END, ' ')
                j += 1
            except:
                pass
        listbox.pack(padx=10, pady=10, fill=BOTH, expand=True)
        scroll.config(command=listbox.yview)
        scroll2.config(command=listbox.xview)
        frame.pack(fill=BOTH, expand=True)
        pr.geometry('500x500')
        pr.mainloop()

    @staticmethod
    def shown(self):
        pr = Tk()
        pr.title('Negative Tweets')
        frame = Frame(pr)
        scroll = Scrollbar(frame)
        scroll.pack(side=RIGHT, fill=Y)

        scroll2 = Scrollbar(frame, orient=HORIZONTAL)
        scroll2.pack(side=BOTTOM, fill=X)

        listbox = Listbox(frame, yscrollcommand=scroll.set,  xscrollcommand=scroll2.set)
        j = 1
        l = reviews['Negative']
        for i in l:
            try:
                listbox.insert(END, str(j) + '. ' + str(i))
                listbox.insert(END, ' ')
                j += 1
            except:
                pass
        listbox.pack(padx=10, pady=10, fill=BOTH, expand=True)
        scroll.config(command=listbox.yview)
        scroll2.config(command=listbox.xview)
        frame.pack(fill=BOTH, expand=True)
        pr.geometry('500x500')
        pr.mainloop()


    def start_review(self, user):

        #My twitter credentials
        consumer_key='KNJv7m3khYTXuWvFS7Y6vnkTs'
        consumer_secret_key='jANitABEvaOZj50yF9n9InjRN3dsaC69DoNDx6rf3c2bLindXj'
        access_token='176084045-9HfXe1Dskd3xgyFv1HUMeDn4moDAhGHDizpTPqzP'
        access_token_secret='stM38xEN8MHHqbqcOoTC7T4TRmzZGsoQA6PRW0Kp842Ko'


        try:
            # Authenticate User and Get Access
            auth=tweepy.OAuthHandler(consumer_key, consumer_secret_key)
            auth.set_access_token(access_token, access_token_secret)

            # Create API object from auth info
            api=tweepy.API(auth,wait_on_rate_limit=True)

        except Exception as e:
            print(e)
            messagebox.showerror('Error', 'Authentication Failed !')
            return

        try:
            #getting tweets
            tweets=api.user_timeline(screen_name=user, count=100, lang='en', tweet_mode='extended')
            if tweets==[]:
                messagebox.showerror('Twitter Error: Account does not exists', 'Please enter correct Twitter User Name')
                return
        except Exception as e:
            print(e)
            messagebox.showerror('Error', 'Cannot load tweets for this user !')
            return

        df=pd.DataFrame( [ i.full_text for i in tweets], columns=['Tweets'])

        def clean_tweets(text):
            text = re.sub(r'@[A-Za-z0-9]+:', '', text)
            text = re.sub(r'#', '', text)
            text = re.sub(r'RT[\s]+', '', text)
            text = re.sub(r'https?:\/\/\S+', '', text)
            return text

        df['Tweets'] = df['Tweets'].apply(clean_tweets)

        def subjective(s):
            p = TextBlob(s).sentiment.subjectivity
            return p

        def polar(s):
            p = TextBlob(s).sentiment.polarity
            if p < 0:
                return 'Negative'
            elif p == 0:
                return 'Neutral'
            else:
                return 'Positive'

        def polar_values(s):
            p =  TextBlob(s).sentiment.polarity
            return p


        df['Polarity'] = df['Tweets'].apply(polar)
        df['Subjective_values'] = df['Tweets'].apply(subjective)
        df['Polar_values'] = df['Tweets'].apply(polar_values)

        reviews.clear()
        for i in range(df.shape[0]):
            reviews[ df['Polarity'][i] ].append( df['Tweets'][i] )



        ptweets = df[ df['Polarity']=='Positive']
        ptweets = ptweets['Tweets']
        negtweets = df[df['Polarity'] == 'Negative']
        negtweets = negtweets['Tweets']
        ntweets = df[df['Polarity'] == 'Neutral']
        ntweets = ntweets['Tweets']

        nc = round( (negtweets.shape[0] / df.shape[0])*100, 1 )
        np = round( (ptweets.shape[0] / df.shape[0])*100, 1 )
        nn = round( (ntweets.shape[0] / df.shape[0])*100, 1 )
        plt.style.use('fivethirtyeight')

        figure_bar=plt.Figure(figsize=(4, 4))
        a_bar=figure_bar.add_subplot(111)
        a_bar.pie([np, nc, nn], labels=['Positive', 'Negative', 'Neutral'], explode=[0.2,0,0],
                  shadow=True, autopct='%1.1f%%')

        figure_scatter=plt.Figure(figsize=(4, 4))
        a_scatter=figure_scatter.add_subplot(111)
        for i in range(0, df.shape[0]):
            a_scatter.scatter(df['Polar_values'][i], df['Subjective_values'][i], color='Blue')
        figure_scatter.suptitle('Scatter Graph')

        chart_bar=FigureCanvasTkAgg(figure_bar,root)
        chart_scatter=FigureCanvasTkAgg(figure_scatter,root)

        chart_bar.get_tk_widget().place(x=30, y=200)
        chart_scatter.get_tk_widget().place(x=500, y=200)

        self.create_text(475, 400, text='Subjectivity', fill='white', angle=90, tag='subjectivity', font='Abc 15 bold')
        self.create_text(650, 630, text='Polarity', fill='white', tag='polarity', font='Abc 15 bold')
        l=[1,2,3,4,5]
        self.create_rectangle(950, 220, 1200, 250, fill="yellow", outline="red", tag='btrpr')
        self.create_text(1060, 235, text="Positive Tweets", fill='green', font='Abc 15 bold', tag='bttpr')
        self.tag_bind(self.find_withtag('btrpr'), "<Button-1>", self.showp)
        self.tag_bind(self.find_withtag('bttpr'), "<Button-1>", self.showp)

        self.create_rectangle(950, 420, 1200, 450, fill="yellow", outline="red", tag='btrnr')
        self.create_text(1060, 435, text="Negative Tweets", fill='green', font='Abc 15 bold', tag='bttnr')
        self.tag_bind(self.find_withtag('btrnr'), "<Button-1>", self.shown)
        self.tag_bind(self.find_withtag('bttnr'), "<Button-1>", self.shown)


obj=Review()
obj.pack()
root.mainloop()