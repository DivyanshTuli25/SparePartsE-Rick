import streamlit as st
import pandas as pd
from PIL import Image

# Define the Excel file paths
stock_file_path = 'Stock3.xlsx'
parts_file_path = 'Stock3.xlsx'


# Function to load parts requirements from the Excel file
def load_parts_requirements():
    df = pd.read_excel(parts_file_path)
    model_parts_requirements = {}
    for model in df.columns[3:]:
        model_parts_requirements[model] = df.set_index('Parts')[model].to_dict()
    return model_parts_requirements


# Function to load stock data from the Excel file
def load_stock_data():
    try:
        df = pd.read_excel(stock_file_path)
    except FileNotFoundError:
        parts = {
            "Motor": 10,
            "Battery": 10,
            "Controller": 10,
            "Throttle": 10,
            "Brake": 10,
            "Frame": 10,
            "Wheels": 10,
            "Charger": 10,
            "Seat": 10,
            "Suspension": 10
        }
        df = pd.DataFrame(parts.items(), columns=['Parts', 'Stock'])
        df.to_excel(stock_file_path, index=False)
    return df


# Function to save stock data to the Excel file
def save_stock_data(df):
    df.to_excel(stock_file_path, index=False)


# Function to calculate how many models can be made with the current stock
def calculate_producible(df, parts_requirements):
    for model, requirements in parts_requirements.items():
        # Use the existing column if it exists, otherwise create it
        column_name = f"{model}s that can be made"
        if column_name not in df.columns:
            df[column_name] = 0

        for index, row in df.iterrows():
            part = row['Parts']
            stock_qty = int(row['Stock'])  # Cast to int
            if part in requirements:
                qty = int(requirements[part])  # Cast to int
                producible = stock_qty // qty if qty > 0 else 0
                df.at[index, column_name] = producible
    return df


# Function to decrement stock for custom number of rickshaws, allowing negative values
def decrement_stock(df, num_rickshaws, model, parts_requirements):
    requirements = parts_requirements[model]
    for part, qty in requirements.items():
        df.loc[df['Parts'] == part, 'Stock'] -= qty * num_rickshaws
    return df, True


# Function to increment stock
def increment_stock(df, selected_parts, quantity):
    if "All stock" in selected_parts:
        df['Stock'] = df['Stock'].apply(lambda x: int(x) + int(quantity))  # Cast to int
    else:
        for part in selected_parts:
            df.loc[df['Parts'] == part, 'Stock'] = int(df.loc[df['Parts'] == part, 'Stock']) + int(quantity)
    return df


# Function to decrement custom stock, allowing negative values
def decrement_custom_stock(df, selected_parts, quantity):
    if "All stock" in selected_parts:
        df['Stock'] = df['Stock'].apply(lambda x: int(x) - int(quantity))  # Cast to int
    else:
        for part in selected_parts:
            df.loc[df['Parts'] == part, 'Stock'] = int(df.loc[df['Parts'] == part, 'Stock']) - int(quantity)
    return df, True


# Load parts requirements and stock data
parts_requirements = load_parts_requirements()
df = load_stock_data()

# Calculate producible quantities
df = calculate_producible(df, parts_requirements)

# Streamlit app
st.set_page_config(page_title="Electric Rickshaw Spare Parts Management", page_icon=":rickshaw:", layout="wide")

# Custom CSS styling
st.markdown("""
    <style>
    .main {
        background-color: #85C227;
    }
    h1 {
        color: #007bff;
    }
    h2, h3 {
        color: #6c757d;
    }
    .stButton>button {
        background-color: #007bff;
        color: white;
        border-radius: 5px;
        font-size: 16px;
        padding: 10px 20px;
    }
    .stButton>button:hover {
        background-color: #0056b3;
        color: white;
    }
    .stNumberInput>div>div>input {
        border-radius: 5px;
        border: 2px solid #007bff;
    }
    .stDataFrame {
        border: 2px solid #007bff;
        border-radius: 10px;
        padding: 10px;
    }
    </style>
""", unsafe_allow_html=True)


# Function to apply stock filter
def apply_stock_filter(df_print, stock_filter):
    # Filter the dataframe based on stock range
    if stock_filter == 'Below 0':
        df_filtered = df_print[df_print['Stock'] < 0]
    elif stock_filter == '0-100':
        df_filtered = df_print[df_print['E-Rickshaws that can be made'] <= 100]
    elif stock_filter == '101-200':
        df_filtered = df_print[
            (df_print['E-Rickshaws that can be made'] > 100) & (df_print['E-Rickshaws that can be made'] <= 200)]
    elif stock_filter == '200+':
        df_filtered = df_print[df_print['E-Rickshaws that can be made'] > 200]
    else:
        df_filtered = df_print
    return df_filtered


