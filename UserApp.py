from kivy.app import App

from kivy.graphics import Ellipse, Color, Rectangle
from kivy.vector import Vector

from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window

from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput

from random import random
from math import atan2, sqrt, pow, degrees, sin, cos, radians

import plyer
import mysql.connector
from mysql.connector import Error

Window.size = (580,600)

pieslices = []

class MainWindow(GridLayout):
    data = {'slept':1,
            'awake':0}

    def __init__(self, **kwargs):
        super(MainWindow, self).__init__(**kwargs)
        gl = GridLayout(height=self.minimum_height, padding=(10,10))
        gl.cols = 3
        gl.rows = 3

        date = TextInput(input_type = 'number',
                         pos_hint={'x': .2, 'y': .2},
                         size_hint_y=None,
                         height=30)
        gl.add_widget(date)

        month = TextInput(input_type = 'number',
                         pos_hint={'x': .2, 'y': .2},
                         size_hint_y=None,
                         height=30)
        gl.add_widget(month)

        year = TextInput(input_type = 'number',
                         pos_hint={'x': .2, 'y': .2},
                         size_hint_y=None,
                         height=30)
        gl.add_widget(year)

        gl.add_widget(Label(text='Date', size_hint_y=None, height=30))
        gl.add_widget(Label(text='Month',size_hint_y=None, height=30))
        gl.add_widget(Label(text='Year', size_hint_y=None, height=30))

        def getdata(but):
            dt = str(year.text) + '-' + str(month.text) + '-' + str(date.text)
            connection = ''
            cursor = ''
            try:
                connection = mysql.connector.connect(host='localhost',
                                                     database='iot',
                                                     user='root',
                                                     password='')
                if connection.is_connected():
                    db_Info = connection.get_server_info()
                    print("Connected to MySQL Server version ", db_Info)
                    cursor = connection.cursor(buffered=True)
                    cursor.execute("select database();")
                    record = cursor.fetchone()
                    print("You're connected to database: ", record)
                    try:
                        cursor.execute("SELECT count(d_date) FROM sensor_data where d_date=cast('"+dt+"' as date) and t_time > cast('02:00:00' as time)")
                        self.data['awake'] = 5*cursor.fetchone()[0]
                        print(self.data)
                        self.data['slept'] = 36000-self.data['awake']
                    except Error as e:
                        print('Error : ', e)
            except Error as e:
                print("Error while connecting to MySQL", e)
            finally:
                try:
                    piegl.remove_widget(self.chart)
                    self.chart = PieChart(data=self.data, position=position, size=size, legend_enable=True)
                    piegl.add_widget(self.chart)
                    if connection.is_connected():
                        cursor.close()
                        connection.close()
                        print("MySQL connection is closed")
                except Error as e:
                    print("Failed to close : ", e)

        but = Button(text='Fetch', on_press = getdata, size_hint_y=None, height=30)
        gl.add_widget(but)

        piegl = GridLayout(height=self.minimum_height)
        piegl.cols = 2
        piegl.rows = 2

        self.cols = 1
        self.rows = 5
        
        # in_data can take form of either formats below
        
        position = (140, 140)
        size = (200, 200)
        self.chart = PieChart(data=self.data, position=position, size=size, legend_enable=True)
        piegl.add_widget(self.chart)

        self.add_widget(gl)
        self.add_widget(piegl)
        self.add_widget(GridLayout())
        self.add_widget(GridLayout())
        self.add_widget(GridLayout())


class PieChart(GridLayout):
    def __init__(self, data, position, size, legend_enable=True, **kwargs):
        super(PieChart, self).__init__(**kwargs)

        # main layout parameters
        self.position = position
        self.size_mine = size
        self.col_default_width = 100
        self.data = {}
        self.cols = 2
        self.rows = 1
        self.col_force_default = True
        self.col_default_width = 50
        self.row_force_default = True
        self.row_default_height = 100
        self.size_hint_y = None
        self.size = (600, 450)
        self.temp = []

        for key, value in data.items():
            if type(value) is int:
                percentage = (value / float(sum(data.values())) * 100)
                color = [random(), random(), random(), 1]
                self.data[key] = [value, percentage, color]

            elif type(value) is tuple:
                vals = []
                for l in data.values():
                    vals.append(l[0])
                percentage = (value[0] / float(sum(vals)) * 100)
                color = value[1]
                self.data[key] = [value[0], percentage, color]

        self.pie = Pie(self.data, self.position, self.size_mine)
        self.add_widget(self.pie)

        if legend_enable:
            self.legend = LegendTree(self.data, self.position, self.size_mine)
            self.add_widget(self.legend)

        self.bind(size=self._update_pie, pos=self._update_pie)

        # yellow background to check widgets size and position
        # with self.canvas:
        #    Rectangle(pos=self.pos, size=self.size, color=Color(1, 1, 0, 0.5))

    def _update_pie(self, instance, value):
        self.legend.pos = (instance.parent.pos[0], instance.parent.pos[1])
        self.pie.pos = (instance.pos[0], instance.pos[1])


