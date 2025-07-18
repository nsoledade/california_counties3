
import geopandas as gpd
import numpy as np
import streamlit as st
import pandas as pd
import pydeck as pdk

from joblib import load

from notebooks.src.config import DADOS_GEO_MEDIAN, DADOS_LIMPOS, MODELO_FINAL

@st.cache_data
def carregar_dados_limpos():
    return pd.read_parquet(DADOS_LIMPOS)

@st.cache_data
def carregar_dados_geo():
    return gpd.read_parquet(DADOS_GEO_MEDIAN)

@st.cache_resource
def carregar_modelo():
    return load(MODELO_FINAL)

df = carregar_dados_limpos()
gdf_geo = carregar_dados_geo()
modelo = carregar_modelo()

st.title("Previsão de preços de imóveis")

condados = list(gdf_geo["name"].sort_values())

coluna1, coluna2 = st.columns(2)

with coluna1:

    selecionar_condado = st.selectbox("Condado", condados)
    
    longitude = gdf_geo.query("name == @selecionar_condado")["longitude"].values
    latitude = gdf_geo.query("name == @selecionar_condado")["latitude"].values
    
    housing_median_age = st.number_input("Idade do imóvel", value=10, min_value=1, max_value=50)
    
    total_rooms = gdf_geo.query("name == @selecionar_condado")["total_rooms"].values
    total_bedrooms = gdf_geo.query("name == @selecionar_condado")["total_bedrooms"].values
    population = gdf_geo.query("name == @selecionar_condado")["population"].values
    households = gdf_geo.query("name == @selecionar_condado")["households"].values
    
    median_income = st.slider("Renda média (milhares de US$)", 5.0, 100.0, 45.0, 5.0)
    
    ocean_proximity = gdf_geo.query("name == @selecionar_condado")["ocean_proximity"].values
    
    bins_income = [0, 1.5, 3, 4.5, 6, np.inf]
    median_income_cat = np.digitize(median_income/10, bins=bins_income)
    
    
    
    rooms_per_household = gdf_geo.query("name == @selecionar_condado")["rooms_per_household"].values
    bedrooms_per_room = gdf_geo.query("name == @selecionar_condado")["bedrooms_per_room"].values
    population_per_household = gdf_geo.query("name == @selecionar_condado")["population_per_household"].values
    
    
    entrada_modelo = {
        "longitude": longitude,
        "latitude": latitude,
        "housing_median_age": housing_median_age,
        "total_rooms": total_rooms,
        "total_bedrooms": total_bedrooms,
        "population": population,
        "households": households,
        "median_income": median_income/10,
        "ocean_proximity": ocean_proximity,
        "median_income_cat": median_income_cat,
        "rooms_per_household": rooms_per_household,
        "bedrooms_per_room": bedrooms_per_room,
        "population_per_household": population_per_household,
    
    }
    
    df_entrada_modelo = pd.DataFrame(entrada_modelo, index=[0])
    
    botao_previsao = st.button("Prever preço")
    
    if botao_previsao:
        preco = modelo.predict(df_entrada_modelo)
        st.write(f"Preço previsto: US$ {preco[0][0]:.2f}")

with coluna2:
    view_state = pdk.ViewState(
        latitude=float(latitude[0]),
        longitude=float(longitude[0]),
        zoom=5,
        min_zoon=5,
        max_zoom=15,
   )

    mapa = pdk.Deck(
        initial_view_state=view_state,
        map_style="light"
        
   )

    st.pydeck_chart(mapa)



                    

        
    
        
        
    
        