# Convert columns to integers
df["Stock"] = df["Stock"].astype(int)
df["E-Rickshaws that can be made"] = df["Stock"] // df["Required per vehicle"].astype(int)
df_print = df[
    ["Parts", "Stock", "Required per vehicle", "E-Rickshaws that can be made", "Round Model", "Loader", "Flexi Model"]]


# Apply conditional formatting
def highlight_rows(val):
    if val <= 0:
        return 'background-color: #8B0000; color: white'  # Dark red for 0 or negative stock
    elif 1 <= val <= 100:
        return 'background-color: #FF0000'  # Red for low stock
    elif 101 <= val <= 200:
        return 'background-color: #FFA500'  # Orange for medium stock
    else:
        return 'background-color: #90EE90'  # Green for high stock


# Header section
st.image("https://www.bybyerickshaw.com/images/logo.png", width=200)
st.title("Electric Rickshaw Spare Parts Management")

# Stock filter
stock_filter = st.radio(
    "Filter Parts by Stock Range",
    ('All', 'Below 0', '0-100', '101-200', '200+')
)

# Apply the filter initially
df_filtered = apply_stock_filter(df_print, stock_filter)

# Display current stock with color formatting
st.subheader("Current Stock of Parts")
st.dataframe(df_filtered.style.applymap(highlight_rows, subset=["E-Rickshaws that can be made"]))

# Section to decrement stock for custom number of rickshaws
st.subheader("Record New Rickshaws")
model = st.selectbox('Select Rickshaw Model', parts_requirements.keys(), key='model')
num_rickshaws = st.number_input('Number of Rickshaws to Record', min_value=1, step=1, key='num_rickshaws')
if st.button('Record Rickshaws Made'):
    df, success = decrement_stock(df, num_rickshaws, model, parts_requirements)
    if success:
        save_stock_data(df)
        df = calculate_producible(df, parts_requirements)
        df_print = df[
            ["Parts", "Stock", "Required per vehicle", "E-Rickshaws that can be made", "Round Model", "Loader",
             "Flexi Model"]]
        df_filtered = apply_stock_filter(df_print, stock_filter)  # Reapply filter to updated data
        st.success(f"Stock updated successfully for {num_rickshaws} rickshaw(s) of {model}!")
        st.dataframe(df_filtered.style.applymap(highlight_rows, subset=["E-Rickshaws that can be made"]))

# Section to increment stock
st.subheader("Increment Stock of Parts")
parts_list = ["All stock"] + df['Parts'].tolist()
increment_parts = st.multiselect('Select Parts to Increment', parts_list)
quantity_increment = st.number_input('Quantity to Add', min_value=1, step=1, key='increment_qty')
if st.button('Increment Stock'):
    df = increment_stock(df, increment_parts, quantity_increment)
    save_stock_data(df)
    df = calculate_producible(df, parts_requirements)
    df_print = df[["Parts", "Stock", "Required per vehicle", "E-Rickshaws that can be made", "Round Model", "Loader",
                   "Flexi Model"]]
    df_filtered = apply_stock_filter(df_print, stock_filter)  # Reapply filter to updated data
    st.success("Stock incremented successfully!")
    st.dataframe(df_filtered.style.applymap(highlight_rows, subset=["E-Rickshaws that can be made"]))

# Section to decrement custom stock
st.subheader("Decrement Stock of Parts")
decrement_parts = st.multiselect('Select Parts to Decrement', parts_list)
quantity_decrement = st.number_input('Quantity to Subtract', min_value=1, step=1, key='decrement_qty')
if st.button('Decrement Stock'):
    df, success = decrement_custom_stock(df, decrement_parts, quantity_decrement)
    if success:
        save_stock_data(df)
        df = calculate_producible(df, parts_requirements)
        df_print = df[
            ["Parts", "Stock", "Required per vehicle", "E-Rickshaws that can be made", "Round Model", "Loader",
             "Flexi Model"]]
        df_filtered = apply_stock_filter(df_print, stock_filter)  # Reapply filter to updated data
        st.success("Stock decremented successfully!")
        st.dataframe(df_filtered.style.applymap(highlight_rows, subset=["E-Rickshaws that can be made"]))
