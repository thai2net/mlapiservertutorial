from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from .serializers import UserSerializer, GroupSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
import json
import math
from django.http import HttpResponse, HttpResponseRedirect
import os

#import data science libraries
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import pandas as pd
import numpy as np
from sklearn import model_selection
from sklearn.linear_model import LogisticRegression
import pickle
import json

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer

class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

class LinearRegressPredict(APIView):

    def get(self, request, *args, **kw):
        print("calling get method")
        # Any URL parameters get passed in **kw
        result = {"result": "model trained"}
        # model training ----------------------------------------------
        filename = './finalized_model.sav'
        print("import data")
        USAhousing = pd.read_csv('USA_Housing.csv')
        X = USAhousing[['Avg. Area Income', 'Avg. Area House Age', 'Avg. Area Number of Rooms',
                        'Avg. Area Number of Bedrooms', 'Area Population']]
        y = USAhousing['Price']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.4, random_state=101)
        print("Start Training Process...")
        lm = LinearRegression()
        lm.fit(X_train, y_train)
        pickle.dump(lm, open(filename, 'wb'))
        response = Response(result, status=status.HTTP_200_OK)
        return response

    def post(self, request, *args, **kw):
        msg_body = json.loads(request.body)
        # TODO check data validity before publish mqtt message to Azure
        print("msg_body: {}".format(msg_body))
        print(type(msg_body))
        X_test = pd.DataFrame.from_dict(msg_body, orient='index')
        print(X_test.T)
        filename = './finalized_model.sav'
        loaded_model = pickle.load(open(filename, 'rb'))
        pred = loaded_model.predict(X_test.T)
        print(pred)
        result = {"result": pred}
        response = Response(result, status=status.HTTP_200_OK)
        return response


