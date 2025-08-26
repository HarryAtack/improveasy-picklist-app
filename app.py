import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import io

# Stock data parsed from your <DOCUMENT> (visible rows; add truncated ones manually or via CSV)
# For full: Export Excel to stock.csv with columns: Supplier,Product Code,Item ID,Description,Category
# Then uncomment: stock_df = pd.read_csv('stock.csv')
stock_data = {
    'Supplier': [],
    'Product Code': [],
    'Item ID': [],
    'Description': [],
    'Category': []
}

# From Combined sheet (partial)
stock_data['Supplier'].extend(['WOL02', 'DAI01', 'CPL01', 'CPL01', 'CPL01', 'CPL01', 'CPL01', 'CPL01'])
stock_data['Product Code'].extend(['191227', 'EJHA04AV3', '626688', '626694', '153316', '153326', '726410', '726412'])
stock_data['Item ID'].extend(['1', '2', '3', '4', '1799', '1800', '1801', '1802'])
stock_data['Description'].extend([
    'ALPHA ETEC HYBRID ASHP 33KW', 'DAIKIN ALTHERMA HYBRID 4KW', 'GRANT AERONA 3 INSTALLATION PACK A HPIDR32PACKA',
    'GRANT AERONA 3 INSTALLATION PACK B HPIDR32PACKB', 'HIVE THERMOSTAT WITH HIVE HUB', 'HIVE THERMOSTAT WITHOUT HIVE HUB',
    'SPACE SAVER HEATER - SS5', 'SPACE SAVER HEATER - SS9'
])
stock_data['Category'].extend(['Air-Source Heat Pumps', 'Air-Source Heat Pumps', 'Air-Source Heat Pumps', 'Air-Source Heat Pumps', 'Thermostats', 'Thermostats', 'Radiators', 'Radiators'])

# From DAI sheet
stock_data['Supplier'].extend(['DAI01'] * 10)
stock_data['Product Code'].extend(['EJHA04AV3', 'AFVALVE1', 'UK.PPC150/R32', 'UK.PPC150SL/R32', 'EDLA08EV3', 'UK.FF600H150', 'UK.DT5', 'UK.DTFB', 'K.KHOSE750', 'UK.HOSE300EL'])
stock_data['Item ID'].extend(['00002', '00605', '00606', '00607', '00608', '00609', '00610', '00611', '00612', '01049'])
stock_data['Description'].extend([
    'DAIKIN ALTHERMA HYBRID 4KW', 'ANTI-FREEZE VALVE FOR GLYCOL FREE SYSTEM', '150L PRE-PLUMBED CYLINDER', '150L SLIMLINE PRE-PLUMBED CYLINDER',
    'MONOBLOC HEAT PUMP CLASS 8', 'FLEX FEET FOR MOUNTING OUTDOOR 150MM TALL - PAIR', 'DONDENSATE TRIP TRAY - 1400 X 400 X 50MM',
    'FLOOR BRAKCET FOR DRIP TRAY', 'FLEXIBLE HOSES - PAIR', 'R32 PRE PLUMBED SYLINDER 150 L 300MM FLEXI HOSE WITH ELBOW'
])
stock_data['Category'].extend(['Air-Source Heat Pumps'] * 10)

# From GENERIC sheet
stock_data['Supplier'].extend(['GENERIC'] * 10)  # Placeholder supplier
stock_data['Product Code'].extend(['01564', '01481', '01561', '01560', '01563', '01504', '01486', '01523', '01521', '01572'])
stock_data['Item ID'].extend(['01564', '01481', '01561', '01560', '01563', '01504', '01486', '01523', '01521', '01572'])
stock_data['Description'].extend([
    'BAGS & SACKS', 'BIN', 'BRICK / BUILDING MATERIALS', 'BUCKETS / TRAYS', 'CLEANING LIQUIDS / SEALANTS', 'HELMETS', 'TOOL BOX', 'VARIOUS TOOLS', 'WHEELBARROWS', 'OTHER CONSUMABLES - ELECTRICS'
])
stock_data['Category'].extend(['Consumables - Other'] * 9 + ['Consumables - Electrical'])

