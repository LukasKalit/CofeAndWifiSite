from fastapi import FastAPI
#Starlette-WTF
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette_wtf import StarletteForm, CSRFProtectMiddleware, csrf_protect
from wtforms import StringField, SelectField
from wtforms.validators	import DataRequired, URL
#jinja2Templates
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
#csv reader
import pandas as pd
#redirecting
from fastapi.responses import RedirectResponse



app = FastAPI(middleware=[
    Middleware(SessionMiddleware, secret_key="I,m a secret dont look at me ;)"),
    Middleware(CSRFProtectMiddleware, csrf_secret="Why u read me :o")
])

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

#Reading csv file
def download_list_of_cafe():
    df = pd.read_csv('cafe-data.csv', header=None)
    list_of_data = df.values.tolist()
    return list_of_data

#Model for starlette WTForm
class CafeForm(StarletteForm):
    cafe = StringField('Cafe name:', validators=[DataRequired()])
    location_URL = StringField('Cafe Location on Google Maps (URL):', validators=[DataRequired(),URL()])
    open_time = StringField('Opening Time e.g. 6AM:', validators=[DataRequired()])
    close_time = StringField('Closing Time e.g. 5:30PM:', validators=[DataRequired()])
    coffee_rating = SelectField('Coffee Rating:', choices=[('✘', '✘'), ('☕', '☕'), ('☕☕', '☕☕'), ('☕☕☕', '☕☕☕'), ('☕☕☕☕', '☕☕☕☕'), ('☕☕☕☕☕', '☕☕☕☕☕')])
    wifi_rating = SelectField('WiFi Strenght Rating:', choices=[('✘', '✘'), ('💪', '💪'), ('💪💪', '💪💪'), ('💪💪💪', '💪💪💪'), ('💪💪💪💪', '💪💪💪💪'), ('💪💪💪💪💪', '💪💪💪💪💪')])
    power_rating = SelectField('Power Socket Availability:', choices=[('✘', '✘'), ('🔌', '🔌'), ('🔌🔌', '🔌🔌'), ('🔌🔌🔌', '🔌🔌🔌'), ('🔌🔌🔌🔌', '🔌🔌🔌🔌'), ('🔌🔌🔌🔌🔌', '🔌🔌🔌🔌🔌')])




@app.get("/")
async def home(request:Request):
    return templates.TemplateResponse("index.html", {"request": request})


#Secret site to add coffe
@app.get('/add')
async def add_cafe(request:Request):
    form = await CafeForm.from_formdata(request)
    return templates.TemplateResponse("add.html", {"request": request, "form":form})


@app.post('/add')
@csrf_protect
async def add_cafe(request:Request):
    form = await CafeForm.from_formdata(request)
    if await form.validate_on_submit():
        list_data = [[i.data for i in form if i.type != "CSRFTokenField"]]


        #that should look better... but work
        df = pd.DataFrame(list_data, columns=["a","b","c","d","e","f","g"])
        df.to_csv('cafe-data.csv', mode='a',sep=',', index=False, header=False)
        #Post/Redirect/Get (PRG)
        response = RedirectResponse(url='/cafes')
        response.status_code = 302
        return response
    else:
        return templates.TemplateResponse("add.html", {"request": request, "form":form})


@app.get('/cafes')
async def cafes(request:Request):
    cafe_list = download_list_of_cafe()
    return templates.TemplateResponse("cafes.html", {"request": request, "cafes":cafe_list})


