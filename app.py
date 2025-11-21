import streamlit as st
import pandas as pd
import plotly.express as px
import streamlit as st
import plotly.graph_objects as go
import numpy as np




@st.cache_data
def load_data():
    return pd.read_csv('data/cleaned_data.csv')
df = load_data()
st.title("Tunisian House Prices Explorer")
st.caption("Created by Wissem Kooli – Industrial engineering student")
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

st.header("Introduction:")
st.markdown("<br>", unsafe_allow_html=True)
st.markdown(
    """
    This project explores house prices in Tunisia using a unique dataset scraped from
    [Mubawab.tn](https://www.mubawab.tn/) in November 2025.
    The data contains over **2,800 residential property listings**.
    This hands-on project not only provides a current snapshot of the country’s real estate market,
    but also equips both data enthusiasts and potential buyers with actionable insights.
    """
)
st.markdown("<br>", unsafe_allow_html=True)
st.dataframe(df, height=400)
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)


# Filter data with valid coordinates
map_df = df[['latitude', 'longitude', 'price', 'city', 'title', 'num_rooms']].dropna(subset=['latitude', 'longitude'])


fig = px.scatter_map(
    map_df,
    lat='latitude',
    lon='longitude',
    color='price',
    hover_name='title',
    hover_data={
        'city': True,
        'price': ':,.0f TND',
        'num_rooms': True,
        'latitude': False,
        'longitude': False
    },
    zoom=6,
    height=600,
    color_continuous_scale=[[0, 'green'], [0.3, 'yellow'], [1, 'red']],
    title='House Prices Across Tunisia'
)

fig.update_traces(
    marker=dict(size=6)
)

fig.update_layout(
    map=dict(
        style='open-street-map',
        center=dict(lat=map_df['latitude'].mean(), lon=map_df['longitude'].mean())
    ),
    margin={"r":0,"t":40,"l":0,"b":0},
    coloraxis_colorbar=dict(
        title="Price (TND)",
        tickformat=",",
    )
)

st.plotly_chart(fig, use_container_width=True,key='4')

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)





st.header("Price Distribution Analysis")

price_data = df[['price']].dropna()
fig1 = px.histogram(
    price_data,
    x='price',
    nbins=50,
    labels={'price': 'Price (TND)', 'count': 'Number of Properties'},
    title='Distribution of House Prices in Tunisia',
    color_discrete_sequence=['#1f77b4'],
    marginal='box'  # Add box plot
)

fig1.update_layout(
    height=400,
    showlegend=False,
    xaxis_tickformat=',',
    yaxis_tickformat=','
)
st.plotly_chart(fig1, use_container_width=True,key=5)








st.header("Total Area vs Price Correlation")

scatter_data = df[['total_area', 'price', 'type_of_good', 'city']].dropna()

fig7 = px.scatter(
    scatter_data,
    x='total_area',
    y='price',
    color='type_of_good',
    size='total_area',
    hover_data=['city'],
    trendline='ols',  # Add regression line
    labels={
        'total_area': 'Total Area (m²)',
        'price': 'Price (TND)',
        'type_of_good': 'Property Type'
    },
    title='Price vs Total Area (with trend)',
    height=500,
    color_discrete_sequence=px.colors.qualitative.Set1
)

fig7.update_traces(marker=dict(size=6, opacity=0.6))
fig7.update_layout(
    xaxis_tickformat=',',
    yaxis_tickformat=',',
)
st.plotly_chart(fig7, use_container_width=True,key='6')

# Calculate correlation
corr_coeff = scatter_data['total_area'].corr(scatter_data['price'])

# Show basic statistics
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Average Price", f"{scatter_data['price'].mean():,.0f} TND")
with col2:
    st.metric("Average Area", f"{scatter_data['total_area'].mean():.0f} m²")
with col3:
    st.metric("Average Price per m²", f"{(scatter_data['price']/scatter_data['total_area']).mean():,.0f} TND")


st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)




# Average Price by Region
st.header("Average Price by Region")

price_df = df[['region', 'price']].dropna()

# Group by region and calculate average, get all regions (no head())
region_avg = price_df.groupby('region', as_index=False)['price'].mean().sort_values('price', ascending=False)

fig = px.bar(
    region_avg,
    x='region',
    y='price',
    labels={
        'region': 'Region',
        'price': 'Average Price (TND)'
    },
    title='All Regions by Average Price',
    height=600,
    color='price',
    color_continuous_scale=[[0, 'green'], [0.5, 'yellow'], [1, 'red']]
)

fig.update_layout(
    xaxis_title='Region',
    yaxis_title='Price (TND)',
    yaxis_tickformat=',',
    xaxis_tickangle=-45,
    xaxis=dict(tickmode='array', tickvals=region_avg['region']),
    margin=dict(b=150)  # More space for x axis labels
)