# Add from other sheets similarly (CEF, CPL, EDM, GRE, JAM, SWIP, SCR, TRA, TUP, PAS, PAM, UKSOL, WOL)
# Example from CEF
stock_data['Supplier'].extend(['CEF01'] * 10)
stock_data['Product Code'].extend(['2082-9976', '0004-4179', '0004-5661', '0005-9197', '0005-9302', '0006-0250', '0006-0313', '0006-0346', '2211-4477', '2467-2016'])
stock_data['Item ID'].extend(['00782', '00039', '00969', '00787', '00080', '00071', '00072', '00073', '01493', '01494'])
stock_data['Description'].extend([
    '5 WAY COMPACT LEVER CONNECTOR', '12.7MM SWA CABLE CLEAT', '100A SINGLE POLE CONNECTOR BLOCK', '6491X 4MM CORE GREEN / YELLOW',
    '6491X 10.0MM2 GREEN/YELLOW 100M', '3182Y 0.75M2 BLACK 50M', '3182Y 1M2 WHITE 50M', '3183Y 0.75MM2 BLACK 50M',
    '10M EXTENSION REEL', 'CAT 6 PASS THROUGH MODULAR DATA PLUG - PK 50'
])
stock_data['Category'].extend(['Consumables - Electrical'] * 10)

# ... Continue adding all visible rows from your query (e.g., CPL, WOL, etc.). For brevity, truncated here; copy full from your document.

stock_df = pd.DataFrame(stock_data).drop_duplicates()

# Simple DB setup
conn = sqlite3.connect(':memory:')  # Use file 'warehouse.db' for persistence
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS picks 
             (id INTEGER PRIMARY KEY, company TEXT, project TEXT, items TEXT, qty TEXT, timestamp TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS projects 
             (company TEXT, address TEXT)''')

# Sample projects (edit with yours)
projects_data = [
    ('Improveasy Services', '123 Green St, London'),
    ('Improveasy Services', '456 Eco Ave, Manchester'),
    # Add more
]
pd.DataFrame(projects_data, columns=['company', 'address']).to_sql('projects', conn, if_exists='replace', index=False)
conn.commit()

# App UI
st.title('Improveasy Warehouse Picklist App')

# Optional password for access: if st.text_input('Password', type='password') != 'improveasy123': st.stop()

mode = st.sidebar.radio('Mode', ['Installer Pick', 'Admin View'])

if mode == 'Installer Pick':
    company = st.selectbox('Select Your Company', ['Improveasy Services', 'Other Installer Co'])  # Add companies
    projects = pd.read_sql(f"SELECT address FROM projects WHERE company='{company}'", conn)['address'].tolist()
    project = st.selectbox('Select Project/Address', projects)
    
    st.subheader('Select Items')
    search = st.text_input('Search by Code, Description, or Category')
    filtered_df = stock_df[stock_df.apply(lambda row: search.lower() in ' '.join(row.astype(str)).lower(), axis=1)]
    
    if not filtered_df.empty:
        st.dataframe(filtered_df[['Product Code', 'Description', 'Category']])
    
    # Cart
    if 'cart' not in st.session_state:
        st.session_state.cart = {}
    
    item_code = st.text_input('Enter Item Code to Add')
    qty = st.number_input('Quantity', min_value=1, value=1)
    if st.button('Add to Cart') and item_code in stock_df['Product Code'].values:
        desc = stock_df[stock_df['Product Code'] == item_code]['Description'].values[0]
        st.session_state.cart[item_code] = {'desc': desc, 'qty': qty}
    
    if st.session_state.cart:
        st.subheader('Your Picklist')
        cart_df = pd.DataFrame.from_dict(st.session_state.cart, orient='index')
        st.dataframe(cart_df)
        
        if st.button('Submit Picklist'):
            items_str = ','.join(st.session_state.cart.keys())
            qty_str = ','.join([str(v['qty']) for v in st.session_state.cart.values()])
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            c.execute("INSERT INTO picks (company, project, items, qty, timestamp) VALUES (?, ?, ?, ?, ?)",
                      (company, project, items_str, qty_str, timestamp))
            conn.commit()
            st.success(f'Submitted! Confirmation: PICK-{c.lastrowid}')
            st.session_state.cart = {}

elif mode == 'Admin View':
    st.subheader('All Picklists')
    picks_df = pd.read_sql('SELECT * FROM picks', conn)
    st.dataframe(picks_df)
    
    # Export for SAGE
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        picks_df.to_excel(writer, index=False)
    st.download_button('Download as Excel for SAGE', output.getvalue(), 'picklists.xlsx')

conn.close()
