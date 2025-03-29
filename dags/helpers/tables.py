from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class City(Base):
    __tablename__ = "cities"
    
    id = Column('id', Integer, primary_key=True)
    city = Column('city', String, nullable=False)
    country = Column('country', String, nullable=False)
    longitude = Column('longitude', Float, nullable=False)
    latitude = Column('latitude', Float, nullable=False)
    timezone = Column('timezone', Integer, nullable=False)
    
class Weather(Base):
    __tablename__ = "weather"
    
    id = Column('id', Integer, primary_key=True)
    city = Column('city', String, nullable=False)
    country = Column('country', String, nullable=False)
    base = Column('base', String, nullable=False)
    description = Column('description', String, nullable=False)
    time = Column('time', String, nullable=False)
    temperature = Column('temperature', Float, nullable=False)
    min_temp = Column('min_temp', Float, nullable=False)
    max_temp = Column('max_temp', Float, nullable=False)
    pressure = Column('pressure', Integer, nullable=False)
    humidity = Column('humidity', Integer, nullable=False)
    visibility = Column('visibility', Integer, nullable=False)
    wind_speed = Column('wind_speed', Float, nullable=False)
    wind_deg = Column('wind_deg', Integer, nullable=False)

class Pollution(Base):
    __tablename__ = "pollution"
    
    id = Column('id', Integer, primary_key=True)
    city = Column('city', String, nullable=False)
    country = Column('country', String, nullable=False)
    time = Column('time', String, nullable=False)
    aqi = Column('aqi', Integer, nullable=False)
    co = Column('co', Float, nullable=False)
    no = Column('no', Float, nullable=False)
    no2 = Column('no2', Float, nullable=False)
    o3 = Column('o3', Float, nullable=False)
    so2 = Column('so2', Float, nullable=False)
    pm2_5 = Column('pm2_5', Float, nullable=False)
    pm10 = Column('pm10', Float, nullable=False)
    nh3 = Column('nh3', Float, nullable=False)