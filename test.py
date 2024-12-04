from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.options import Options

with open("log/query.txt", "r", encoding="utf-8") as f:
    content = f.read()
    print(repr(content))