# Use container_width to maximize chart width, but let users scroll in the figure if needed
st.plotly_chart(fig, use_container_width=True, key='region_bar')


st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# Average Price per m² by Region (Top 20)
st.header("Average Price per m² by Region")

price_per_m2_df = df[['region', 'price', 'total_area']].dropna()
price_per_m2_df['price_per_m2'] = price_per_m2_df['price'] / price_per_m2_df['total_area']

# Group by city and calculate average, get top 20
city_avg = price_per_m2_df.groupby('region')['price_per_m2'].mean().sort_values(ascending=False).head(20).reset_index()

fig = px.bar(
    city_avg,
    x='region',
    y='price_per_m2',
    labels={
        'city': 'Region',
        'price_per_m2': 'Average Price per m² (TND)'
    },
    title='Top 20 Regions by Average Price per m²',
    height=500,
    color='price_per_m2',
    color_continuous_scale=[[0, 'green'], [0.5, 'yellow'], [1, 'red']]
)

fig.update_layout(
    xaxis_title='Region',
    yaxis_title='Price per m² (TND)',
    yaxis_tickformat=',',
    xaxis_tickangle=-45
)

st.plotly_chart(fig, use_container_width=True,key='7')

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

st.header("Impact of Amenities on Price")

# Get all boolean columns (amenities)
boolean_cols = [
    'Antenne parabolique', 'Ascenseur', 'Chambre rangement', 'Chauffage central',
    'Cheminée', 'Climatisation', 'Concierge', 'Cuisine équipée', 'Double vitrage',
    'Entre-seul', 'Four', 'Garage', 'Jardin', 'Machine à laver', 'Meublé',
    'Micro-ondes', 'Piscine', 'Porte blindée', 'Réfrigérateur', 'Salon européen',
    'Sécurité', 'Terrasse', 'Vue sur les montagnes', 'Vue sur mer'
]

# Calculate price impact for each amenity
amenity_impact = []
amenity_names = []

for amenity in boolean_cols:
    if amenity in df.columns:
        # Get average price when amenity is True vs False
        price_with = df[df[amenity] == True]['price'].mean()
        price_without = df[df[amenity] == False]['price'].mean()
        
        # Calculate impact (premium)
        if not pd.isna(price_with) and not pd.isna(price_without):
            impact = price_with - price_without
            amenity_impact.append(impact)
            amenity_names.append(amenity)

# Create dataframe
impact_df = pd.DataFrame({
    'Amenity': amenity_names,
    'Price Impact (TND)': amenity_impact
}).sort_values('Price Impact (TND)', ascending=True)



# CORRELATION HEATMAP

# Calculate correlation between amenities and price
corr_data = []
for amenity in boolean_cols:
    if amenity in df.columns:
        corr = df[amenity].astype(int).corr(df['price'])
        corr_data.append({
            'Amenity': amenity,
            'Correlation with Price': corr
        })

corr_df = pd.DataFrame(corr_data).sort_values('Correlation with Price', ascending=False)

# Create vertical bar chart
fig2 = px.bar(
    corr_df,
    x='Amenity',
    y='Correlation with Price',
    color='Correlation with Price',
    color_continuous_scale='RdBu',
    labels={'Correlation with Price': 'Correlation Coefficient'},
    title='Amenity Correlation with Price',
    height=500
)

fig2.update_layout(
    xaxis_tickangle=-45,
    showlegend=False
)
st.plotly_chart(fig2, use_container_width=True,key='2')

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)
# 2D HEATMAP
st.subheader("2D Amenity Impact Analysis")
heatmap_data = []
amenities_sample = amenity_names[:15]  # Top 15 for clarity

for amenity in amenities_sample:
    if amenity in df.columns:
        price_with = df[df[amenity] == True]['price'].mean()
        price_without = df[df[amenity] == False]['price'].mean()
        count_with = (df[amenity] == True).sum()
        count_without = (df[amenity] == False).sum()
        
        heatmap_data.append({
            'Amenity': amenity,
            'With Amenity': price_with,
            'Without Amenity': price_without
        })

heatmap_df = pd.DataFrame(heatmap_data).set_index('Amenity')

# Create heatmap
fig3 = go.Figure(data=go.Heatmap(
    z=heatmap_df.values,
    x=['With Amenity', 'Without Amenity'],
    y=heatmap_df.index,
    colorscale='RdYlGn',
    text=np.round(heatmap_df.values, 0),
    texttemplate='%{text:,.0f} TND',
    textfont={"size": 10},
    colorbar=dict(title="Average Price (TND)")
))

fig3.update_layout(
    title='Average Price: With vs Without Amenity',
    height=600,
    xaxis_title='',
    yaxis_title='Amenity'
)
st.plotly_chart(fig3, use_container_width=True,key='3')