class LegendTree(GridLayout):
    def __init__(self, data, position, size, **kwargs):
        super(LegendTree, self).__init__(**kwargs)

        # Legend layout parameters.
        # Initial rows is 1, then for each next data entry new one is added.
        self.cols = 1
        self.rows = 1
        self.position = position
        self.size = size
        self.row_default_height = 50
        self.spacing = 5

        count = 0
        for key, value in data.items():
            percentage = value[1]
            color = value[2]
            # add legend (rectangle and text)
            self.legend = Legend(pos=(self.position[0], self.position[1] - count * self.size[1] * 0.15),
                                 size=self.size,
                                 color=color,
                                 name=key,
                                 value=percentage)
            self.add_widget(self.legend)
            self.rows += 1
            count += 1

        self.bind(size=self._update_rect, pos=self._update_rect)

    def _update_rect(self, instance, value):
        self.legend.pos = (instance.parent.pos[0], instance.parent.pos[1])
        self.pos = (instance.parent.pos[0] + 260, instance.parent.pos[1])


# Class for creating Legend
class Legend(FloatLayout):
    def __init__(self, pos, size, color, name, value, **kwargs):
        super(Legend, self).__init__(**kwargs)
        self.cols = 2
        self.rows = 1
        self.size_hint_x = 200
        self.size_hint_y = 50
        self.name = name
        with self.canvas.before:
            Color(*color)
            self.rect = Rectangle(pos=(pos[0] + size[0] * 1.3, pos[1] + size[1] * 0.9),
                                  size=(size[0] * 0.1, size[1] * 0.1))
            self.label = Label(text=str("%.2f" % value + "% - " + name),
                               pos=(pos[0] + size[0] * 1.3 + size[0]*0.5, pos[1] + size[1] * 0.9 - 30),
                               halign='left',
                               text_size=(size[1], size[1] * 0.1))

        self.bind(size=self._update_rect, pos=self._update_rect)

    def _update_rect(self, instance, value):
        self.rect.pos = (instance.pos[0] + 100, instance.pos[1] + 100)
        self.label.pos = (instance.pos[0] + 220, instance.pos[1] + 65)


class Pie(FloatLayout):
    def __init__(self, data, position, size, **kwargs):
        super(Pie, self).__init__(**kwargs)
        self.position = position
        self.size = size
        angle_start = 0
        count = 0
        self.temp = []
        for key, value in data.items():
            percentage = value[1]
            angle_end = angle_start + 3.6 * percentage
            color = value[2]
            # add part of Pie
            self.temp.append(PieSlice(pos=self.position, size=self.size,
                                      angle_start=angle_start,
                                      angle_end=angle_end, color=color, name=key))
            self.add_widget(self.temp[count])
            angle_start = angle_end
            count += 1
        self.bind(size=self._update_temp, pos=self._update_temp)
        global pieslices
        pieslices = self.temp

    def _update_temp(self, instance, value):
        for i in self.temp:
            i.pos = (instance.parent.pos[0] + 55, instance.parent.pos[1] + 60)


# Class for making one part of Pie
# Main functions for handling move out/in and click inside area recognition
class PieSlice(FloatLayout):
    def __init__(self, pos, color, size, angle_start, angle_end, name, **kwargs):
        super(PieSlice, self).__init__(**kwargs)
        self.moved = False
        self.angle = 0
        self.name = name
        with self.canvas.before:
            Color(*color)
            self.slice = Ellipse(pos=pos, size=size,
                                 angle_start=angle_start,
                                 angle_end=angle_end)
        self.bind(size=self._update_slice, pos=self._update_slice)

    def _update_slice(self, instance, value):
        self.slice.pos = (instance.pos[0], instance.pos[1])

    # Function for moving part of pie outside of circle
    def move_pie_out(self):
        ang = self.slice.angle_start + (self.slice.angle_end - self.slice.angle_start) / 2
        vector_x = cos(radians(ang - 90)) * 50
        vector_y = sin(radians(ang + 90)) * 50
        if not self.moved:
            self.slice.pos = Vector(vector_x, vector_y) + self.slice.pos
            self.moved = True
        else:
            self.slice.pos = Vector(-vector_x, -vector_y) + self.slice.pos
            self.moved = False

    # Function for moving part of pie inside of circle
    def move_pie_in(self):
        ang = self.slice.angle_start + (self.slice.angle_end - self.slice.angle_start) / 2
        vector_x = cos(radians(ang - 90)) * 50
        vector_y = sin(radians(ang + 90)) * 50
        if self.moved:
            self.slice.pos = Vector(-vector_x, -vector_y) + self.slice.pos
            self.moved = False

    # Click handler on Pie Part
    # If click is inside Pie Part, move it out
    def on_touch_down(self, touch):
        if self.is_inside_pie(*touch.pos):
            if self.moved==True:
                self.move_pie_out()
                return
            global pieslices
            for p in pieslices:
                p.move_pie_in()
            self.move_pie_out()

    # Function for checking if click is inside Pie Slice
    def is_inside_pie(self, *touch_pos):
        y_pos = touch_pos[1] - self.slice.pos[1] - self.slice.size[1] / 2
        x_pos = touch_pos[0] - self.slice.pos[0] - self.slice.size[0] / 2
        angle = degrees(1.5707963268 - atan2(y_pos, x_pos))
        if angle < 0:
            angle += 360
        self.angle = angle
        radius = sqrt(pow(x_pos, 2) + pow(y_pos, 2))
        if self.slice.angle_start < angle < self.slice.angle_end:
            return radius < self.slice.size[0] / 2


class PieChartApp(App):
    def build(self):
        return MainWindow()


if __name__ == '__main__':
    PieChartApp().run()